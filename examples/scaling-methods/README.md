# Choose a scaling method: add workers, resize, or hibernate

This is an original design case for SAA-C03 Domain 4 task 4.2, skill 02. It is not an AWS exam item. First choose a change that can meet the workload promise; then compare whole operating costs.

## Three requests from Maya's team

1. **Photo conversion queue:** 300 independent jobs arrive during a 15-minute event. Jobs can be retried by stable ID and write completed results to shared durable storage. During the busiest measured test, one worker completes 10 jobs/minute; the database can save 80 results/minute. Customers need all accepted images ready within 30 minutes. Choose a starting capacity method. State how you would calculate enough workers and preserve spare capacity if one fails. These rates are fictional; they do not include launch time, job variation or retry overhead.
2. **License-bound engineering solver:** one vendor-supported process uses 26 GiB RAM, processes one model that cannot be split, and runs for hours. The license and software certify only a subset of EC2 families. Recommend what to measure before a vertical resize or replacement. Explain the maintenance window and why adding ordinary queue workers does not divide this process.
3. **Analyst's workstation:** one person uses a long-lived Linux workstation for a few hours, leaves it idle overnight, and wants applications to resume where they were. The application state fits in RAM and its data is on encrypted EBS; no instance-store data is required. Assess hibernation against a clean stop and a fresh start. Verify current AMI and instance-type support and the actual root-volume requirement before recommending it.

```text
Many independent jobs:     queue -> worker 1, worker 2, ... -> durable outputs
One indivisible job:        one compatible process -> larger compatible instance
One resumable workstation: hibernate -> encrypted EBS stores RAM -> start and resume
```

The paths meet different promises. Hibernation is not an Auto Scaling policy. Do not attach hibernation as a cost-saving trick to an ordinary Auto Scaling worker: an instance in an Auto Scaling group cannot be hibernated as an ordinary instance, and group health management can replace it. Hibernation also does not retain instance-store data. AWS continues to charge for the attached EBS volumes when the instance is stopped; other resources such as an associated Elastic IP may also retain separate charges.

## Complete the decision record

For each request, write the workload shape, customer deadline, scaling direction, state location, current failure boundary, restart/replace behavior, dependency limit, and monthly cost inputs. Compare on-demand usage, any minimum capacity, EBS storage (including memory space for hibernation), IP/network costs, license fees, logs, scheduled idle time and the labor to patch and test. Use the current regional calculator for any real estimate; no prices are included here.

Answer these changed constraints:

- The photo worker's database save rate is only 35 results/minute. Compare two, three and four workers at the stated per-worker rate. At which point does the database cap useful completion? What customer measure must be checked before adding more?
- The solver vendor certifies a larger instance but its data is on instance store. What must happen to the state before changing instance type or stopping the machine?
- The analyst's application takes only 20 seconds to reopen and stores all work on EBS. Is preserving RAM worth the extra root-volume capacity and resume checks?
- The workstation must be always available to the user, including during an Availability Zone disruption. Does hibernation alone meet that service promise? What design or recovery evidence is missing?
- The instance type appears on a family list, but `DescribeInstanceTypes` in the selected Region reports hibernation unsupported. Which source controls the decision?

## Run the local checklist

The hibernation checker validates a *fictional candidate description* against selected documented rules. It trusts two explicit input fields saying that the selected AMI and instance type were checked against current AWS information. It checks an encrypted EBS root volume and one supported root-volume type. Its simple capacity comparison adds RAM, the supplied OS/application space and a supplied work-space reserve; this is a learner's planning check, not AWS's exact reserved-space calculation or a substitute for checking actual free space. It does not call AWS or prove the support statements.

```bash
python3 examples/scaling-methods/hibernation_check.py examples/scaling-methods/fixtures/eligible-linux.json
python3 -m unittest discover -s examples/scaling-methods -p 'test_*.py'
```

The eligible fixture should pass the local checklist with a note to verify actual regional support and test resume. The negative fixtures show why root encryption, RAM bounds, Auto Scaling membership and root-volume space can reverse the apparent choice. The tests also check invalid inputs and the supported root-volume type boundary. Change one field at a time, run the checker, and explain the failure in ordinary language.

Sources: [EC2 hibernation behavior](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Hibernate.html), [hibernation prerequisites](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/hibernating-prerequisites.html), [hibernation limitations](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-hibernate-overview.html), [Auto Scaling launch-template updates](https://docs.aws.amazon.com/autoscaling/ec2/userguide/update-auto-scaling-group.html).

See the [assessor notes](ASSESSOR.md) after completing the case.
