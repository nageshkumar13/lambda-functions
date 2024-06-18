# create zip file 

data "archive_file" "python_lambda_package" {  
  type = "zip"  
  source_file = "source.py" 
  output_path = "source_code.zip"
}

# define Lambda function

resource "aws_lambda_function" "snapshot_deletion_lambda_function" {
        function_name = "snapshot_deletion"
        filename      = "source_code.zip"
        source_code_hash = data.archive_file.python_lambda_package.output_base64sha256
        role          = aws_iam_role.iam_for_lambda.arn
        runtime       = "python3.9"
        handler       = "source.lambda_handler"
        timeout       = 10
}