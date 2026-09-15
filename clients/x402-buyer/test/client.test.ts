import assert from 'node:assert/strict';
import {test} from 'node:test';
import {mkdtemp, readFile, readdir, rm} from 'node:fs/promises';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {encodePaymentRequiredHeader, encodePaymentResponseHeader, encodePaymentSignatureHeader, decodePaymentSignatureHeader} from '@x402/core/http';
import type {PaymentRequired, PaymentPayload} from '@x402/core/types';
import {AlpNAIBuyer, ORIGIN, NETWORK, USDC, RECEIVER, type BuyerOptions, type RecordEntry, type Journal, type Quote, type Purchase} from '../src/client.js';
import {FileJournal} from '../src/file-journal.js';
import {officialPaymentFactory} from '../src/official-factory.js';
import {publicBuyerDiscovery} from '../src/public-discovery.js';
import {x402ResourceServer} from '@x402/core/server';
import {ExactEvmScheme as ExactEvmServerScheme} from '@x402/evm/exact/server';

const PAYER = '0x1111111111111111111111111111111111111111';
const TERMS = {version: 'fixture-v1', sha256: 'a'.repeat(64)};
const PURCHASE: Purchase = {product: 'snapshot', idempotencyKey: 'owner-request-0001'};
const ORDER = 'order-00000001';
const signature = ('0x' + '1'.repeat(130)) as `0x${string}`; // synthetic bytes; never a valid live signature

class MemoryJournal implements Journal {
  data = new Map<string, RecordEntry>(); locked = false;
  async exclusive<T>(_id: string, op: () => Promise<T>) {
    if (this.locked) throw Error('locked');
    this.locked = true; try {return await op();} finally {this.locked = false;}
  }
  async load(id: string) {return structuredClone(this.data.get(id));}
  async save(id: string, record: RecordEntry) {this.data.set(id, structuredClone(record));}
  record() {return [...this.data.values()][0];}
}
function catalog(live = true) {
  return {live_payments_enabled: live, mode: live ? 'live' : 'sandbox', network: NETWORK, currency: 'USDC',
    commerce: {routes_enabled: live, mainnet_enabled: live, status: live ? 'restricted_live' : 'commercial_activation_pending'},
    products: [{id: 'snapshot', method: 'GET', path: '/api/v1/snapshot', amount: 10000, availability: 'qualified_account_required'}]};
}
function quote(now: number): Quote {
  return {x402Version: 2, resource: {url: ORIGIN + '/api/v1/snapshot'}, extensions: publicBuyerDiscovery('snapshot'), accepts: [{scheme: 'exact', network: NETWORK,
    asset: USDC, amount: '10000', payTo: RECEIVER, maxTimeoutSeconds: 60, extra: {name: 'USD Coin', version: '2'}}],
    alpnai_quote: {order_id: ORDER, expires_at: new Date(now + 300_000).toISOString(), snapshot_hash: 'b'.repeat(64),
      terms: {...TERMS, archive_url: ORIGIN + '/legal/versions/fixture-v1.json'} as typeof TERMS,
      pricing: {currency: 'USDC', network: NETWORK, asset: USDC, product: 'snapshot', total_atomic: 10000}}};
}
function response(body: unknown, status = 200, headers: Record<string, string> = {}) {
  return Response.json(body, {status, headers});
}
function challenge(q: Quote) {
  const {alpnai_quote: _, ...protocol} = q;
  return response(q, 402, {'PAYMENT-REQUIRED': encodePaymentRequiredHeader(protocol), 'X-AlpNAI-Order': q.alpnai_quote.order_id});
}
function pending(order = ORDER, follow = '/api/v1/orders/' + order) {
  return response({order_id: order, settled: false, status: 'pending', follow_up: follow}, 202, {'Retry-After': '15'});
}
function settled() {
  const receipt = {success: true, network: NETWORK, payer: PAYER, amount: '10000', transaction: '0x' + 'c'.repeat(64)} as const;
  // Shape from ledger.orderResponse; values are synthetic and contain no owner data.
  return response({order_id: ORDER, settled: true, mode: 'live', replayed: true,
    receipt: {...receipt, product: 'snapshot', amount_usdc: 0.01, date: '2026-09-15T00:00:00.000Z',
      order_created_at: '2026-09-15T00:00:00.000Z', payment_recorded_at: '2026-09-15T00:00:00.000Z',
      seller: {name: 'Fixture Seller'}, document_type: 'payment_receipt',
      quotation: {order_id: ORDER, document_type: 'quotation', terms: TERMS,
        pricing: {currency: 'USDC', network: NETWORK, asset: USDC, product: 'snapshot', total_atomic: 10000}, snapshot_hash: 'b'.repeat(64)}},
    data: {fixture: true}}, 200,
    {'PAYMENT-RESPONSE': encodePaymentResponseHeader(receipt)});
}
function payload(required: PaymentRequired, now: number): PaymentPayload {
  return {x402Version: 2, resource: required.resource, accepted: required.accepts[0], payload: {
    authorization: {from: PAYER, to: RECEIVER, value: '10000', validAfter: '0', validBefore: String(Math.floor(now / 1000) + 60), nonce: '0x' + 'd'.repeat(64)}, signature,
  }};
}
type Step = (url: string, init: RequestInit) => Response | Promise<Response>;
function harness(steps: Step[], overrides: Partial<BuyerOptions> = {}) {
  let now = 1_800_000_000_000, signatures = 0;
  const journal = new MemoryJournal(); const calls: Array<{url: string; init: RequestInit}> = [];
  const options: BuyerOptions = {agentKey: 'alp_test_fixture00000001', mandateId: 'owner-mandate-0001', payer: PAYER,
    allowMainnet: true, maxAtomic: {snapshot: '10000'}, terms: TERMS, journal, now: () => now,
    createPayment: async ({paymentRequired}) => {assert.equal(paymentRequired.extensions, undefined); signatures++; return payload(paymentRequired, now);},
    fetch: (async (input: string | URL | Request, init: RequestInit = {}) => {
      const url = String(input); calls.push({url, init});
      assert.equal(init.redirect, 'manual'); assert.equal(init.credentials, 'omit');
      const next = steps.shift(); assert.ok(next, 'Unexpected network request: ' + url); return next(url, init);
    }) as typeof fetch,
    ...overrides};
  return {buyer: new AlpNAIBuyer(options), options, journal, calls, now: () => now,
    advance: (ms = 15_000) => {now += ms;}, signatures: () => signatures, remaining: () => steps.length};
}
const catalogStep: Step = (_u, init) => {assert.equal(new Headers(init.headers).has('Authorization'), false); return response(catalog());};

