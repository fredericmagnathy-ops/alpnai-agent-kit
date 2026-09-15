import {createHash} from 'node:crypto';
import {decodePaymentRequiredHeader, decodePaymentResponseHeader, encodePaymentSignatureHeader, decodePaymentSignatureHeader} from '@x402/core/http';
import type {PaymentRequired, PaymentPayload} from '@x402/core/types';
import {publicBuyerDiscovery} from './public-discovery.js';

export const ORIGIN = 'https://alpnai.com';
export const NETWORK = 'eip155:8453';
export const USDC = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913';
export const RECEIVER = '0x092161689b3aaf6d5c00E6656EB7DB78027B95B2';
export const PRICE_CEILINGS = {snapshot: '10000', changes: '50000', evidence: '250000'} as const;
export type Product = keyof typeof PRICE_CEILINGS;
export type Purchase = {product: Product; since?: string; idempotencyKey: string};
export type Quote = PaymentRequired & {alpnai_quote: {
  order_id: string; expires_at: string; snapshot_hash: string;
  terms: {version: string; sha256: string};
  pricing: {currency: string; network: string; asset: string; product: string; total_atomic: number};
}};
export type PaymentFactory = (input: {
  paymentRequired: PaymentRequired; quoteExpiresAt: number; payer: string;
}) => Promise<PaymentPayload>;
export type Outcome = {
  state: 'inactive' | 'pending' | 'settled' | 'needs_attention';
  orderId?: string; nextPollAt?: number; reason?: string; result?: unknown;
};
export type RecordEntry = {
  version: 1; identity: string; url: string; product: Product; amount: string;
  phase: 'quoted' | 'authorizing' | 'ready' | 'submitted' | 'pending' | 'settled' | 'blocked';
  orderId: string; quote: Quote; header?: string; nextPollAt?: number; result?: unknown;
};
/** Must serialize this identity across processes and durably commit before resolving save. */
export interface Journal {
  exclusive<T>(identity: string, operation: () => Promise<T>): Promise<T>;
  load(identity: string): Promise<RecordEntry | undefined>;
  save(identity: string, entry: RecordEntry): Promise<void>;
}
export type BuyerOptions = {
  agentKey: string; mandateId: string; payer: string;
  /** An explicit owner policy. Omission or false prevents every paid request. */
  allowMainnet?: boolean;
  /** Omitted products cannot be bought. Atomic USDC integers; 1 USDC = 1,000,000. */
  maxAtomic: Partial<Record<Product, string>>;
  /** Bind owner-reviewed commercial terms; a changed document fails closed. */
  terms: {version: string; sha256: string};
  journal: Journal; createPayment: PaymentFactory;
  fetch?: typeof fetch; now?: () => number;
};
type Obj = Record<string, any>;
const object = (v: unknown): v is Obj => !!v && typeof v === 'object' && !Array.isArray(v);
const equal = (a: unknown, b: unknown): boolean => canonical(a) === canonical(b);
function canonical(v: unknown): string {
  if (Array.isArray(v)) return '[' + v.map(canonical).join(',') + ']';
  if (object(v)) return '{' + Object.keys(v).sort().map(k => JSON.stringify(k) + ':' + canonical(v[k])).join(',') + '}';
  return JSON.stringify(v);
}
const address = (v: unknown): v is string => typeof v === 'string' && /^0x[\da-f]{40}$/i.test(v) && !/^0x0{40}$/i.test(v);
const sameAddress = (a: unknown, b: string) => address(a) && a.toLowerCase() === b.toLowerCase();
const atomic = (v: unknown): v is string => typeof v === 'string' && /^[1-9]\d{0,11}$/.test(v);
const orderId = (v: unknown): v is string => typeof v === 'string' && /^[-a-zA-Z0-9]{8,80}$/.test(v);
function fail(code: string): never {throw new Error(code);}
const digest = (v: string) => createHash('sha256').update(v).digest('hex');

