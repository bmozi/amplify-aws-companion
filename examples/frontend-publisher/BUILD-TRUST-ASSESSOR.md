# Assessor notes for the publication ZIP

1. **Approved page:** the ZIP matches the build digest and commit/run marker, and its page matches the independent fixture. This is local byte evidence only.
2. **After-hash change:** the ZIP digest differs from the build output value, so `expected_marker()` rejects it before parsing the marker. The altered page also fails the independent content comparison. This is the kind of corruption the digest detects.
3. **Changed inside the build:** the same build step packs the changed page, writes a correct marker and reports the digest of those changed bytes. The real publisher accepts the digest/marker; independent approved-content comparison fails. A matching hash is not a source review, dependency safety proof, artifact signature from another trust root or application acceptance test.

The current workflow gives the build job no AWS OIDC permission and reserves temporary AWS credentials for the later publisher job. That separation limits build-job cloud authority but does not make its output automatically trustworthy. Review source writers, workflow changes and build dependencies before enabling publication; test the served page and private API separately afterward. The local fixture uses invented strings and no AWS access. It does not demonstrate an actual malicious dependency, a GitHub Actions run, IAM enforcement or customer behavior.
