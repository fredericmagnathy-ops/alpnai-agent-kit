# ALPNAI buyer client — standalone draft

An already authorized AI agent can use this TypeScript helper to buy ALPNAI's curated JSON products over REST, create an exact x402 authorization through an existing wallet adapter, and resume order checks after restart. The helper is deliberately restricted to the existing ALPNAI commercial contract. It is not a general wrapper that pays any HTTP 402.

**Status: offline draft.** No ALPNAI API request, real wallet signature, settlement, key access or deployment was performed to create or test it. Commercial availability must be checked at runtime; the helper returns `inactive` when the public catalog does not advertise live payments. This draft does not enable live commerce or qualify a buyer account.

## Files

- `src/client.ts`: purchase state machine, fixed origin, quote/receipt checks, durable single-step polling.
- `src/official-factory.ts`: official x402 2.25.0 integration with an injected `ClientEvmSigner` subset.
- `src/public-discovery.ts`: exact reviewed public Bazaar declaration, including static onboarding/header placeholders.
- `src/file-journal.ts`: atomic filesystem journal for one host, with exclusive locks and fsync.
- `test/client.test.ts`: focused offline tests using mock responses and synthetic signature bytes.

## Owner-supplied setup

The owner must already have an active ALPNAI agent key, an active commercial mandate tied to that agent and payer, the required billing qualification, a reviewed terms version and SHA-256, and an existing wallet capable of policy-controlled EIP-712 signing. Keep these capabilities within the owner's existing secure runtime. This helper never creates, loads, requests or receives wallet private keys.

Current ALPNAI agent credentials use the `alp_test_` prefix, including credentials whose owners separately add a commercial mandate. The prefix itself does not authorize real payment. The helper additionally requires `allowMainnet: true`, a mandate, owner policy and live catalog status. The server remains responsible for mandate balance, active authorization, billing and settlement.

Run `npm run build` first. For an integration file placed in this package directory, use the emitted paths below. The package also exports its root client, `./file-journal` and `./official-factory` for consumers installing it as a local dependency.

```ts
import {AlpNAIBuyer} from './dist/src/client.js';
import {FileJournal} from './dist/src/file-journal.js';
import {officialPaymentFactory} from './dist/src/official-factory.js';

// Each referenced value is supplied by the owner's existing authorized runtime.
// No secrets or wallet implementation are included in this draft.
const buyer = new AlpNAIBuyer({
  agentKey: owner.agentKey,
  mandateId: owner.mandateId,
  payer: existingWallet.address,
  allowMainnet: owner.explicitlyAllowsBaseMainnet === true,
  maxAtomic: {snapshot: '10000'}, // permit only Snapshot, maximum 0.01 USDC
  terms: {version: owner.termsVersion, sha256: owner.termsSha256},
  journal: new FileJournal(owner.privateDurableStateDirectory),
  createPayment: officialPaymentFactory(existingWallet),
});

// The owner supplies one stable identity for this intended purchase.
const request = {product: 'snapshot' as const, idempotencyKey: owner.purchaseId};
const outcome = await buyer.purchase(request);

// On pending, persist/schedule outcome.nextPollAt in the existing job system.
// After that time, even in a fresh process with the same journal and owner identity:
// const nextOutcome = await buyer.poll(request);
// Continue only read-only polling while pending. Never replace purchaseId to retry.
```

Each `poll` call performs **at most one status GET**, returns immediately if `nextPollAt` is still in the future, and uses a 10-second request timeout. There is no hidden infinite loop. The existing agent scheduler can impose its own total duration/attempt budget, retain the pending record and surface prolonged review to the owner. Server `Retry-After` values from 15 through 300 seconds are persisted; a value outside the reviewed contract fails closed.

The default native transport refuses redirects, omits cookies, sends authentication only to the pinned ALPNAI API, and caps JSON responses at 512 KB. An injected transport is a trusted test/runtime dependency and must honor the supplied AbortSignal and normal Fetch semantics.

## Payment and retry contract

1. Validate the owner's product permission and explicit Base mainnet opt-in. Fetch the public catalog before any new quote or payment submission. Require `mode: live`, `live_payments_enabled: true`, Base network, USDC currency, enabled commerce routes, and the exact available product entry. Catalog checks carry no agent credential.
2. Request the product with `Authorization`, `X-AlpNAI-Mode: live`, `X-AlpNAI-Mandate`, and the owner-supplied `Idempotency-Key`. `changes` normalizes its default date to `2026-01-01`; a different valid date is included in both URL and persisted identity.
3. A first 402 must have agreeing JSON and `PAYMENT-REQUIRED` protocol data and matching order ID. Before the payment factory can run, check the exact URL, `exact` scheme, Base chain 8453, native Base USDC contract, fixed public ALPNAI receiver, catalog amount, owner limit, commercial total, approved terms hash, quote expiry and 60-second payment timeout. If a Bazaar extension is present, compare its complete canonical value against the copied public declaration. Reject any modification, including real credentials in public placeholders or private metadata anywhere in the declaration.
4. Persist the immutable order and authorization phase. The official factory registers Base only and calls the existing wallet's `signTypedData`. It validates the domain and EIP-3009 amount, payer, receiver, nonce and expiry before delegating. A returned authorization must remain valid for more than two seconds, no longer than 60 seconds from the local clock, and must end by the quote expiry. Quotes must have more than 65 seconds left before starting a new signature and no more than five minutes left. An almost-expired quote needs owner review; no replacement is signed automatically.
5. Persist the exact encoded payment header in `ready`, then durably commit `submitted` **before** sending it. A crash before the `submitted` commit permits reuse of the same saved header while valid. A crash after that commit, timeout, malformed response, HTTP 402 or 5xx never causes a new payment submission. Only the original order status is read. An ambiguous status that still says `quoted` requires owner review.
6. HTTP 202 means payment is already under review. Persist its next poll time, discard the stored signature, and use only `GET /api/v1/orders/{original_order_id}`. Never follow an arbitrary response URL, refresh a nonce, or change idempotency key. An HTTP 200 is treated as settled only when the body and official `PAYMENT-RESPONSE` confirm the same original order, payer, network, amount, product and transaction.

