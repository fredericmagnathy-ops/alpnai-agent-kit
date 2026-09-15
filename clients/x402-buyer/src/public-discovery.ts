// Copied from the reviewed ALPNAI public declaration, 2026-09-15.
/** Reviewed public examples, never assembled from an order, receipt or buyer input.
 * Uses the @x402/extensions 2.25.0 base with public header prerequisites.
 * Validated with its official discovery validators; no real credentials belong here.
 * The server may use this declaration only when that paid resource is available.
 */
export function publicBuyerDiscovery(product:string){
 if(!['snapshot','changes','evidence'].includes(product))throw Error('invalid_discovery_declaration');
 const input=product==='changes'?{since:'2026-01-01'}:{};
 const properties=product==='changes'?{since:{type:'string',pattern:'^\\d{4}-\\d{2}-\\d{2}$'}}:{};
 const headers={Authorization:'Bearer <ALPNAI_AGENT_KEY>','X-AlpNAI-Mode':'live','X-AlpNAI-Mandate':'<OWNER_MANDATE_ID>','Idempotency-Key':'<PERSISTED_PURCHASE_ID>'};
 return {bazaar:{
  info:{input:{type:'http',method:'GET',queryParams:input,headers},output:{type:'json',example:{data:{schema_version:'1.0',entity:'OpenAI'}}}},
  schema:{$schema:'https://json-schema.org/draft/2020-12/schema',type:'object',properties:{
   input:{type:'object',properties:{type:{type:'string',const:'http'},method:{type:'string',enum:['GET','HEAD','DELETE']},queryParams:{type:'object',properties,additionalProperties:false},headers:{type:'object',description:'Public placeholders only. Activate an agent key at https://alpnai.com/start and prepare billing and an owner mandate at https://alpnai.com/account before purchase. A wallet signature alone is insufficient.',properties:{Authorization:{type:'string'},'X-AlpNAI-Mode':{const:'live'},'X-AlpNAI-Mandate':{type:'string'},'Idempotency-Key':{type:'string'}},required:Object.keys(headers),additionalProperties:false}},required:['type','method','headers'],additionalProperties:false},
   output:{type:'object',properties:{type:{type:'string'},example:{type:'object',properties:{data:{type:'object',properties:{schema_version:{type:'string'},entity:{type:'string'}},required:['schema_version','entity']}},required:['data']}},required:['type']}
  },required:['input']}
 }};
}
