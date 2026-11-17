# Check your address-governance reasoning

1. **Why hold `10.20.4.0/24`?** The legacy VPC occupies it in the proposed connected domain. “Unmanaged” means it was not allocated from the pool; it does not mean unused.
2. **Why count `10.20.6.0/24`?** The exercise has a recorded claimant. IPAM's ignored state does not prove the network is gone. Resolve ownership and actual connectivity before reusing it.
3. **Does a clean `/24` paper result create an AWS VPC?** No. It asks for a later real allocation, current inventory, routes in both directions, permissions and a customer operation.
4. **When may the two scopes reuse `10.20.8.0/24`?** Only if they represent genuinely disconnected routing domains and the proposed future architecture keeps them apart. A label in a spreadsheet is not isolation evidence.
5. **Does the IPAM Free Tier supply this private IPv4 governance plan?** No. The cited AWS pricing table puts private IPv4 management in Advanced Tier. Calculate active IP hours and all dependent charges before any authorized live lab.

Change one assumption: the training domain is scheduled to connect to production next month. Reconsider the once-isolated overlap, the migration path and the rollback owner. A local `REVIEW_WITH_IPAM_AND_ROUTE_EVIDENCE` is an instruction to gather facts, not permission to connect networks.