The read-only `poll` path remains available after live commerce is disabled. This lets an already submitted purchase reach its existing result without authorizing another payment.

## Fixed reviewed limits

| Product | Atomic USDC ceiling | USDC |
| --- | ---: | ---: |
| Snapshot | 10000 | 0.01 |
| Change Set | 50000 | 0.05 |
| Evidence Pack | 250000 | 0.25 |

Owner limits may be lower; products omitted from `maxAtomic` cannot be bought. Server price increases above these reviewed ceilings fail closed.

The only service origin is `https://alpnai.com`. The only network is `eip155:8453`. The only token is native Base USDC at `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`. The pinned public receiving address is `0x092161689b3aaf6d5c00E6656EB7DB78027B95B2`, taken from the checked application source. Changing any of these requires explicit review and a new draft. There is no Base Sepolia or other-chain fallback.

## Durability and limitations

- Use the same journal and credentials for the lifetime of an intended purchase. The journal identity binds a SHA-256 fingerprint of the agent key, mandate, payer and owner purchase ID. The stored request URL binds the product/date. Reusing the identity for a different request is rejected. Do not rotate a credential/mandate or discard the journal to work around a pending purchase.
- The file journal is for a private, trusted, local filesystem, not a shared/cloud filesystem or multiple hosts. It stores order metadata and briefly a spend-capable signed payment header; protect the directory. It stores no raw bearer key and no private key. A crash can leave `.lock` or `.tmp` files; the owner must inspect the original order and journal before resolving them. Locks are never expired automatically. A multi-host deployment needs a transactional database journal implementing the same exclusive, durable contract.
- Reaching `authorizing` then failing/crashing is deliberately stopped for owner review; the helper does not assume another signature is harmless. A `needs_attention` result is not evidence of a failed on-chain transfer, and must not trigger another purchase identity.
- This version accepts ordinary 65-byte EIP-3009 signatures only. Smart-wallet/EIP-6492 signatures, Permit2, token approvals, gas-sponsoring extensions, MPC-specific adaptations and arbitrary wallet prompts are not implemented. The signer adapter itself remains a trusted capability and must enforce the owner's overall spending policy.
- The exact reviewed Bazaar declaration is appended to the payment after the signing factory returns, preserving discovery data without activating extension hooks. Its public header placeholders are never replaced with real agent keys, mandate IDs, purchase IDs, customer data or receipts. Only complete canonical equality is accepted; alternate date-filter URLs accept no discovery declaration. This enables a facilitator to receive the public declaration with the payment, but actual indexing depends on the facilitator and a real accepted transaction. MCP transport is outside this draft.
- Catalog availability is a preflight indicator, not proof of buyer eligibility or a successful settlement. Server-side account, mandate and billing checks can still refuse the request before payment. The client trusts the pinned HTTPS service's receipt and does not independently reconcile the blockchain.
- The clock must be reasonably accurate. Local filesystem storage must be durable. Missing records or inconsistent response shapes fail closed and need reconciliation; there is no order lookup by idempotency key in the inspected public status API.
- Nothing here enrolls a buyer, funds a wallet, creates a mandate, enables commerce, changes the Site, publishes the kit or schedules a production worker.

## Build and offline verification

```sh
npm install --ignore-scripts
npm test
```

Packages are pinned to the application's inspected official SDK versions. The local verification used the already-installed dependency tree through a symlink; it did not run dependency installation. `npm test` compiles the TypeScript and runs only mock transports. The tests cover inactive/live gates, owner caps, quote corruption, redirects, one submission followed by 202 polling, restarts, timeout/402 ambiguity, idempotency conflict, safe reuse before submission, file persistence, complete public discovery echo and privacy rejection, and official SDK interoperability with synthetic signature bytes.

Primary SDK reference: [x402 buyer quickstart](https://docs.x402.org/getting-started/quickstart-for-buyers). The exact runtime APIs and EIP-3009 payload shape were also checked in the installed official `@x402/core@2.25.0` and `@x402/evm@2.25.0` packages. Server behavior was checked in `lib/payments/commerce.ts`, `ledger.ts`, `wallet-purchase.ts`, `x402.ts`, `lib/agent-catalog.ts` and `app/api/v1/orders/[id]/route.ts` in the supplied application checkout. The draft is intended for review before production integration.
