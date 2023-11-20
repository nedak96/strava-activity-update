locals {
  path_source_code = "${path.module}/.."
  function_name    = "update-strava-activity"
  runtime          = "python3.11"
}

data "archive_file" "source_code_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda"
  output_path = "${path.module}/files/update-strava-activity.zip"
}

data "aws_lambda_function" "update_strava_activity" {
  count         = var.strava_client_id == "" ? 0 : 1
  function_name = local.function_name
}

resource "aws_lambda_function" "update_strava_activity" {
  filename         = data.archive_file.source_code_zip.output_path
  function_name    = local.function_name
  role             = aws_iam_role.update_strava_activity_role.arn
  handler          = "index.handler"
  runtime          = local.runtime
  source_code_hash = data.archive_file.source_code_zip.output_base64sha256
  layers           = [aws_lambda_layer_version.python_dependencies_lambda_layer.arn]
  environment {
    variables = {
      STRAVA_CLIENT_ID         = var.strava_client_id
      STRAVA_CLIENT_SECRET     = var.strava_client_secret
      STRAVA_TOKENS_TABLE_NAME = aws_dynamodb_table.strava_tokens.name
      ACCESS_TOKEN_KEY         = local.access_token_key
      REFRESH_TOKEN_KEY        = local.refresh_token_key
    }
  }

  lifecycle {
    ignore_changes = [environment]
  }
}

resource "aws_cloudwatch_event_rule" "every_minute" {
  name                = "every-minute"
  description         = "Fires every minute"
  schedule_expression = "rate(1 minute)"
}

resource "aws_cloudwatch_event_target" "update_strava_activity_every_minute" {
  rule      = aws_cloudwatch_event_rule.every_minute.name
  target_id = "update-strava-activity-every-minute"
  arn       = aws_lambda_function.update_strava_activity.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_lambda_trigger" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.update_strava_activity.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_minute.arn
}