/** EIP-3009 only. Used both before the injected signer and after factory return. */
export function checkAuthorization(a: Obj, amount: string, payer: string, expiry: number, now: number) {
  const t = Math.floor(now / 1000), before = Number(a.validBefore), after = Number(a.validAfter);
  if (!sameAddress(a.from, payer) || !sameAddress(a.to, RECEIVER) || String(a.value) !== amount ||
      !/^\d{1,12}$/.test(String(a.validAfter)) || !/^\d{1,12}$/.test(String(a.validBefore)) ||
      !Number.isSafeInteger(after) || after > t || !Number.isSafeInteger(before) ||
      before <= t + 2 || before > t + 60 || before * 1000 > expiry || after >= before ||
      typeof a.nonce !== 'string' || !/^0x[\da-f]{64}$/i.test(a.nonce)) fail('authorization_outside_policy');
}

function requestUrl(p: Purchase) {
  if (!Object.hasOwn(PRICE_CEILINGS, p.product) || !/^[A-Za-z0-9_-]{8,100}$/.test(p.idempotencyKey)) fail('invalid_purchase_identity');
  if (p.since !== undefined && p.product !== 'changes') fail('since_only_for_changes');
  const since = p.product === 'changes' ? p.since ?? '2026-01-01' : undefined;
  if (since && (!/^\d{4}-\d{2}-\d{2}$/.test(since) || !Number.isFinite(Date.parse(since)) || new Date(since).toISOString().slice(0, 10) !== since)) fail('invalid_since');
  return ORIGIN + '/api/v1/' + p.product + (since ? '?since=' + since : '');
}

/** Validate all payment-bearing facts before the payment factory is called. */
export function validateQuote(q: unknown, url: string, product: Product, amount: string, terms: BuyerOptions['terms'], now: number, minRemainingMs = 65_000): Quote {
  if (!object(q) || q.x402Version !== 2 || !object(q.resource) || q.resource.url !== url ||
      !Array.isArray(q.accepts) || q.accepts.length !== 1 || !object(q.accepts[0])) fail('invalid_quote');
  const required = q as Obj, r = required.accepts[0], aq = required.alpnai_quote;
  if (r.scheme !== 'exact' || r.network !== NETWORK || !sameAddress(r.asset, USDC) || !sameAddress(r.payTo, RECEIVER) ||
      r.amount !== amount || r.maxTimeoutSeconds !== 60 || !object(r.extra) || r.extra.name !== 'USD Coin' || r.extra.version !== '2' ||
      Object.keys(r.extra).some(k => !['name', 'version', 'assetTransferMethod'].includes(k)) ||
      (r.extra.assetTransferMethod !== undefined && r.extra.assetTransferMethod !== 'eip3009')) fail('payment_requirements_outside_policy');
  const expires = object(aq) ? Date.parse(aq.expires_at) : NaN;
  if (!object(aq) || !orderId(aq.order_id) || !Number.isFinite(expires) || expires <= now + minRemainingMs || expires > now + 300_000 ||
      !/^[\da-f]{64}$/i.test(aq.snapshot_hash) || !object(aq.terms) || aq.terms.version !== terms.version || aq.terms.sha256 !== terms.sha256 || !object(aq.pricing) ||
      aq.pricing.currency !== 'USDC' || aq.pricing.network !== NETWORK || !sameAddress(aq.pricing.asset, USDC) ||
      aq.pricing.product !== product || !Number.isSafeInteger(aq.pricing.total_atomic) || String(aq.pricing.total_atomic) !== amount) fail('invalid_commercial_quote');
  // Only the complete static public declaration may be echoed for discovery.
  // Never replace its placeholders with real buyer credentials, order or receipt data.
  if (required.extensions != null && !equal(required.extensions, {})) {
    const canonicalUrl = ORIGIN + '/api/v1/' + product + (product === 'changes' ? '?since=2026-01-01' : '');
    if (url !== canonicalUrl || new TextEncoder().encode(JSON.stringify(required.extensions)).length > 8192 ||
        !equal(required.extensions, publicBuyerDiscovery(product))) fail('invalid_public_discovery');
  }
  return JSON.parse(JSON.stringify(q)) as Quote;
}

