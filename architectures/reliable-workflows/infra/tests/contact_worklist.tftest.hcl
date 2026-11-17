mock_provider "aws" {
  mock_resource "aws_iam_role" {
    defaults = { arn = "arn:aws:iam::123456789012:role/mock" }
  }
  mock_resource "aws_lambda_function" {
    defaults = { arn = "arn:aws:lambda:us-east-2:123456789012:function:mock" }
  }
  mock_resource "aws_sqs_queue" {
    defaults = { arn = "arn:aws:sqs:us-east-2:123456789012:mock" }
  }
}
mock_provider "archive" {}

run "default_omits_contact_function" {
  command = plan
  variables {
    account_id              = "123456789012"
    approved_run_budget_usd = 1
    estimated_run_cost_usd  = 0.5
    expires_at_epoch        = 1893456000
  }
  assert {
    condition     = length(aws_lambda_function.lab) == 4 && !contains(keys(aws_lambda_function.lab), "contact_worklist")
    error_message = "The default stack must not create the contact function."
  }
}

run "manual_opt_in_has_one_scoped_function_and_no_trigger" {
  command = apply
  variables {
    account_id              = "123456789012"
    approved_run_budget_usd = 1
    estimated_run_cost_usd  = 0.5
    expires_at_epoch        = 1893456000
    enable_contact_worklist = true
  }
  assert {
    condition     = length(aws_lambda_function.lab) == 5 && contains(keys(aws_lambda_function.lab), "contact_worklist")
    error_message = "Manual opt-in should add one contact function."
  }
  assert {
    condition     = length(aws_scheduler_schedule.due_tick) == 0 && aws_lambda_event_source_mapping.work.function_name == aws_lambda_function.lab["worker"].arn
    error_message = "Contact opt-in must not add a schedule or consume the work queue."
  }
  assert {
    condition     = length(jsondecode(aws_iam_role_policy.function["contact_worklist"].policy).Statement) == 2 && toset(jsondecode(aws_iam_role_policy.function["contact_worklist"].policy).Statement[0].Action) == toset(["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:ConditionCheckItem", "dynamodb:Scan"]) && jsondecode(aws_iam_role_policy.function["contact_worklist"].policy).Statement[0].Resource == aws_dynamodb_table.lab.arn
    error_message = "The contact execution role needs only the lab-table actions plus its log stream."
  }
}
