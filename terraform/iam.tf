data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "upload_garmin_runs_to_strava_role" {
  name               = "upload-garmin-runs-to-strava-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
}

data "aws_iam_policy_document" "upload_garmin_runs_to_strava_policy_doc" {
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

resource "aws_iam_policy" "upload_garmin_runs_to_strava_policy" {
  name        = "upload-garmin-runs-to-strava-policy"
  description = "Policy for the upload Garmin runs to Strava lambda function"
  policy      = data.aws_iam_policy_document.upload_garmin_runs_to_strava_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "upload_garmin_runs_to_strava" {
  role       = aws_iam_role.upload_garmin_runs_to_strava_role.name
  policy_arn = aws_iam_policy.upload_garmin_runs_to_strava_policy.arn
}
