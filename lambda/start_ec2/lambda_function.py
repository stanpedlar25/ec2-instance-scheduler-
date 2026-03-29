import json
import boto3

# EC2 client for Europe (London) region
client = boto3.client('ec2', region_name='eu-west-2')

# Target instance ID - update this to your instance ID
instance_id = "i-024236f32f8f5c04c"

def lambda_handler(event, context):
    """
    Starts the EC2 instance. Triggered by EventBridge scheduled rule
    at 09:00 UTC Monday to Friday.
    """
    response = client.start_instances(
        InstanceIds=[instance_id]
    )

    current_state = response['StartingInstances'][0]['CurrentState']['Name']
    previous_state = response['StartingInstances'][0]['PreviousState']['Name']

    print(f"Instance {instance_id}: {previous_state} -> {current_state}")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'EC2 instance {instance_id} start initiated',
            'previousState': previous_state,
            'currentState': current_state
        })
    }