test('inactive catalog stops before product request, signature and journal creation', async () => {
  const h = harness([() => response(catalog(false))]);
  assert.equal((await h.buyer.purchase(PURCHASE)).state, 'inactive');
  assert.equal(h.calls.length, 1); assert.equal(h.signatures(), 0); assert.equal(h.journal.data.size, 0);
});
test('mainnet is explicitly opt in', async () => {
  const h = harness([], {allowMainnet: undefined});
  assert.equal((await h.buyer.purchase(PURCHASE)).reason, 'explicit_mainnet_opt_in_required');
  assert.equal(h.calls.length, 0); assert.equal(h.signatures(), 0);
});
test('catalog price cannot exceed owner cap, or an omitted product permission', async () => {
  for (const caps of [{snapshot: '9999'}, {}]) {
    const h = harness([catalogStep], {maxAtomic: caps});
    await assert.rejects(h.buyer.purchase(PURCHASE), /catalog_outside_owner_policy/); assert.equal(h.signatures(), 0);
  }
});
test('reject wrong chain/token/receiver/amount/expiry/terms/URL before factory', async () => {
  const mutations: Array<(q: Quote) => void> = [
    q => {q.accepts[0].network = 'eip155:1';}, q => {q.accepts[0].asset = PAYER;},
    q => {q.accepts[0].payTo = PAYER;}, q => {q.accepts[0].amount = '10001';},
    q => {q.alpnai_quote.expires_at = new Date(1_800_000_000_000 + 60_000).toISOString();},
    q => {q.alpnai_quote.expires_at = new Date(1_800_000_000_000 + 301_000).toISOString();},
    q => {q.alpnai_quote.terms.sha256 = 'c'.repeat(64);},
    q => {q.resource.url = 'https://evil.example/paid';},
    q => {q.accepts[0].extra = {name: 'USD Coin', version: '2', assetTransferMethod: 'permit2'};},
  ];
  for (const change of mutations) {
    const h = harness([catalogStep, () => {const q = quote(h.now()); change(q); return challenge(q);}]);
    await assert.rejects(h.buyer.purchase(PURCHASE)); assert.equal(h.signatures(), 0); assert.equal(h.calls.length, 2);
  }
});
test('header/body challenge disagreement fails before payment', async () => {
  const h = harness([catalogStep, () => {const res = challenge(quote(h.now())); res.headers.set('X-AlpNAI-Order', 'other-order-01'); return res;}]);
  await assert.rejects(h.buyer.purchase(PURCHASE), /quote_transport_mismatch/); assert.equal(h.signatures(), 0);
});
test('reject credentials, customer/order data and altered schema anywhere in discovery before signing', async () => {
  const mutations: Array<(extension: any) => void> = [
    e => {e.bazaar.info.input.headers.Authorization = 'Bearer alp_test_private_customer_key';},
    e => {e.bazaar.info.input.headers['X-AlpNAI-Mandate'] = 'private-owner-mandate';},
    e => {e.bazaar.info.output.example.data.invoice = {customer: 'Private Company', order_id: ORDER};},
    e => {e.bazaar.schema.properties.input.properties.headers.description += ' Private company address';},
    e => {e['eip2612GasSponsoring'] = {};},
  ];
  for (const change of mutations) {
    const h = harness([catalogStep, () => {const q = quote(h.now()); change(q.extensions); return challenge(q);}]);
    await assert.rejects(h.buyer.purchase(PURCHASE), /invalid_public_discovery/);
    assert.equal(h.signatures(), 0); assert.equal(h.calls.length, 2);
  }
});
test('canonical public declaration comparison accepts object key reordering and echoes the complete value', async () => {
  function reverseKeys(value: any): any {
    if (Array.isArray(value)) return value.map(reverseKeys);
    if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).reverse().map(k => [k, reverseKeys(value[k])]));
    return value;
  }
  const h = harness([catalogStep, () => {const q = quote(h.now()); q.extensions = reverseKeys(q.extensions); return challenge(q);}, (_u, init) => {
    const header = new Headers(init.headers).get('PAYMENT-SIGNATURE')!;
    assert.deepEqual(decodePaymentSignatureHeader(header).extensions, publicBuyerDiscovery('snapshot'));
    return pending();
  }]);
  assert.equal((await h.buyer.purchase(PURCHASE)).state, 'pending'); assert.equal(h.signatures(), 1);
});
test('402 creates one payment; 202 polls without payment, survives new client, and confirms receipt', async () => {
  const h = harness([catalogStep, () => challenge(quote(h.now())), (u, init) => {
    assert.equal(u, ORIGIN + '/api/v1/snapshot'); const headers = new Headers(init.headers);
    assert.ok(headers.get('PAYMENT-SIGNATURE')); assert.equal(headers.get('Idempotency-Key'), PURCHASE.idempotencyKey);
    const signed = decodePaymentSignatureHeader(headers.get('PAYMENT-SIGNATURE')!);
    assert.deepEqual(signed.extensions, publicBuyerDiscovery('snapshot'));
    assert.ok(!JSON.stringify(signed.extensions).includes(h.options.agentKey));
    assert.equal(headers.get('X-AlpNAI-Mandate'), 'owner-mandate-0001'); assert.equal(headers.get('X-AlpNAI-Mode'), 'live');
    assert.equal(h.journal.record().phase, 'submitted'); return pending();
  }, (u, init) => {assert.equal(u, ORIGIN + '/api/v1/orders/' + ORDER); assert.equal(new Headers(init.headers).has('PAYMENT-SIGNATURE'), false); return settled();}]);
  assert.equal((await h.buyer.purchase(PURCHASE)).state, 'pending'); assert.equal(h.signatures(), 1);
  assert.equal(h.journal.record().header, undefined);
  const resumed = new AlpNAIBuyer({...h.options, allowMainnet: false});
  assert.equal((await resumed.poll(PURCHASE)).reason, 'wait_until_next_poll'); assert.equal(h.calls.length, 3);
  h.advance(); assert.equal((await resumed.poll(PURCHASE)).state, 'settled');
  assert.equal((await resumed.purchase(PURCHASE)).state, 'settled'); assert.equal(h.calls.length, 4); assert.equal(h.signatures(), 1);
});
test('ambiguous submission timeout resumes ONLY order status, never second settlement', async () => {
  const h = harness([catalogStep, () => challenge(quote(h.now())), () => {throw Error('timeout');}, () => pending(), () => settled()]);
  assert.equal((await h.buyer.purchase(PURCHASE)).reason, 'submission_outcome_unknown_poll_original_order');
  h.advance(); assert.equal((await new AlpNAIBuyer(h.options).purchase(PURCHASE)).state, 'pending');
  h.advance(); assert.equal((await h.buyer.poll(PURCHASE)).state, 'settled');
  assert.equal(h.signatures(), 1); assert.equal(h.calls.filter(c => new Headers(c.init.headers).has('PAYMENT-SIGNATURE')).length, 1);
});
test('HTTP 402 after submission never generates another payload', async () => {
  const h = harness([catalogStep, () => challenge(quote(h.now())), () => challenge(quote(h.now())), () => pending()]);
  assert.equal((await h.buyer.purchase(PURCHASE)).state, 'pending');
  h.advance(); assert.equal((await h.buyer.purchase(PURCHASE)).state, 'pending');
  assert.equal(h.signatures(), 1); assert.equal(h.calls[3].url, ORIGIN + '/api/v1/orders/' + ORDER);
});
test('malicious follow_up never forwards bearer key or payment to another origin', async () => {
  const h = harness([catalogStep, () => challenge(quote(h.now())), () => pending(ORDER, 'https://evil.example/order'), () => settled()]);
  assert.equal((await h.buyer.purchase(PURCHASE)).state, 'needs_attention');
  h.advance(); assert.equal((await h.buyer.purchase(PURCHASE)).state, 'needs_attention');
  assert.equal(h.calls.length, 3); assert.ok(h.calls.every(c => c.url.startsWith(ORIGIN + '/')));
});
test('redirect is rejected before any signature', async () => {
  const h = harness([() => new Response(null, {status: 302, headers: {Location: 'https://evil.example'}})]);
  await assert.rejects(h.buyer.purchase(PURCHASE), /redirect_refused/); assert.equal(h.signatures(), 0);
});
test('same idempotency identity cannot change product/date', async () => {
  const h = harness([catalogStep, () => challenge(quote(h.now())), () => pending()]);
  await h.buyer.purchase(PURCHASE);
  await assert.rejects(h.buyer.purchase({...PURCHASE, product: 'changes'}), /journal_identity_conflict/);
  assert.equal(h.signatures(), 1);
});
test('quote after ambiguous submission requires owner review and cannot re-sign', async () => {
  const h = harness([catalogStep, () => challenge(quote(h.now())), () => {throw Error('timeout');},
    () => response({order_id: ORDER, status: 'quoted', settled: false, payment_required: false})]);
  await h.buyer.purchase(PURCHASE); h.advance();
  assert.equal((await h.buyer.poll(PURCHASE)).state, 'needs_attention');
  assert.equal((await h.buyer.purchase(PURCHASE)).state, 'needs_attention'); assert.equal(h.signatures(), 1);
});
test('READY survives a failed pre-submission journal commit and reuses exact stored header', async () => {
  let failCommit = true, expectedHeader: string | undefined;
  const h = harness([catalogStep, () => challenge(quote(h.now())), catalogStep, (_u, init) => {
    assert.equal(new Headers(init.headers).get('PAYMENT-SIGNATURE'), expectedHeader); return pending();
  }]);
  const originalSave = h.journal.save.bind(h.journal);
  h.journal.save = async (id, r) => {
    if (r.phase === 'submitted' && failCommit) {failCommit = false; throw Error('mock disk failure');}
    return originalSave(id, r);
  };
  await assert.rejects(h.buyer.purchase(PURCHASE), /mock disk failure/);
  assert.equal(h.journal.record().phase, 'ready'); expectedHeader = h.journal.record().header;
  assert.equal((await new AlpNAIBuyer(h.options).purchase(PURCHASE)).state, 'pending'); assert.equal(h.signatures(), 1);
});
test('file journal persists across instances without storing the bearer agent key', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'alpnai-offline-test-'));
  try {
    const journal = new FileJournal(dir);
    const h = harness([catalogStep, () => challenge(quote(h.now())), () => pending(), () => settled()], {journal});
    await h.buyer.purchase(PURCHASE);
    const files = await readdir(dir); assert.equal(files.length, 1);
    const stored = await readFile(join(dir, files[0]), 'utf8'); assert.equal(stored.includes(h.options.agentKey), false);
    h.advance();
    assert.equal((await new AlpNAIBuyer({...h.options, journal: new FileJournal(dir)}).poll(PURCHASE)).state, 'settled');
    assert.equal(h.signatures(), 1);
  } finally {await rm(dir, {recursive: true, force: true});}
});
test('official SDK integrates with injected mock signer; signs only exact Base USDC domain', async () => {
  const now = Date.now(), q = quote(now); let count = 0;
  const factory = officialPaymentFactory({address: PAYER, signTypedData: async data => {
    count++; assert.equal(data.primaryType, 'TransferWithAuthorization'); assert.equal(data.domain.chainId, 8453);
    assert.equal(String(data.domain.verifyingContract).toLowerCase(), USDC.toLowerCase()); return signature;
  }});
  const required: PaymentRequired = {x402Version: 2, resource: {url: q.resource.url}, accepts: q.accepts};
  const result = await factory({paymentRequired: required, quoteExpiresAt: now + 300_000, payer: PAYER});
  assert.equal(count, 1); assert.equal(result.accepted.amount, '10000'); assert.ok(encodePaymentSignatureHeader(result));
  await assert.rejects(factory({paymentRequired: required, quoteExpiresAt: now + 10_000, payer: PAYER}), /authorization_outside_policy/);
  assert.equal(count, 1);
});

