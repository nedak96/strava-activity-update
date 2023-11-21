locals {
  path_source_code = "${path.module}/.."
  function_name    = "upload-garmin-runs-to-strava"
  runtime          = "python3.11"
}

data "archive_file" "source_code_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda"
  output_path = "${path.module}/files/upload-garmin-runs-to-strava.zip"
}

resource "aws_lambda_function" "upload_garmin_runs_to_strava" {
  filename         = data.archive_file.source_code_zip.output_path
  function_name    = local.function_name
  role             = aws_iam_role.upload_garmin_runs_to_strava_role.arn
  handler          = "index.handler"
  runtime          = local.runtime
  timeout          = 30
  source_code_hash = data.archive_file.source_code_zip.output_base64sha256
  layers           = [aws_lambda_layer_version.python_dependencies_lambda_layer.arn]
  environment {
    variables = {
      STRAVA_CLIENT_ID         = var.strava_client_id
      STRAVA_CLIENT_SECRET     = var.strava_client_secret
      STRAVA_TOKENS_TABLE_NAME = aws_dynamodb_table.strava_tokens.name
      ACCESS_TOKEN_KEY         = local.access_token_key
      REFRESH_TOKEN_KEY        = local.refresh_token_key
      GARMIN_USERNAME          = var.garmin_username
      GARMIN_PASSWORD          = var.garmin_password
    }
  }

  lifecycle {
    ignore_changes = [environment]
  }
}

resource "aws_cloudwatch_log_group" "upload_garmin_runs_to_strava_lambda_logs" {
  name = "/aws/lambda/${aws_lambda_function.upload_garmin_runs_to_strava.function_name}"
  retention_in_days = 3
}

resource "aws_cloudwatch_event_rule" "every_minute" {
  name                = "every-minute"
  description         = "Fires every minute"
  schedule_expression = "rate(1 minute)"
}

resource "aws_cloudwatch_event_target" "upload_garmin_runs_to_strava_every_minute" {
  rule      = aws_cloudwatch_event_rule.every_minute.name
  target_id = "upload-garmin-runs-to-strava-every-minute"
  arn       = aws_lambda_function.upload_garmin_runs_to_strava.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_lambda_trigger" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.upload_garmin_runs_to_strava.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_minute.arn
}
