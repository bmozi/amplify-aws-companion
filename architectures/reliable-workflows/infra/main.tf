terraform {
  required_version = ">= 1.6, < 2.0"
  required_providers {
    aws     = { source = "hashicorp/aws", version = "~> 5.100.0" }
    archive = { source = "hashicorp/archive", version = "~> 2.7" }
  }
}
variable "account_id" {
  type = string
  validation {
    condition     = can(regex("^[0-9]{12}$", var.account_id))
    error_message = "Supply the confirmed 12-digit sandbox account."
  }
}
variable "region" { default = "us-east-2" }
variable "lab_name" {
  default = "amplify-patterns-practice"
  validation {
    condition     = can(regex("^amplify-patterns-[a-z0-9-]{1,24}$", var.lab_name))
    error_message = "Use an isolated amplify-patterns- name."
  }
}
variable "approved_run_budget_usd" {
  type        = number
  description = "Human-approved working budget; not a billing cap."
  validation {
    condition     = var.approved_run_budget_usd > 0 && var.approved_run_budget_usd <= 5
    error_message = "This personal teaching run requires a reviewed budget greater than zero and at most USD 5."
  }
}
variable "estimated_run_cost_usd" {
  type        = number
  description = "Reviewed estimate including retries, polling, storage and logs; no default or assumed Free Tier."
}
variable "expires_at_epoch" {
  type        = number
  description = "UTC Unix timestamp after which handlers refuse work. This does not delete resources or stop storage charges."
}
variable "enable_due_tick_schedule" {
  type        = bool
  default     = false
  description = "Opt-in recurring A03 due-hold tick. Requires a separately completed scheduled-run worksheet."
}
variable "enable_contact_worklist" {
  type        = bool
  default     = false
  description = "Opt-in manual A02 overdue-contact checker and worklist reader; no schedule or notification."
}
provider "aws" {
  region              = var.region
  allowed_account_ids = [var.account_id]
  default_tags {
    tags = { Project = "amplify-aws-patterns", Environment = "disposable-learning", ManagedBy = "Terraform" }
  }
}
resource "terraform_data" "cost_gate" {
  lifecycle {
    precondition {
      condition     = var.estimated_run_cost_usd > 0 && var.estimated_run_cost_usd <= var.approved_run_budget_usd
      error_message = "Supply a positive reviewed cost estimate within the approved working budget."
    }
    precondition {
      condition     = var.expires_at_epoch > 0
      error_message = "Set an explicit lab expiry. The run wrapper restricts it to two hours."
    }
  }
}
resource "aws_dynamodb_table" "lab" {
  name         = var.lab_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  attribute {
    name = "pk"
    type = "S"
  }
  attribute {
    name = "due_partition"
    type = "S"
  }
  attribute {
    name = "expires_at"
    type = "N"
  }
  global_secondary_index {
    name            = "due-holds"
    hash_key        = "due_partition"
    range_key       = "expires_at"
    projection_type = "KEYS_ONLY"
    on_demand_throughput {
      max_read_request_units  = 20
      max_write_request_units = 20
    }
  }
  on_demand_throughput {
    max_read_request_units  = 20
    max_write_request_units = 20
  }
  server_side_encryption { enabled = true }
  # Disposable synthetic data only: destroy deliberately removes the table.
}
resource "aws_sqs_queue" "failed" {
  name                      = "${var.lab_name}-failed"
  message_retention_seconds = 86400
  sqs_managed_sse_enabled   = true
}
resource "aws_sqs_queue" "work" {
  name                       = "${var.lab_name}-work"
  visibility_timeout_seconds = 60
  message_retention_seconds  = 3600
  sqs_managed_sse_enabled    = true
  redrive_policy             = jsonencode({ deadLetterTargetArn = aws_sqs_queue.failed.arn, maxReceiveCount = 3 })
}
resource "aws_sqs_queue_redrive_allow_policy" "failed" {
  queue_url            = aws_sqs_queue.failed.id
  redrive_allow_policy = jsonencode({ redrivePermission = "byQueue", sourceQueueArns = [aws_sqs_queue.work.arn] })
}
locals {
  functions = toset(concat(["intake", "dispatcher", "worker", "reservation"], var.enable_due_tick_schedule ? ["due_tick"] : [], var.enable_contact_worklist ? ["contact_worklist"] : []))
  table_actions = {
    intake           = ["dynamodb:GetItem", "dynamodb:PutItem"]
    dispatcher       = ["dynamodb:Scan", "dynamodb:UpdateItem"]
    worker           = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem"]
    reservation      = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:DeleteItem", "dynamodb:ConditionCheckItem", "dynamodb:Scan"]
    due_tick         = ["dynamodb:GetItem", "dynamodb:UpdateItem", "dynamodb:DeleteItem", "dynamodb:ConditionCheckItem"]
    contact_worklist = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:ConditionCheckItem", "dynamodb:Scan"]
  }
}
data "archive_file" "code" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/../build/functions.zip"
  excludes    = ["__pycache__"]
}
resource "aws_cloudwatch_log_group" "function" {
  for_each          = local.functions
  name              = "/aws/lambda/${var.lab_name}-${each.key}"
  retention_in_days = 1
}
resource "aws_iam_role" "function" {
  for_each           = local.functions
  name               = "${var.lab_name}-${each.key}"
  assume_role_policy = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Service = "lambda.amazonaws.com" }, Action = "sts:AssumeRole" }] })
}
resource "aws_iam_role_policy" "function" {
  for_each = local.functions
  role     = aws_iam_role.function[each.key].id
  policy = jsonencode({ Version = "2012-10-17", Statement = concat([
    { Effect = "Allow", Action = local.table_actions[each.key], Resource = aws_dynamodb_table.lab.arn },
    { Effect = "Allow", Action = ["logs:CreateLogStream", "logs:PutLogEvents"], Resource = "${aws_cloudwatch_log_group.function[each.key].arn}:*" }
    ], contains(["reservation", "due_tick"], each.key) ? [
    { Effect = "Allow", Action = ["dynamodb:Query"], Resource = "${aws_dynamodb_table.lab.arn}/index/due-holds" }
    ] : [], each.key == "dispatcher" ? [
    { Effect = "Allow", Action = ["sqs:SendMessage"], Resource = aws_sqs_queue.work.arn }
    ] : [], each.key == "worker" ? [
    { Effect = "Allow", Action = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"], Resource = aws_sqs_queue.work.arn }
  ] : []) })
}
resource "aws_lambda_function" "lab" {
  for_each                       = local.functions
  function_name                  = "${var.lab_name}-${each.key}"
  role                           = aws_iam_role.function[each.key].arn
  filename                       = data.archive_file.code.output_path
  source_code_hash               = data.archive_file.code.output_base64sha256
  runtime                        = "python3.12"
  handler                        = "handlers.${each.key}"
  timeout                        = 10
  memory_size                    = 128
  reserved_concurrent_executions = 2
  environment {
    variables = {
      TABLE_NAME       = aws_dynamodb_table.lab.name
      QUEUE_URL        = aws_sqs_queue.work.id
      EXPIRES_AT_EPOCH = tostring(var.expires_at_epoch)
    }
  }
  depends_on = [aws_iam_role_policy.function, terraform_data.cost_gate]
}
resource "aws_lambda_event_source_mapping" "work" {
  event_source_arn        = aws_sqs_queue.work.arn
  function_name           = aws_lambda_function.lab["worker"].arn
  batch_size              = 5
  function_response_types = ["ReportBatchItemFailures"]
  scaling_config { maximum_concurrency = 2 }
}
output "lab" {
  value = {
    name             = var.lab_name
    account          = var.account_id
    region           = var.region
    table            = aws_dynamodb_table.lab.name
    queue            = aws_sqs_queue.work.id
    failed_queue     = aws_sqs_queue.failed.id
    functions        = { for k, f in aws_lambda_function.lab : k => f.function_name }
    expires_at_epoch = var.expires_at_epoch
  }
}
