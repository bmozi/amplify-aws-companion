import { defineStorage } from '@aws-amplify/backend';
export const storage = defineStorage({ name: 'labFiles', access: allow => ({ 'private/{entity_id}/*': [allow.entity('identity').to(['read', 'write', 'delete'])] }) });