function payloadHeader(payload: PaymentPayload, quote: Quote, payer: string, now: number) {
  if (!object(payload) || payload.x402Version !== 2 || !equal(payload.accepted, quote.accepts[0]) ||
      !equal(payload.resource, {url: quote.resource.url}) || !object(payload.payload) ||
      !equal(payload.extensions ?? {}, quote.extensions ?? {})) fail('unexpected_payment_payload');
  const p = payload.payload as Obj;
  if (Object.keys(p).sort().join(',') !== 'authorization,signature' || !object(p.authorization) ||
      typeof p.signature !== 'string' || !/^0x[\da-f]{130}$/i.test(p.signature)) fail('unsupported_payment_signature');
  checkAuthorization(p.authorization, quote.accepts[0].amount, payer, Date.parse(quote.alpnai_quote.expires_at), now);
  const header = encodePaymentSignatureHeader(payload);
  if (header.length > 32_768) fail('payment_payload_too_large');
  return header;
}

export class AlpNAIBuyer {
  private readonly o: BuyerOptions;
  private readonly now: () => number;
  constructor(options: BuyerOptions) {
    this.o = {...options, maxAtomic: {...options.maxAtomic}, terms: {...options.terms}};
    this.now = options.now ?? Date.now;
    if (!/^alp_test_[A-Za-z0-9_-]{8,200}$/.test(options.agentKey) || !/^[-A-Za-z0-9]{8,80}$/.test(options.mandateId) ||
        !address(options.payer) || !options.terms.version || !/^[\da-f]{64}$/i.test(options.terms.sha256)) fail('owner_configuration_required');
    for (const [p, cap] of Object.entries(options.maxAtomic)) {
      if (!Object.hasOwn(PRICE_CEILINGS, p) || !atomic(cap) || BigInt(cap) > BigInt(PRICE_CEILINGS[p as Product])) fail('invalid_owner_price_ceiling');
    }
  }
  private identity(p: Purchase) {
    return digest(canonical([digest(this.o.agentKey), this.o.mandateId, this.o.payer.toLowerCase(), p.idempotencyKey]));
  }
  private async read(url: string, p?: Purchase, signature?: string) {
    if (new URL(url).origin !== ORIGIN || !/^https:\/\/alpnai\.com\/api\/v1\/(catalog|snapshot|changes|evidence|orders\/[-A-Za-z0-9]+)(\?since=\d{4}-\d{2}-\d{2})?$/.test(url)) fail('untrusted_url');
    const signal = AbortSignal.timeout(10_000);
    const headers: Record<string, string> = {Accept: 'application/json'};
    if (url !== ORIGIN + '/api/v1/catalog') headers.Authorization = 'Bearer ' + this.o.agentKey;
    if (p) Object.assign(headers, {'X-AlpNAI-Mode': 'live', 'X-AlpNAI-Mandate': this.o.mandateId, 'Idempotency-Key': p.idempotencyKey});
    if (signature) headers['PAYMENT-SIGNATURE'] = signature;
    const res = await (this.o.fetch ?? fetch)(url, {method: 'GET', headers, redirect: 'manual', credentials: 'omit', cache: 'no-store', signal});
    if (res.redirected || (res.url && res.url !== url) || (res.status >= 300 && res.status < 400)) fail('redirect_refused');
    if (res.headers.get('content-type')?.split(';')[0].trim() !== 'application/json' || !res.body) fail('invalid_json_response');
    const reader = res.body.getReader(), chunks: Uint8Array[] = []; let size = 0;
    try {
      while (true) {
        const part = await reader.read();
        if (part.done) break;
        size += part.value.byteLength;
        if (signal.aborted || size > 512_000) {await reader.cancel(); fail('response_limit_exceeded');}
        chunks.push(part.value);
      }
    } finally {reader.releaseLock();}
    const bytes = new Uint8Array(size); let offset = 0;
    for (const c of chunks) {bytes.set(c, offset); offset += c.length;}
    let body: unknown;
    try {body = JSON.parse(new TextDecoder().decode(bytes));} catch {fail('invalid_json_response');}
    if (!object(body)) fail('invalid_json_response');
    return {res, body: body as Obj};
  }
  private async catalog(p: Purchase) {
    const {res, body: c} = await this.read(ORIGIN + '/api/v1/catalog');
    if (res.status !== 200 || c.live_payments_enabled !== true || c.mode !== 'live' || c.network !== NETWORK || c.currency !== 'USDC' ||
        c.commerce?.routes_enabled !== true || c.commerce?.mainnet_enabled !== true || c.commerce?.status !== 'restricted_live') return undefined;
    const matches = Array.isArray(c.products) ? c.products.filter((v: Obj) => v?.id === p.product) : [];
    const product = matches[0], cap = this.o.maxAtomic[p.product];
    if (matches.length !== 1 || product.method !== 'GET' || product.path !== '/api/v1/' + p.product ||
        product.availability !== 'qualified_account_required' || !Number.isSafeInteger(product.amount) || product.amount <= 0 ||
        !cap || BigInt(product.amount) > BigInt(cap) || BigInt(product.amount) > BigInt(PRICE_CEILINGS[p.product])) fail('catalog_outside_owner_policy');
    return String(product.amount);
  }
  private async saved(p: Purchase) {
    const identity = this.identity(p), record = await this.o.journal.load(identity);
    if (record && (record.version !== 1 || record.identity !== identity || record.url !== requestUrl(p) || record.product !== p.product || !orderId(record.orderId))) fail('journal_identity_conflict');
    return record;
  }
  private async save(r: RecordEntry) {await this.o.journal.save(r.identity, r);}
  private pending(r: RecordEntry, reason?: string): Outcome {return {state: 'pending', orderId: r.orderId, nextPollAt: r.nextPollAt, reason};}

