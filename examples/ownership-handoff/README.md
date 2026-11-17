# Who owns the table after the handoff?

Maya's app uses a data-bearing table created by an Amplify Gen 2 backend. Her team wants Terraform to manage more infrastructure. Read [Unit 09's handoff lesson](../../reader/BOOK-LOCATORS.md#book-2c590dc24f10596f) and draw the owner, physical table and customer path at each stage. Answer each case before opening the [assessor notes](ASSESSOR.md). All names are fictional; this packet has no AWS commands or credentials and is **design-only**.

After predicting the cases, run `python3 examples/ownership-handoff/lab.py` from the repository root. The script evaluates eight **synthetic evidence summaries**. It distinguishes readiness for a proposed import from completed customer acceptance. Run `python3 -m unittest discover -s examples/ownership-handoff -p 'test_*.py'` for six focused tests. A string such as `released` is a supplied assumption, not evidence extracted from CloudFormation; the script does not parse AWS change sets, Terraform plans, stack membership or customer requests. Use it to rehearse what must be verified, never as permission to run a real transfer.

For each case, record: **current owner → proposed owner; known physical ID; missing evidence; next read-only check; stop condition; recovery/cost implication**. Explain whether you would keep CloudFormation ownership, migrate to a new table or attempt an in-place handoff.

## 1. A maintenance request, not an ownership requirement

Maya wants another service to read the table. The Amplify backend still deploys reliably and can grant the required access. A teammate proposes exporting the table to Terraform because the new service is described in Terraform. Which design would you choose, and what boundary remains between permission to use a table and permission to manage its lifecycle?

## 2. The early import

A developer adds a Terraform resource and `import` block for the table while the CloudFormation stack still lists it. The plan says it can import with no immediate update. The developer calls this a completed migration. What does the plan establish? What could the next backend or Terraform deployment do?

## 3. The missing Retain policy

The team removes the table from generated backend definitions. The proposed CloudFormation change set shows deletion, and no effective `Retain` policy has been demonstrated on the resource. The team has a recent Terraform state backup. Is the change safe? Identify the evidence needed before any stack update.

## 4. The wrong table with the right name

The old stack no longer lists the table. Terraform is configured for the practice Region but the operator believes the table is in production. A similarly named table exists in each Region. The import plan proposes no updates. Which identities and records must match before continuing, and why is a no-op plan insufficient?

## 5. A preserved table, broken application

CloudFormation retained the physical table, and Terraform now tracks its ID. The next Amplify backend build changes generated API and authorization outputs. The app loads its homepage, but Maya cannot see an order she placed before the handoff. What should be checked before declaring success or reverting? How could a rollback itself cause a second owner or data loss?

## 6. A safer new-target route

An in-place release cannot be expressed durably through the supported Amplify backend workflow. The team proposes a new Terraform-managed table and an application cutover. List the extra evidence this route needs: data completeness, writes during the move, permissions, cutover/rollback point, temporary dual cost and retained old data. Which part of the old design remains authoritative until cutover?

## AI review without delegation of authority

Give Codex a sanitized ownership diagram, fictional change-set actions and a redacted Terraform plan. Ask: “Find assumptions that could delete, replace, misidentify or double-manage the table. Separate observed facts from design choices and unknowns. Give the smallest next read-only check for each unknown.” Verify the claims against current AWS, Amplify and Terraform documentation and actual private account evidence. Never paste customer rows, credentials, raw state or unredacted plans into the exercise.
