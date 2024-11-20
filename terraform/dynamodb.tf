resource "aws_dynamodb_table" "strava_tokens" {
  name           = "strava_tokens"
  hash_key       = "token_type"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1

  attribute {
    name = "token_type"
    type = "S"
  }
}

resource "aws_dynamodb_table_item" "initial_refresh_token" {
  table_name = aws_dynamodb_table.strava_tokens.name
  hash_key   = aws_dynamodb_table.strava_tokens.hash_key

  item = <<ITEM
{
  "token_type": {"S": "${local.refresh_token_key}"},
  "token": {"S": "${var.strava_initial_refresh_token}"},
  "expires_at": {"N": "0"}
}
ITEM
}

resource "aws_dynamodb_table_item" "initial_access_token" {
  table_name = aws_dynamodb_table.strava_tokens.name
  hash_key   = aws_dynamodb_table.strava_tokens.hash_key

  item = <<ITEM
{
  "token_type": {"S": "${local.access_token_key}"},
  "token": {"S": ""},
  "expires_at": {"N": "0"}
}
ITEM

  lifecycle {
    ignore_changes = [item]
  }
}