  /** New purchase, or resume the SAME identity. No implicit generation of keys/mandates/IDs. */
  async purchase(p: Purchase): Promise<Outcome> {
    const url = requestUrl(p), identity = this.identity(p);
    return this.o.journal.exclusive(identity, async () => {
      let r = await this.saved(p);
      if (r?.phase === 'settled') return {state: 'settled', orderId: r.orderId, result: r.result};
      if (r && ['submitted', 'pending'].includes(r.phase)) return this.pollRecord(r);
      if (r && ['authorizing', 'blocked'].includes(r.phase)) return {state: 'needs_attention', orderId: r.orderId, reason: 'resume_requires_owner_review'};
      if (this.o.allowMainnet !== true) return {state: 'inactive', reason: 'explicit_mainnet_opt_in_required'};
      const amount = await this.catalog(p);
      if (!amount) return {state: 'inactive', reason: 'commercial_activation_pending'};
      if (r?.amount && r.amount !== amount) fail('catalog_price_changed');
      if (!r) {
        const {res, body} = await this.read(url, p);
        if (res.status !== 402) return {state: 'needs_attention', reason: 'expected_unpaid_quote_http_' + res.status};
        const q = validateQuote(body, url, p.product, amount, this.o.terms, this.now());
        const requiredHeader = res.headers.get('PAYMENT-REQUIRED');
        if (!requiredHeader || requiredHeader.length > 32_768) fail('invalid_payment_required_header');
        const decoded = decodePaymentRequiredHeader(requiredHeader);
        const {alpnai_quote: _, ...protocolQuote} = q;
        if (!equal(decoded, protocolQuote) || res.headers.get('X-AlpNAI-Order') !== q.alpnai_quote.order_id) fail('quote_transport_mismatch');
        r = {version: 1, identity, url, product: p.product, amount, phase: 'quoted', orderId: q.alpnai_quote.order_id, quote: q};
        await this.save(r);
      }
      if (r.phase === 'quoted') {
        validateQuote(r.quote, url, p.product, amount, this.o.terms, this.now());
        r.phase = 'authorizing'; await this.save(r);
        // Limit the factory to payment-bearing requirements and the exact URL.
        const paymentRequired: PaymentRequired = {x402Version: 2, resource: {url}, accepts: JSON.parse(JSON.stringify(r.quote.accepts))};
        const payload = await this.o.createPayment({paymentRequired, quoteExpiresAt: Date.parse(r.quote.alpnai_quote.expires_at), payer: this.o.payer});
        if (payload.extensions && !equal(payload.extensions, {})) fail('factory_extensions_forbidden');
        // Discovery is attached only after signing, so no extension can trigger wallet
        // actions. The complete value was compared to the reviewed public constant.
        const completed = {...payload, ...(r.quote.extensions && !equal(r.quote.extensions, {})
          ? {extensions: JSON.parse(JSON.stringify(r.quote.extensions))} : {})};
        r.header = payloadHeader(completed, r.quote, this.o.payer, this.now());
        r.phase = 'ready'; await this.save(r);
      }
      // Only READY can send: a crash before this commit reuses its stored header;
      // after this commit every outcome (including timeout/402/5xx) is polling only.
      if (r.phase !== 'ready' || !r.header) fail('invalid_journal_phase');
      validateQuote(r.quote, url, p.product, amount, this.o.terms, this.now(), 2_000);
      payloadHeader(decodePaymentSignatureHeader(r.header) as PaymentPayload, r.quote, this.o.payer, this.now());
      r.phase = 'submitted'; r.nextPollAt = this.now() + 15_000; await this.save(r);
      try {return await this.handle(r, await this.read(url, p, r.header));}
      catch {return this.pending(r, 'submission_outcome_unknown_poll_original_order');}
    });
  }

