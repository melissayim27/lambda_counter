terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-central-1"
}

# 1. ECR Repository fuer das Docker Image
resource "aws_ecr_repository" "repo" {
  name                 = "counter-repo"
  image_tag_mutability = "MUTABLE"
}

# 2. Bestehendes Subnetz & VPC nutzen (Konform mit Firmen-Richtlinien)
locals {
  subnet_id            = "subnet-044f37ec1d2a17b36"
  permissions_boundary = "arn:aws:iam::545618397441:policy/ECASBubbleOwnerPermissionBoundaries"
}

data "aws_subnet" "selected" {
  id = local.subnet_id
}

resource "aws_security_group" "fargate_sg" {
  name   = "counter-fargate-sg-v2"
  vpc_id = data.aws_subnet.selected.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3. ECS Cluster & Task Definition
resource "aws_ecs_cluster" "cluster" {
  name = "counter-cluster"
}

resource "aws_iam_role" "ecs_execution_role" {
  name                 = "counter-ecs-execution-role"
  permissions_boundary = local.permissions_boundary
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecs_task_definition" "task" {
  family                   = "counter-task-def"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256" # XS Config laut Whiteboard
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([{
    name      = "counter-container"
    image     = "${aws_ecr_repository.repo.repository_url}:latest"
    essential = true
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/counter-task"
        "awslogs-region"        = "eu-central-1"
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/counter-task"
  retention_in_days = 1
}

# 4. Lambda Rolle & Funktion
resource "aws_iam_role" "lambda_role" {
  name                 = "counter-lambda-role"
  permissions_boundary = local.permissions_boundary
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_policy" "lambda_ecs_policy" {
  name = "counter-lambda-ecs-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["ecs:RunTask", "ecs:StopTask", "ecs:ListTasks"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = "iam:PassRole"
        Resource = aws_iam_role.ecs_execution_role.arn
      },
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_ecs_policy.arn
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "lambda_function.py"
  output_path = "lambda.zip"
}

resource "aws_lambda_function" "counter_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "pull-info-dev"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      ECS_CLUSTER       = aws_ecs_cluster.cluster.name
      TASK_DEFINITION   = aws_ecs_task_definition.task.family
      SUBNET_ID         = local.subnet_id
      SECURITY_GROUP_ID = aws_security_group.fargate_sg.id
    }
  }
}

output "ecr_repository_url" {
  value = aws_ecr_repository.repo.repository_url
}