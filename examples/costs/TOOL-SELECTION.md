# Choose the cost evidence before choosing the tool

This fictional exercise accompanies [the cost lesson](../../reader/BOOK-LOCATORS.md#book-b69ea6a931797633). It needs no AWS account, billing export, paid API call or deployment. Write an unaided answer before reading [assessor notes](TOOL-SELECTION-ASSESSOR.md).

For each packet, state the question, a suitable tool or evidence source, the filter/period assumptions and what the result cannot prove. A service name without those boundaries is insufficient.

## Packet 1: tomorrow's experiment

Maya has a proposed architecture and an expected request count. Nothing has been deployed. A teammate opens last month's Cost Explorer graph and says it proves the proposed design will fit tomorrow's allowance. Another teammate has an estimate, but it includes only compute; the diagram also contains storage, logs and a network component.

What should be estimated, what evidence supports the inputs, and which claim is currently unsupported? Do not invent prices or assume promotional credits apply to every component.

## Packet 2: the project filter is quiet

After a bounded fictional run, the Cost Explorer view filtered to `Project=repair-lab` shows no charge. The filter period includes the run, but its refresh time is earlier than the final activity. The resource inventory contains both tagged and untagged resources. The operator has not confirmed cost-allocation tag activation.

Can Maya conclude that the experiment was free? Specify the broader comparison and configuration checks. Keep investigation separate from enabling a feature or changing tags. Do not assume a newly activated tag immediately repairs all historical reporting.

## Packet 3: the alert did not arrive

A saved budget exists. No recipient-delivery test is recorded. No alert has arrived, and a worker still accepts new jobs. A teammate says this proves the worker is below the intended spending ceiling.

Which observations would answer notification health, reported usage and actual workload status? What action belongs in the prewritten run-stop procedure instead of waiting for a billing signal? Do not propose deleting shared resources indiscriminately.

## Packet 4: the export is more detailed

The team needs a repeatable monthly investigation with selected line-item fields and a documented allocation method. It proposes CUR 2.0 through Data Exports. The export query excludes one service; a dashboard query also excludes rows with missing project tags. A teammate claims the resulting total covers the whole account because it came from detailed billing data.

What must be reconciled before accepting that claim? Name the access, retention and operating-cost decisions for the export destination and query path. You are reviewing a design; do not create resources.

## Transfer: a different audience

A contractor needs to investigate one application's costs, while the underlying billing dataset includes unrelated business information. Explain why sharing the entire export is not automatically justified. Define the intended data scope, approved reader and a verification check. Then explain why narrowing access must not be disguised as a whole-account total.

After recording your answers, ask Codex to identify missing time boundaries, excluded records and evidence that would distinguish competing explanations. Keep supplied facts, proposed checks and AI suggestions separate. No learner mastery or live notification delivery is inferred from completing the written packet.
