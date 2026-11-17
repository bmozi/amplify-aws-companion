# Your first exercise: learn before spending

Imagine renting equipment for a two-hour experiment and forgetting it for three days. The equipment did not become more expensive per hour; you bought more hours. We can learn this lesson with invented numbers on a laptop before renting anything from AWS.

This exercise needs an existing Python 3 installation and a trusted copy of this repository. It needs no AWS account, login, Node, Terraform, Docker or extra Python packages. The program calculates fictional costs and checks its own arithmetic. It does not query prices, contact AWS, publish a website or set a spending limit.

## Find the right folder

Open a terminal in the folder containing this repository's `README.md`, `scripts` and `examples` folders. That folder is called the **repository root**; it has nothing to do with the AWS root identity. Your copy may be in any folder you chose.

Run these commands one at a time from that folder:

```sh
python3 --version
python3 examples/costs/lifecycle-exercise.py
```

The first asks your computer which Python it will use. The second asks Python to run one specific file. Do not add `-O`: that option disables assertions, the checks this teaching program relies on. If your installation uses `python` or `py -3` instead, use that interpreter consistently after checking its version. The recorded execution for this lesson is on macOS; these alternatives are not a claim of Windows testing.

Before the second command, predict the results using these **invented** inputs:

| Item | Calculation |
| --- | --- |
| Running equipment | $0.05 for each hour |
| Retained storage | 3 days at $0.02 per day |
| Requests | 500,000 at $0.0000002 per request |
| Extra allowance for uncertainty | Add 50% to the subtotal |

Compare two hours with 72 hours. Keep storage and requests unchanged in this particular comparison. In a real system they might also grow; that is one reason this small model is not an AWS quote.

## Read what actually happened

The output begins with `INVENTED RATES`. Find the two duration rows and compare them with your prediction:

| Duration | Subtotal | With 50% allowance | Fictional $80 credit balance afterward |
| --- | --- | --- | --- |
| 2 hours | $0.26 | $0.39 | $79.61 |
| 72 hours | $3.76 | $5.64 | $74.36 |

The two-hour case meets both teaching rules: an estimated run at most $4 and at least $75 remaining. The 72-hour case fails both. `True` and `False` report these comparisons. They do not install a cloud control that stops spending. The $80 starting balance and both rules are invented for this exercise; choose limits appropriate to your own account.

You will also see a deliberately wrong request calculation of $100,000. The program demonstrates the mistake of entering a per-million rate as a per-request rate; it did not spend that money. Later lines compare cost per completed result, retry attempts and shared-cost allocations. Return to those after you can explain the first two rows; [the outcome review](../examples/costs/OUTCOME-REVIEW.md) develops them further.

A `PASS` line means the corresponding programmed check succeeded. Read the entire output: an early pass does not cancel a later failure. Successful completion means the process finishes with exit code zero. In a macOS or Linux shell, run `echo $?` immediately afterward to inspect that code. A different command in between replaces the status you intended to inspect.

If Python reports that it cannot open the file, check your folder and the path before changing code. If the command is unavailable, Python installation is a prerequisite still to resolve. If there is a traceback or assertion failure, keep the error and source revision: do not remove a check merely to produce a pass. This exercise creates no cloud resources to remove. Python may leave a local `__pycache__` folder for the imported calculator; that is a local cache, not deployed infrastructure.

## Learn to classify the next command

The command's purpose and implementation determine its effect. A familiar program name alone does not prove that a command is local or harmless.

| Example in this repository | What it does | What you need before running it |
| --- | --- | --- |
| `python3 examples/costs/lifecycle-exercise.py` | Local fictional arithmetic | Python and trusted source |
| `python3 scripts/check-companion.py` | Runs the larger explicit local suite and writes a local report | Its additional tools; inspect the script and its prerequisites before running it |
| `aws amplify get-app …` | Reads an actual AWS app's settings | Authorized account access and the intended account/region/app |
| `python3 scripts/deploy-frontend.py` | Uploads built files and starts a real publication | Reviewed deployment identity, correct build, target and cost controls |
| `terraform apply` | Can create, change or remove resources described by the selected configuration | Reviewed configuration, plan, identity, state ownership and spending/cleanup decision |

The ellipsis in the inspection example means arguments are omitted; it is not a command to paste. A local build and a Git push are also different from deployment in our recorded manual setup. A future configured pipeline can connect a push to deployment. Read the [Field Lab reader playbook](FIELD-LAB-READER-PLAYBOOK.md#the-github-badge-and-the-publish-switch) before assuming a push has no cloud effect.

## Explain it, then change the situation

Without editing the program, calculate a third case: ten hours of equipment, the same storage and requests, and the same 50% allowance. Explain whether it meets both rules with the fictional $80 balance. Then change the starting balance to $75.50. Can a run satisfy the $4 rule while failing the reserve rule?

Check your reasoning afterward: the subtotal is $0.66 and the allowance brings it to $0.99. The remaining balances are $79.01 and $74.51. The second balance fails the reserve rule even though the run estimate is under $4. Neither rule is an automatic shutdown mechanism.

Ask Codex: “Use this exercise as a tutor. Ask me to predict one result before revealing it. Help me distinguish an arithmetic check, a current AWS price and an enforced spending limit. Do not install tools, access AWS or change the source.” Verify its arithmetic yourself and record any assistance.

Use the [learning-record worksheet](../curriculum/LEARNING-RECORD.md) to retain your attempt. Your learning evidence should contain your prediction, observed output, source revision and a short explanation of the changed case. A successful run establishes local arithmetic behavior. Your explanation demonstrates something different: whether you understand why the result changes.

Continue reading [cost and business constraints](../reader/BOOK-LOCATORS.md#book-97215f8e0e3f150d). For your next small hands-on task, use [the guided data-contract exercise](../examples/data-contract/README.md#start-with-one-update) to predict and inspect a local JSON update. The [learning routes](../curriculum/LEARNING-ROUTES.md) connect these foundations to the first Amplify walkthrough. The larger suite is useful later; it is not a prerequisite for either introductory exercise.
