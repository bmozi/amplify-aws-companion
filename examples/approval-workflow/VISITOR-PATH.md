# Check the page after the publisher says yes

Maya's two reviewers approve revision 1 of a fictional training price list. The [earlier separate-store drill](EXTERNAL-EFFECT.md) proves only that a simulated publisher recorded the operation after a lost reply. This continuation asks what a visitor actually receives from a third local store and loopback HTTP route. Read [the illustrated lesson](../../reader/BOOK-LOCATORS.md#book-fe5e217fb74cb1df) before running it.

Predict the page after the provider commits but before the site pointer changes, then run from the repository root:

```sh
python3 examples/approval-workflow/visitor_path.py
python3 -m unittest discover -s examples/approval-workflow -p 'test_visitor_path.py' -v
```

The script creates three temporary SQLite files: review/dispatch state, a publisher receipt, and a site pointer holding response bytes. A loopback HTTP listener serves `/training-site/prices`. The provider commits revision 1 and loses its reply. The local action is `unknown`, while the visitor still receives **revision 0**. The site promotion refuses to run until the exact operation is reconciled and the content digest, destination and provider receipt match. After that separate local step, the same HTTP path serves **revision 1**. `/public-site/prices` returns 404. The three focused tests also reject changed content and a mismatched provider receipt.

Before opening [the assessor](VISITOR-PATH-ASSESSOR.md), explain which observation supports each sentence: “two people approved revision 1,” “the publisher recorded revision 1,” and “the visitor received revision 1.” Change the case so the site serves an old cached copy after local promotion. Which evidence would you need from the **actual** host and browser? Change it again so a page loads but shows the wrong price or links to the wrong order flow. A 200 is not a business acceptance test. Ask Codex to propose one false-green path, then verify its claim against the actual program output and source.

The fixture uses trusted reviewer strings, deterministic bytes and an intentionally separate site-selection step. It does not authenticate a person, publish to AWS Amplify, test GitHub Actions, CDN/browser caches, TLS, multiple assets, a real provider API, customer purchase behavior, rollback, current price or spending. The HTTP server binds to loopback and the temporary stores are removed. A future cloud test needs a scoped identity, reviewed whole-run estimate and cleanup record. Choose spending and reserve limits from the account that would host the test. This local exercise uses no AWS resources or credits.
