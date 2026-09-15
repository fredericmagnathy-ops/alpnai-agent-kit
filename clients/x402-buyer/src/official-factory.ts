import {x402Client} from '@x402/core/client';
import {ExactEvmScheme} from '@x402/evm/exact/client';
import type {ClientEvmSigner} from '@x402/evm';
import type {PaymentFactory} from './client.js';
import {NETWORK, USDC, checkAuthorization} from './client.js';

/** Accept an existing policy-controlled wallet adapter; no key loading or wallet setup. */
export function officialPaymentFactory(signer: Pick<ClientEvmSigner, 'address' | 'signTypedData'>): PaymentFactory {
  return async ({paymentRequired, quoteExpiresAt, payer}) => {
    if (signer.address.toLowerCase() !== payer.toLowerCase()) throw Error('payer_signer_mismatch');
    const amount = paymentRequired.accepts[0].amount;
    const guarded: ClientEvmSigner = {
      address: signer.address,
      async signTypedData(input) {
        if (input.primaryType !== 'TransferWithAuthorization' || input.domain.name !== 'USD Coin' ||
            input.domain.version !== '2' || input.domain.chainId !== 8453 ||
            String(input.domain.verifyingContract).toLowerCase() !== USDC.toLowerCase()) throw Error('unexpected_signing_domain');
        checkAuthorization(input.message, amount, payer, quoteExpiresAt, Date.now());
        return signer.signTypedData(input);
      },
    };
    // Register only Base exact; no wildcard, transport retries, extensions or permits.
    const client = new x402Client().register(NETWORK, new ExactEvmScheme(guarded));
    return client.createPaymentPayload(paymentRequired);
  };
}
