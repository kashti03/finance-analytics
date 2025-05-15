# Create ZIP file for Lambda function
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/lambda_function.zip"
}

# DynamoDB Table
resource "aws_dynamodb_table" "finance_data" {
  name           = "${var.environment}_finance_data"
  billing_mode   = var.dynamodb_billing_mode
  hash_key       = "id"
  
  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}
resource "aws_dynamodb_table" "order_report_data" {
  name         = "${var.environment}_order_report_data"
  billing_mode = var.dynamodb_billing_mode
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_dynamodb_table" "product_report_data" {
  name         = "${var.environment}_product_report_data"
  billing_mode = var.dynamodb_billing_mode
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}
# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.environment}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.environment}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = ["${aws_dynamodb_table.finance_data.arn}",
          "${aws_dynamodb_table.order_report_data.arn}",
          "${aws_dynamodb_table.product_report_data.arn}"]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = ["arn:aws:logs:*:*:*"]
      }
    ]
  })
}

# Lambda Function
resource "aws_lambda_function" "data_analytics_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.environment}_data_analytics"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  runtime = "python3.12"

  environment {
  variables = {
    FINANCE_TABLE_NAME        = aws_dynamodb_table.finance_data.name
    ORDER_REPORT_TABLE_NAME   = aws_dynamodb_table.order_report_data.name
    PRODUCT_REPORT_TABLE_NAME = aws_dynamodb_table.product_report_data.name
  }
}

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}