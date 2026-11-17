import { defineBackend } from '@aws-amplify/backend';
import { Tags } from 'aws-cdk-lib';
import { auth } from './auth/resource';
import { data } from './data/resource';
import { storage } from './storage/resource';
import { inspect } from './functions/inspect/resource';
const backend = defineBackend({ auth, data, storage, inspect });
for (const stack of [backend.auth.stack, backend.data.stack, backend.storage.stack]) {
  Tags.of(stack).add('Project', 'amplify-learning-lab');
  Tags.of(stack).add('Owner', 'REPLACE_WITH_REVIEWED_RESOURCE_OWNER');
}
backend.auth.resources.cfnResources.cfnIdentityPool.allowUnauthenticatedIdentities = false;
