import os
import boto3

ecs = boto3.client('ecs')

CLUSTER_NAME = os.environ.get('ECS_CLUSTER')
TASK_DEF = os.environ.get('TASK_DEFINITION')
SUBNET_ID = os.environ.get('SUBNET_ID')
SECURITY_GROUP_ID = os.environ.get('SECURITY_GROUP_ID')

def lambda_handler(event, context):
    trigger = event.get("trigger", "").upper()
    
    if trigger == "START":
        response = ecs.run_task(
            cluster=CLUSTER_NAME,
            taskDefinition=TASK_DEF,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [SUBNET_ID],
                    'securityGroups': [SECURITY_GROUP_ID],
                    'assignPublicIp': 'ENABLED'
                }
            }
        )
        task_arn = response['tasks'][0]['taskArn']
        print(f"Started task ARN: {task_arn}")
        return {"statusCode": 200, "body": f"Fargate Task started: {task_arn}"}
        
    elif trigger == "END":
        tasks = ecs.list_tasks(cluster=CLUSTER_NAME, desiredStatus='RUNNING')['taskArns']
        pending = ecs.list_tasks(cluster=CLUSTER_NAME, desiredStatus='PENDING')['taskArns']
        all_tasks = tasks + pending
        
        if not all_tasks:
            return {"statusCode": 200, "body": "No running or pending tasks found."}
            
        for task_arn in all_tasks:
            ecs.stop_task(cluster=CLUSTER_NAME, task=task_arn, reason='Killed by Lambda END trigger')
        return {"statusCode": 200, "body": f"Task(s) stopped: {all_tasks}"}

    return {"statusCode": 400, "body": "Invalid trigger. Use {'trigger': 'START'} or {'trigger': 'END'}."}