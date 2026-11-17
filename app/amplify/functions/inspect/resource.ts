import { defineFunction } from '@aws-amplify/backend';
export const inspect = defineFunction({ name: 'inspect-entry', entry: './handler.ts', timeoutSeconds: 10, memoryMB: 128, resourceGroupName: 'data' });
