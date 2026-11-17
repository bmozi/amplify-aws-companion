# Assessor notes: compute availability classes

There is no fixed “production equals multi-region” answer. Assess whether the learner connected the business impact and schedule to measurable service outcomes, then selected the least complex strategy that meets the approved requirement.

## Arithmetic

For a continuous 30-day month, there are 43,200 minutes. At 99.9% availability, 0.1% may be unavailable: 43,200 × 0.001 = 43.2 minutes. At 99.99%, 0.01% may be unavailable: 43,200 × 0.0001 = 4.32 minutes. This simple allowance assumes a continuous window and no exclusions. It is not an AWS service-level commitment, and it does not establish actual achieved availability.

## Strong answer characteristics

- The booking site is treated as a continuous customer service with an explicitly defined success journey. The learner notices that timeouts, wrong booking state and unavailable dependencies may be failures even if the compute instance reports healthy.
- To tolerate one-AZ loss, the design places eligible components across multiple AZs and demonstrates enough compute and downstream capacity remains after the loss. Merely naming two AZs, setting desired capacity to two or enabling a load balancer does not prove this.
- The learner considers the database and other dependencies, data consistency, authentication, DNS/networking, deployment and operator access. The RPO requirement for confirmed bookings is not automatically met by redundant compute.
- A full-Region event is treated separately. The four-hour RTO demands a documented regional recovery path, required configuration/data, credentials and tested human/automation steps; multi-AZ alone does not cross that failure boundary.
- The training environment's allowed rebuild window and class schedule can justify stop/rebuild or simpler capacity outside the window, while versioned instructor materials and access to credentials remain necessary. A live showcase changes the impact and measurement requirements. Environment isolation still matters even if availability requirements are modest.
- The batch worker is judged by durable accepted work, backlog, throughput and completion deadline. Individual compute interruptions can be acceptable if retries and remaining time/capacity keep all due reports on schedule. The learner does not confuse worker uptime with batch success.
- Cost discussion includes duplicate/spare capacity, load balancing, replicated/standby data, cross-zone or regional data movement, logging/monitoring, backup, restore tests and operator effort. Unknown costs remain unknown until estimated.
- AI critique is checked against the actual failure scenario and official documentation; it does not turn an assumed SLO into a customer-approved promise.

## Common errors

| Error | Why it is weak | Better question |
| --- | --- | --- |
| “Everything called production needs 99.99%.” | A label does not describe the customer's schedule, loss or consequence. | What interruptions can this business accept, and when? |
| “Nonproduction can go down whenever.” | A class, release test or regulatory exercise may have a tight window. | What event depends on this environment, and how quickly can it be rebuilt? |
| “Two AZs guarantee high availability.” | The application, data path, available capacity and recovery process may still fail together. | Which full customer action succeeds after a zone loss, at peak load? |
| “Multi-region is always safer.” | It adds cost and data-consistency/failover complexity, and may not be required by the approved failure boundary. | Which regional event must be tolerated, and what is the tested recovery objective? |
| “An SLA proves our SLO.” | A provider SLA has its own service scope and exclusions; the application includes additional components and customer behavior. | How will the end-to-end workload measure success? |
| “A healthy worker means the batch is available.” | The queue may still miss its deadline or contain unrecoverable work. | Is accepted work complete by the deadline and reconciled correctly? |

No AWS resource, recovery process or learner response was inspected as part of this worksheet. A production decision still needs owner-approved objectives, current service-feature review, cost estimate and a failure exercise covering the actual customer path.
