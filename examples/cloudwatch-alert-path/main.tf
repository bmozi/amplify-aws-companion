terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.83.0, < 7.0.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  alarm_name = "${var.name_prefix}-booking-server-errors"
  namespace  = "AmplifyAWS/BookingLab"
}

# The default false gate keeps this a local configuration lesson.
resource "aws_cloudwatch_log_group" "booking" {
  count             = var.enable_resources ? 1 : 0
  name              = "/amplify-aws/${var.name_prefix}/booking"
  retention_in_days = var.log_retention_days
  log_group_class   = "STANDARD"

  tags = var.tags
}

resource "aws_cloudwatch_log_metric_filter" "server_errors" {
  count          = var.enable_resources ? 1 : 0
  name           = "${var.name_prefix}-booking-5xx"
  log_group_name = aws_cloudwatch_log_group.booking[0].name
  pattern        = "{ $.statusCode >= 500 }"

  metric_transformation {
    name          = "ServerErrors"
    namespace     = local.namespace
    value         = "1"
    default_value = 0
    unit          = "Count"
  }
}

resource "aws_sns_topic" "alerts" {
  count = var.enable_resources ? 1 : 0
  name  = "${var.name_prefix}-booking-alerts"
  tags  = var.tags
}

# A topic with zero confirmed subscriptions has no human delivery path.
resource "aws_sns_topic_subscription" "email" {
  count     = var.enable_resources && var.notification_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts[0].arn
  protocol  = "email"
  endpoint  = var.notification_email
}

resource "aws_cloudwatch_metric_alarm" "server_errors" {
  count               = var.enable_resources ? 1 : 0
  alarm_name          = local.alarm_name
  alarm_description   = "Teaching alarm for received booking 5xx log events; check source freshness separately"
  namespace           = local.namespace
  metric_name         = aws_cloudwatch_log_metric_filter.server_errors[0].metric_transformation[0].name
  statistic           = "Sum"
  period              = 60
  evaluation_periods  = 2
  datapoints_to_alarm = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "missing"
  alarm_actions       = [aws_sns_topic.alerts[0].arn]

  tags = var.tags
}

# This policy grants the newly created alarm only, with owner access retained.
resource "aws_sns_topic_policy" "alerts" {
  count = var.enable_resources ? 1 : 0
  arn   = aws_sns_topic.alerts[0].arn
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AccountOwnerAdministration"
        Effect    = "Allow"
        Principal = { AWS = "arn:aws:iam::${var.account_id}:root" }
        Action    = "SNS:*"
        Resource  = aws_sns_topic.alerts[0].arn
      },
      {
        Sid       = "BookingAlarmPublish"
        Effect    = "Allow"
        Principal = { Service = "cloudwatch.amazonaws.com" }
        Action    = "sns:Publish"
        Resource  = aws_sns_topic.alerts[0].arn
        Condition = {
          ArnEquals    = { "aws:SourceArn" = aws_cloudwatch_metric_alarm.server_errors[0].arn }
          StringEquals = { "aws:SourceAccount" = var.account_id }
        }
      }
    ]
  })
}

resource "aws_cloudwatch_dashboard" "booking" {
  count          = var.enable_resources ? 1 : 0
  dashboard_name = "${var.name_prefix}-booking-operations"
  dashboard_body = jsonencode({
    start = "-PT3H"
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title   = "Received booking 5xx log events"
          region  = var.aws_region
          metrics = [[local.namespace, "ServerErrors"]]
          period  = 60
          stat    = "Sum"
        }
      },
      {
        type   = "alarm"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "Server error alarm state"
          alarms = [aws_cloudwatch_metric_alarm.server_errors[0].arn]
        }
      }
    ]
  })
}
