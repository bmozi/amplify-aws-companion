# Assessor: workflow path is one boundary, not the whole release

This answer key applies to the fictional conditions in [the lesson](WORKFLOW-PATH-UPGRADE.md). The comparison assumes exact `aud`, immutable `sub` and `job_workflow_ref` conditions on a proposed publisher role. It is not an IAM simulator or an account readback.

| Case | Provisional trust result | What a strong answer retains |
| --- | --- | --- |
| 1. Copied name, direct job | The name-only source candidate could match; the new path condition should not, because the direct job lacks the expected called-workflow claim. | Check actual token issuance and installed trust. A flag in the original workflow does not constrain a separate file. |
| 2. Correct called file, build changes bytes | Claim comparison may match. | IAM trust does not inspect built content. The called job binds and hashes its own ZIP, but a dependency that changes content before hashing can still pass those checks. Review dependencies and compare approved content separately from commit and ZIP metadata. |
| 3. Different caller, same called file | Claim comparison may match if the caller also has the exact trusted subject. | `job_workflow_ref` identifies the called reusable file, not which same-branch caller chose it. The called build makes its own ZIP, so a different caller cannot hand it an arbitrary artifact; source writers and caller inputs still need review, and the called jobs must enforce their gates. |
| 4. Feature-branch caller | The exact immutable `main` subject fails even if the reusable file path points at `main`. | Keep both conditions; a called-path check alone would not preserve the caller branch rule. |
| 5. Direct job after path trust change | Missing `job_workflow_ref` fails the path comparison. | Moving IAM trust before checking the new job's actual claim can lock out the intended publisher. |
| 6. Flag changed after session issuance | The new setting can stop future gated jobs, but the existing session may remain usable until expiry or another effective control intervenes. | Check session duration and actual AWS permissions; the variable is not a role revocation mechanism. |
| 7. Reused names, different IDs | The exact immutable subject fails. | Name and path spelling alone are weaker than stable repository identity. Recheck GitHub's subject format after a transfer. |

The stronger design is **conditional**: the actual reusable job must emit the expected claim; the exact IAM trust must be installed and read back; the caller and called job must enforce publication controls; the role policy must remain scoped; and a bounded live probe must show intended allow/deny outcomes. None has happened merely because the paper cases are solved. Keep the book's current cloud-free, cost and credit limits in place.
