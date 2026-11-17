# Every resource in this file is absent in the default manual-only lab.
resource "aws_scheduler_schedule_group" "due_tick" {
  count = var.enable_due_tick_schedule ? 1 : 0
  name  = "${var.lab_name}-due-tick"
}

resource "aws_sqs_queue" "tick_delivery_failed" {
  count                     = var.enable_due_tick_schedule ? 1 : 0
  name                      = "${var.lab_name}-tick-delivery-failed"
  message_retention_seconds = 86400
  sqs_managed_sse_enabled   = true
}

resource "aws_sqs_queue" "tick_execution_failed" {
  count                     = var.enable_due_tick_schedule ? 1 : 0
  name                      = "${var.lab_name}-tick-execution-failed"
  message_retention_seconds = 86400
  sqs_managed_sse_enabled   = true
}

resource "aws_iam_role" "due_tick_scheduler" {
  count = var.enable_due_tick_schedule ? 1 : 0
  name  = "${var.lab_name}-due-tick-scheduler"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "scheduler.amazonaws.com" }
      Action    = "sts:AssumeRole"
      Condition = { StringEquals = {
        "aws:SourceAccount" = var.account_id
        "aws:SourceArn"     = aws_scheduler_schedule_group.due_tick[0].arn
      } }
    }]
  })
}

resource "aws_iam_role_policy" "due_tick_scheduler" {
  count = var.enable_due_tick_schedule ? 1 : 0
  role  = aws_iam_role.due_tick_scheduler[0].id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Effect = "Allow", Action = ["lambda:InvokeFunction"], Resource = aws_lambda_function.lab["due_tick"].arn },
      { Effect = "Allow", Action = ["sqs:SendMessage"], Resource = aws_sqs_queue.tick_delivery_failed[0].arn }
    ]
  })
}

resource "aws_iam_role_policy" "due_tick_failure" {
  count = var.enable_due_tick_schedule ? 1 : 0
  role  = aws_iam_role.function["due_tick"].id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["sqs:SendMessage"]
      Resource = aws_sqs_queue.tick_execution_failed[0].arn
    }]
  })
}

resource "aws_lambda_function_event_invoke_config" "due_tick" {
  count                        = var.enable_due_tick_schedule ? 1 : 0
  function_name                = aws_lambda_function.lab["due_tick"].function_name
  maximum_event_age_in_seconds = 120
  maximum_retry_attempts       = 1
  destination_config {
    on_failure {
      destination = aws_sqs_queue.tick_execution_failed[0].arn
    }
  }
  depends_on = [aws_iam_role_policy.due_tick_failure]
}

resource "aws_scheduler_schedule" "due_tick" {
  count                        = var.enable_due_tick_schedule ? 1 : 0
  name                         = "${var.lab_name}-due-tick"
  group_name                   = aws_scheduler_schedule_group.due_tick[0].name
  state                        = "ENABLED"
  schedule_expression          = "rate(1 minute)"
  schedule_expression_timezone = "UTC"
  end_date                     = timeadd("1970-01-01T00:00:00Z", "${var.expires_at_epoch}s")
  flexible_time_window { mode = "OFF" }
  target {
    arn      = aws_lambda_function.lab["due_tick"].arn
    role_arn = aws_iam_role.due_tick_scheduler[0].arn
    input    = jsonencode({ source = "a03-due-tick" })
    dead_letter_config { arn = aws_sqs_queue.tick_delivery_failed[0].arn }
    retry_policy {
      maximum_event_age_in_seconds = 60
      maximum_retry_attempts       = 1
    }
  }
  depends_on = [aws_iam_role_policy.due_tick_scheduler, aws_lambda_function_event_invoke_config.due_tick]
}

resource "aws_cloudwatch_metric_alarm" "tick_delivery_failed" {
  count               = var.enable_due_tick_schedule ? 1 : 0
  alarm_name          = "${var.lab_name}-tick-delivery-failed"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 60
  statistic           = "Maximum"
  threshold           = 0
  treat_missing_data  = "notBreaching"
  dimensions          = { QueueName = aws_sqs_queue.tick_delivery_failed[0].name }
  # No notification destination is installed; the named operator must inspect this alarm.
}

resource "aws_cloudwatch_metric_alarm" "tick_execution_failed" {
  count               = var.enable_due_tick_schedule ? 1 : 0
  alarm_name          = "${var.lab_name}-tick-execution-failed"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 60
  statistic           = "Maximum"
  threshold           = 0
  treat_missing_data  = "notBreaching"
  dimensions          = { QueueName = aws_sqs_queue.tick_execution_failed[0].name }
}

resource "aws_cloudwatch_metric_alarm" "due_tick_errors" {
  count               = var.enable_due_tick_schedule ? 1 : 0
  alarm_name          = "${var.lab_name}-due-tick-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 0
  treat_missing_data  = "notBreaching"
  dimensions          = { FunctionName = aws_lambda_function.lab["due_tick"].function_name }
}

resource "aws_cloudwatch_metric_alarm" "due_tick_destination_delivery_failures" {
  count               = var.enable_due_tick_schedule ? 1 : 0
  alarm_name          = "${var.lab_name}-tick-destination-delivery-failures"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "DestinationDeliveryFailures"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 0
  treat_missing_data  = "notBreaching"
  dimensions          = { FunctionName = aws_lambda_function.lab["due_tick"].function_name }
}

output "due_tick_schedule" {
  value = var.enable_due_tick_schedule ? {
    schedule_arn            = aws_scheduler_schedule.due_tick[0].arn
    delivery_failure_queue  = aws_sqs_queue.tick_delivery_failed[0].id
    execution_failure_queue = aws_sqs_queue.tick_execution_failed[0].id
    alarm_names = [aws_cloudwatch_metric_alarm.tick_delivery_failed[0].alarm_name,
      aws_cloudwatch_metric_alarm.tick_execution_failed[0].alarm_name,
      aws_cloudwatch_metric_alarm.due_tick_errors[0].alarm_name,
    aws_cloudwatch_metric_alarm.due_tick_destination_delivery_failures[0].alarm_name]
  } : null
}
