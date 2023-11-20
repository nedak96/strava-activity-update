data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "update_strava_activity_role" {
  name               = "update-strava-activity-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
}

data "aws_iam_policy_document" "update_strava_activity_policy_doc" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    actions = [
      "dynamodb:GetItem",
      "dynamodb:UpdateItem"
    ]
    resources = [aws_dynamodb_table.strava_tokens.arn]
  }
}

resource "aws_iam_policy" "update_strava_activity_policy" {
  name        = "update-strava-activity-policy"
  description = "Policy for the update Strava activity lambda function"
  policy      = data.aws_iam_policy_document.update_strava_activity_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "update_strava_activity" {
  role       = aws_iam_role.update_strava_activity_role.name
  policy_arn = aws_iam_policy.update_strava_activity_policy.arn
}
