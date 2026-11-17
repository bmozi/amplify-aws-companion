import { type ClientSchema, a, defineData } from '@aws-amplify/backend';
import { inspect } from '../functions/inspect/resource';
const schema = a.schema({
  Entry: a.model({ title: a.string().required(), notes: a.string(), explored: a.boolean() }).authorization(allow => [allow.owner()]),
  inspectEntry: a.query().arguments({ text: a.string().required() }).returns(a.string()).authorization(allow => [allow.authenticated()]).handler(a.handler.function(inspect)),
});
export type Schema = ClientSchema<typeof schema>;
export const data = defineData({ schema, authorizationModes: { defaultAuthorizationMode: 'userPool' } });
