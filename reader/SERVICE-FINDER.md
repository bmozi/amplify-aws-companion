# Find an AWS service through its decision

Use this companion index when you recognize a product name and need the book's explanation or comparison. Numbers below are reading-order chapters. They differ from the older unit numbers in filenames. These are starting points, not claims of complete service coverage or deployment verification. The [topic finder](BOOK-LOCATORS.md#book-9b24361462ef46cc) starts from a concept instead.

| Service or family | Decision to investigate | Start in the book |
| --- | --- | --- |
| IAM, STS, IAM Identity Center | Which actor has which authority? | [3, identity](BOOK-LOCATORS.md#book-47726780fac09ca7); [28, accounts](BOOK-LOCATORS.md#book-71a7c1be66a5700e) |
| Cognito | What establishes an application identity? | [6, first app](BOOK-LOCATORS.md#book-e8d9fb108293da29) |
| Amplify Hosting, Gen 2 and Blocks | Which part serves the page or changes the backend? | [6, first app](BOOK-LOCATORS.md#book-e8d9fb108293da29); [8, environments](BOOK-LOCATORS.md#book-0c50e8451acb85fa) |
| AppSync | Where does the application's data request cross a boundary? | [6, first app](BOOK-LOCATORS.md#book-e8d9fb108293da29) |
| EC2, Lambda and Fargate | Which execution model fits this work? | [5, compute](BOOK-LOCATORS.md#book-1b1379691a2f6239) |
| Lambda Web Functions | Does the application need an HTTP-native server contract? | [5, web comparison](BOOK-LOCATORS.md#book-095112084d6625c3) |
| Lambda durable functions and Step Functions | Which orchestration model fits the workflow? | [23, approvals](BOOK-LOCATORS.md#book-842e431cbcce6c95); [24, events](BOOK-LOCATORS.md#book-f0f0044d800d44b9) |
| SQS and SNS | Do workers share one job or need independent deliveries? | [19, durable work](BOOK-LOCATORS.md#book-0b7eb9d1bab09ff9); [22, tenant fairness](BOOK-LOCATORS.md#book-422c5f26d4302648) |
| EventBridge | Which event should route to which responsibility? | [14, observation](BOOK-LOCATORS.md#book-f72a70eb301cb115); [24, events](BOOK-LOCATORS.md#book-f0f0044d800d44b9) |
| DynamoDB | Which keys, access patterns and writes preserve the rule? | [12, database choice](BOOK-LOCATORS.md#book-0fb36d2b3a5c21aa); [20, reservations](BOOK-LOCATORS.md#book-ffe5a37f32aa3433) |
| RDS and Aurora | Which relational behavior and operating model fit? | [12, database choice](BOOK-LOCATORS.md#book-0fb36d2b3a5c21aa); [13, read paths](BOOK-LOCATORS.md#book-8d7fd952f0661828) |
| Aurora DSQL | Does distributed SQL meet the actual compatibility and transaction contract? | [12, DSQL comparison](BOOK-LOCATORS.md#book-d4883fa6da5a9fd0) |
| ElastiCache and MemoryDB | Is this copy disposable or authoritative? | [12, database choice](BOOK-LOCATORS.md#book-0fb36d2b3a5c21aa); [13, freshness](BOOK-LOCATORS.md#book-8d7fd952f0661828) |
| S3, S3 Files, EBS, EFS and FSx | Which object, file or block interface does the workload need? | [11, storage](BOOK-LOCATORS.md#book-316ad1ab1452bb2f) |
| S3 Tables | Who maintains the Iceberg table and its history? | [24, managed tables](BOOK-LOCATORS.md#book-0efe6881e5c2505f) |
| S3 Vectors | Which retrieval query and access contract must the store support? | [31, retrieval-store comparison](BOOK-LOCATORS.md#book-bb4f83194bb15e73) |
| Route 53 and CloudFront | Is the decision about name resolution, cached content or customer state? | [4, network paths](BOOK-LOCATORS.md#book-6948135871204c55); [17, recovery](BOOK-LOCATORS.md#book-20703bba15f79b2d) |
| Load balancers and Global Accelerator | Which protocol, entry point and health signal fit? | [4, network paths](BOOK-LOCATORS.md#book-6948135871204c55) |
| VPC, PrivateLink, VPN and Direct Connect | Which request and return paths must exist? | [4, foundations](BOOK-LOCATORS.md#book-6948135871204c55); [29, hybrid paths](BOOK-LOCATORS.md#book-0b54b52a3c811230) |
| ECS, EKS, ECR and ECS Express Mode | Who owns the image, platform, identity and replacement? | [16, delivery](BOOK-LOCATORS.md#book-02b8b1e13a935d6d); [26, containers](BOOK-LOCATORS.md#book-8444a5a7a3bbe0d5) |
| CloudWatch | What customer signal warrants which operating action? | [14, observation](BOOK-LOCATORS.md#book-f72a70eb301cb115); [15, incident](BOOK-LOCATORS.md#book-48004aaa3a73ab7d) |
| CloudTrail, GuardDuty, Inspector and Macie | Which evidence source answers the investigation question? | [10, findings](BOOK-LOCATORS.md#book-367ab937e61db26d) |
| KMS and Secrets Manager | Who can decrypt or retrieve the intended material? | [3, identity](BOOK-LOCATORS.md#book-47726780fac09ca7); [9, data protection](BOOK-LOCATORS.md#book-4f6cf1453aa8c153) |
| Organizations and Control Tower | Which account and governance boundary carries responsibility? | [28, accounts](BOOK-LOCATORS.md#book-71a7c1be66a5700e) |
| Bedrock and SageMaker AI | Is the need generation, authorized retrieval, inference or action? | [6, AI route](BOOK-LOCATORS.md#book-e8d9fb108293da29); [31, retrieval and inference](BOOK-LOCATORS.md#book-c7716c08655f741e) |
| Athena, Glue and analytics reporting | Which facts, table state and reader support the decision? | [24, events and tables](BOOK-LOCATORS.md#book-f0f0044d800d44b9); [25, dashboards](BOOK-LOCATORS.md#book-9a2045b273a89d57) |
| Migration and transfer services | Are you moving a dataset, preserving an interface or switching business authority? | [27, migration](BOOK-LOCATORS.md#book-9fb6047993bd4d40) |

After locating a service, state the requirement it satisfies, the nearest credible alternative and the condition that would reverse the choice. Use current primary documentation for exact features, prices and supported configurations. Use [cumulative practice](../curriculum/RETRIEVAL-PRACTICE.md) when you need to test the reasoning without a product-name hint.
