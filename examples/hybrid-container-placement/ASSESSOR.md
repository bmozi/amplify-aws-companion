# Check the hybrid-control-plane decision

1. **Where is the conductor?** ECS Anywhere and EKS Hybrid Nodes use a regional control plane. EKS Anywhere uses a customer-managed on-site control plane. An EKS local cluster on Outposts places the EKS control plane on the Outpost. The location of a worker alone does not answer this.
2. **What does `REVIEW_WITH_DISCONNECTION_DRILL` prove?** Only that the fictional required inputs are marked local. It does not prove Kubernetes scheduling, task restart, identity correctness, record durability, ingress, site resilience or a customer result.
3. **What is the first false inference?** “It runs on our floor, so it works offline.” A remote control plane, image registry, identity provider or database can break the promise.
4. **Which rejected option can become useful?** ECS Anywhere or EKS Hybrid Nodes may fit a workload that tolerates management disruption and keeps its business path safe, once tested. They fail this worksheet's stronger promise of new scheduled work during WAN loss without evidence.
5. **What cost can remain during a quiet month?** On-site machines, power, support/subscriptions and managed external instances can continue to cost money. Use current terms and the entire system estimate, not a single container rate.

Transfer question: the WAN returns after 15 minutes, but two copies of the same safety event were accepted locally. What durable event identity, reconciliation owner and customer-visible correction rule are needed before calling recovery complete?
