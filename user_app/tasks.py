import boto3
import os
import json
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from datetime import datetime

class AsyncTaskManager:
    def __init__(self, task_id=None):
        self.sqs = boto3.client('sqs',
                    aws_access_key_id=os.environ.get('AWS_GAMES_KEY'),
                    aws_secret_access_key=os.environ.get('AWS_GAMES_SECRET'),
                    region_name='us-west-2'
)
        self.queue_url = os.environ.get('FIELD_CSV_TASK_Q')
        
        self.dynamodb = boto3.resource('dynamodb',
                    aws_access_key_id=os.environ.get('AWS_GAMES_KEY'),
                    aws_secret_access_key=os.environ.get('AWS_GAMES_SECRET'),
                    region_name='us-west-2')
        self.table = self.dynamodb.Table('TASK_STATUS_TABLE')
        
        if task_id:
            self.task_id = task_id
        else:
            self.task_id = None
        
    def start_async_task(self, task_type, task_data):
        """Initiates an async task and returns a task ID"""
        
        message = {
            'task_type': task_type,
            'task_data': task_data,
            'status': 'PENDING'
        }
        
        try:
            response = self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message),
                 MessageAttributes={
                'token': {
                    'DataType': 'String',
                    'StringValue': task_data.get('token', '')
                }
            }
                
            )
            self.task_id = response['MessageId']
            return response['MessageId']
        except ClientError as e:
            print(f"Error starting async task: {e}")
            raise

    def update_progress(self, progress, status='IN_PROGRESS', meta_data={}):
        """Updates task progress in DynamoDB"""
        timestamp = datetime.now().isoformat()
        try:
        # Write both current and historical records
            with self.table.batch_writer() as batch:
            # Current status record - always at known position
                batch.put_item(
                    Item={
                        'pk': self.task_id,
                        'sk': 'CURRENT',  # Fixed sort key for current status
                        'progress': progress,
                        'status': status,
                        'meta_data': meta_data,
                        'updated_at': timestamp
                }
            )
            
                # Historical record
                batch.put_item(
                    Item={
                        'pk': self.task_id,
                        'sk': f'STATUS#{timestamp}',  # Historical sort key
                        'progress': progress,
                        'status': status,
                        'meta_data': meta_data,
                        'updated_at': timestamp
                    }
                )
                return True
        except ClientError as e:
            print(f"Error updating progress: {e}")
            raise