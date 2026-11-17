output "resource_creation_enabled" {
  description = "A configuration flag, not evidence that AWS accepted any resource."
  value       = var.enable_resources
}

output "alarm_name" {
  value = var.enable_resources ? aws_cloudwatch_metric_alarm.server_errors[0].alarm_name : null
}

output "topic_arn" {
  value = var.enable_resources ? aws_sns_topic.alerts[0].arn : null
}
