terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.12"
    }
  }
  
  backend "s3" {
    bucket = "727646514588-terraform-state-bucket"
    key    = "projects/finance-analytics.tfstate"
    region = "us-west-2"
  }
}

provider "aws" {
  region = var.aws_region
}