  /** A read-only step suitable for a scheduler; works even if commerce is later disabled. */
  async poll(p: Purchase): Promise<Outcome> {
    requestUrl(p);
    return this.o.journal.exclusive(this.identity(p), async () => {
      const r = await this.saved(p);
      if (!r) return {state: 'needs_attention', reason: 'original_order_not_in_journal'};
      if (r.phase === 'settled') return {state: 'settled', orderId: r.orderId, result: r.result};
      if (!['submitted', 'pending'].includes(r.phase)) return {state: 'needs_attention', orderId: r.orderId, reason: 'order_not_submitted'};
      return this.pollRecord(r);
    });
  }
  private async pollRecord(r: RecordEntry): Promise<Outcome> {
    if (r.nextPollAt && this.now() < r.nextPollAt) return this.pending(r, 'wait_until_next_poll');
    // Persist spacing before issuing the GET, including on malformed/failed reads.
    r.nextPollAt = this.now() + 15_000; await this.save(r);
    try {return await this.handle(r, await this.read(ORIGIN + '/api/v1/orders/' + r.orderId));}
    catch {return this.pending(r, 'status_unavailable_retry_read_only');}
  }
  private async handle(r: RecordEntry, {res, body}: {res: Response; body: Obj}): Promise<Outcome> {
    if (body.order_id !== r.orderId) fail('response_order_mismatch');
    if (res.status === 200 && body.settled === true) {
      const header = res.headers.get('PAYMENT-RESPONSE');
      if (!header || header.length > 16_384) fail('confirmed_receipt_missing');
      const receipt = decodePaymentResponseHeader(header);
      if (receipt.success !== true || receipt.network !== NETWORK || receipt.amount !== r.amount ||
          !sameAddress(receipt.payer, this.o.payer) || !/^0x[\da-f]{64}$/i.test(receipt.transaction) ||
          body.receipt?.transaction !== receipt.transaction || body.receipt?.product !== r.product ||
          body.receipt?.amount !== r.amount || body.receipt?.success !== true || body.mode !== 'live' || !Object.hasOwn(body, 'data')) fail('receipt_outside_policy');
      r.phase = 'settled'; r.result = body; delete r.header; delete r.nextPollAt; await this.save(r);
      return {state: 'settled', orderId: r.orderId, result: body};
    }
    if (res.status === 202 && body.settled === false && ['reserved', 'settling', 'pending', 'unknown'].includes(body.status) &&
        body.follow_up === '/api/v1/orders/' + r.orderId) {
      const retry = res.headers.get('Retry-After') ?? '15';
      if (!/^\d{1,3}$/.test(retry) || Number(retry) < 15 || Number(retry) > 300) fail('invalid_retry_after');
      r.phase = 'pending'; r.nextPollAt = this.now() + Number(retry) * 1000; delete r.header; await this.save(r);
      return this.pending(r);
    }
    if ([429, 500, 502, 503, 504].includes(res.status)) return this.pending(r, 'server_unavailable_poll_original_order');
    // A quoted/cancelled/expired/rejected order never triggers another signature.
    r.phase = 'blocked'; delete r.header; await this.save(r);
    return {state: 'needs_attention', orderId: r.orderId, reason: 'order_requires_review_http_' + res.status};
  }
}
