
# connect to aws.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}


provider "aws" {
    profile = "terraform"
}

terraform {
    backend "s3" {
        bucket = "my-app-backend-17-05"
        key = "tf/backend-state/snapshot-cleanup-lambda-function/tf-state"
        region = "ap-south-1"
        dynamodb_table = "my-app-locks"
        encrypt = true
    }
}





