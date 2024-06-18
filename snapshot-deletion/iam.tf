# This resource creates an IAM role with the necessary permissions for the Lambda function.

resource "aws_iam_role" "iam_for_lambda" {
  name               = "snapshot_deletion"
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [       
      {
        "Action": "sts:AssumeRole",
        "Principal": {
          "Service": "lambda.amazonaws.com"   
        },
        "Effect": "Allow",
        "Sid": ""       
      }         
    ]           
  }   
EOF        
}

# IAM policy for the lambda

resource "aws_iam_policy" "iam_policy_for_lambda" {

  name         = "snapshot_deletion_policy"
  path         = "/"
  description  = "AWS IAM Policy for managing aws lambda role for snap shot deletioon"
  policy = jsonencode(
{
  "Version": "2012-10-17",
  "Statement": [
      {
        Effect   = "Allow"
        Action   = [
            "ec2:DescribeInstances",
            "ec2:DeleteSnapshot",
            "ec2:DescribeVolumes",
            "ec2:DescribeSnapshots"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = [
           "logs:CreateLogGroup",
           "logs:CreateLogStream",
           "logs:PutLogEvents"
        ]
        "Resource": "arn:aws:logs:*:*:*",
        "Effect": "Allow"
      },
    ]
})
}

# Role - Policy Attachment
resource "aws_iam_role_policy_attachment" "attach_iam_policy_to_iam_role" {
  role        = aws_iam_role.iam_for_lambda.name
  policy_arn  = aws_iam_policy.iam_policy_for_lambda.arn
}

