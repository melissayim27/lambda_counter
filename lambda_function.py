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
        return {"statusCode": 200, "body": f"Fargate Task gestartet: {task_arn}"}
        
    elif trigger == "END":
        tasks = ecs.list_tasks(cluster=CLUSTER_NAME, family=TASK_DEF, desiredStatus='RUNNING')
        if not tasks['taskArns']:
            return {"statusCode": 200, "body": "Kein laufender Task zum Stoppen gefunden."}
            
        for task_arn in tasks['taskArns']:
            ecs.stop_task(cluster=CLUSTER_NAME, task=task_arn, reason='Gekillt durch Lambda END Trigger')
        return {"statusCode": 200, "body": f"Task(s) gestoppt: {tasks['taskArns']}"}

    return {"statusCode": 400, "body": "Ungueltiger Trigger. Nutzen Sie {'trigger': 'START'} oder {'trigger': 'END'}."}