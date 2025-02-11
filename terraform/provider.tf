terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.12"
    }
  }
  
  backend "s3" {
    bucket = "terraform-state-bucket"
    key    = "projects/financial-analytics.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}