test('real SDK server quote recipe, full resource metadata and ledger-shaped receipt work offline', async () => {
  let facilitatorPaymentCalls = 0;
  const server = new x402ResourceServer({
    getSupported: async () => ({kinds: [{x402Version: 2, scheme: 'exact', network: NETWORK}], extensions: ['bazaar'], signers: {}}),
    verify: async () => {facilitatorPaymentCalls++; throw Error('forbidden');},
    settle: async () => {facilitatorPaymentCalls++; throw Error('forbidden');},
  }).register(NETWORK, new ExactEvmServerScheme());
  await server.initialize();
  // Same public quote construction as the checked lib/payments/x402.ts adapter.
  const [requirements] = await server.buildPaymentRequirements({scheme: 'exact', network: NETWORK, payTo: RECEIVER,
    maxTimeoutSeconds: 60, price: {amount: '10000', asset: USDC, extra: {name: 'USD Coin', version: '2'}}});
  const required = await server.createPaymentRequiredResponse([requirements], {
    url: ORIGIN + '/api/v1/snapshot', mimeType: 'application/json',
    description: 'Curated OpenAI IPO facts with dates and public primary-source references.',
    serviceName: 'ALPNAI', tags: ['openai', 'ipo', 'structured-data'],
  }, undefined, publicBuyerDiscovery('snapshot'));
  assert.equal(required.resource.description, 'Curated OpenAI IPO facts with dates and public primary-source references.');
  const h = harness([catalogStep, () => challenge({...required, alpnai_quote: quote(h.now()).alpnai_quote}), (_url, init) => {
    const paid = decodePaymentSignatureHeader(new Headers(init.headers).get('PAYMENT-SIGNATURE')!);
    assert.deepEqual(paid.accepted, requirements);
    assert.deepEqual(paid.extensions, required.extensions);
    return settled();
  }]);
  assert.equal((await h.buyer.purchase(PURCHASE)).state, 'settled');
  assert.equal(h.signatures(), 1); assert.equal(facilitatorPaymentCalls, 0);
});
