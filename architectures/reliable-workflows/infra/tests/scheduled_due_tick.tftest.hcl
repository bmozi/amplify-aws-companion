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
  mock_resource "aws_scheduler_schedule_group" {
    defaults = { arn = "arn:aws:scheduler:us-east-2:123456789012:schedule-group/mock" }
  }
}
mock_provider "archive" {}

run "manual_default_has_no_recurring_resources" {
  command = plan
  variables {
    account_id              = "123456789012"
    approved_run_budget_usd = 1
    estimated_run_cost_usd  = 0.5
    expires_at_epoch        = 1893456000
  }
  assert {
    condition     = length(aws_scheduler_schedule.due_tick) == 0 && length(aws_scheduler_schedule_group.due_tick) == 0
    error_message = "The default lab must not create a recurring schedule."
  }
  assert {
    condition     = length(aws_sqs_queue.tick_delivery_failed) == 0 && length(aws_sqs_queue.tick_execution_failed) == 0
    error_message = "The default lab must not create tick failure queues."
  }
  assert {
    condition     = length(aws_lambda_function.lab) == 4
    error_message = "The default lab should retain its original four functions."
  }
}

run "opt_in_has_bounded_route_and_distinct_failure_paths" {
  command = apply
  override_resource {
    target = aws_sqs_queue.tick_delivery_failed[0]
    values = { arn = "arn:aws:sqs:us-east-2:123456789012:delivery" }
  }
  override_resource {
    target = aws_sqs_queue.tick_execution_failed[0]
    values = { arn = "arn:aws:sqs:us-east-2:123456789012:execution" }
  }
  variables {
    account_id               = "123456789012"
    approved_run_budget_usd  = 1
    estimated_run_cost_usd   = 0.5
    expires_at_epoch         = 1893456000
    enable_due_tick_schedule = true
  }
  assert {
    condition     = length(aws_scheduler_schedule.due_tick) == 1 && length(aws_lambda_function.lab) == 5
    error_message = "Opt-in should create one schedule and one dedicated function."
  }
  assert {
    condition     = aws_scheduler_schedule.due_tick[0].schedule_expression == "rate(1 minute)" && aws_scheduler_schedule.due_tick[0].end_date == "2030-01-01T00:00:00Z"
    error_message = "The tick must have a one-minute recurrence and the reviewed UTC end."
  }
  assert {
    condition     = aws_scheduler_schedule.due_tick[0].target[0].dead_letter_config[0].arn == aws_sqs_queue.tick_delivery_failed[0].arn && aws_lambda_function_event_invoke_config.due_tick[0].destination_config[0].on_failure[0].destination == aws_sqs_queue.tick_execution_failed[0].arn
    error_message = "Delivery and execution failures need separate queues."
  }
  assert {
    condition     = jsondecode(aws_iam_role.due_tick_scheduler[0].assume_role_policy).Statement[0].Condition.StringEquals["aws:SourceArn"] == aws_scheduler_schedule_group.due_tick[0].arn
    error_message = "The Scheduler role trust must be scoped to its schedule group."
  }
  assert {
    condition     = aws_scheduler_schedule.due_tick[0].target[0].retry_policy[0].maximum_retry_attempts == 1 && aws_lambda_function_event_invoke_config.due_tick[0].maximum_retry_attempts == 1
    error_message = "Both delivery and execution retries must be explicit."
  }
  assert {
    condition     = length(aws_cloudwatch_metric_alarm.tick_delivery_failed) == 1 && length(aws_cloudwatch_metric_alarm.tick_execution_failed) == 1 && length(aws_cloudwatch_metric_alarm.due_tick_errors) == 1 && length(aws_cloudwatch_metric_alarm.due_tick_destination_delivery_failures) == 1
    error_message = "Opt-in should expose all four console alarms."
  }
}
