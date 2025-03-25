import boto3
from botocore.exceptions import ClientError
import os
import hmac
import base64
import hashlib


ACCESS_KEY = os.environ.get('AWS_GAMES_KEY')
ACCESS_SECRET = os.environ.get('AWS_GAMES_SECRET')
REGION_NAME = 'us-west-2'


class CognitoService:
    def __init__(self, username=None, password=None):
        self.client = boto3.client('cognito-idp',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=ACCESS_SECRET,
                    region_name=REGION_NAME)
        self.user_pool_id = os.environ.get('COGNITO_USER_POOL_ID')
        self.client_id = os.environ.get('COGNITO_CLIENT_ID')
        self.client_secret = os.environ.get('COGNITO_CLIENT_SECRET') 
        self.username = username if username else os.environ.get('COGNITO_SERVICE_USERNAME')
        self.password = password if password else os.environ.get('COGNITO_SERVICE_PASSWORD')


    def get_secret_hash(self):
        """Calculate the secret hash for Cognito authentication"""
        message = self.username + self.client_id
        dig = hmac.new(
            key=self.client_secret.encode('utf-8'),
            msg=message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(dig).decode()
    
    def setup_service_account(self):
        """Set up service account with permanent password"""
        try:
            self.client.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=self.username,
                Password=self.password,
                Permanent=True
            )
            return True
        except self.client.exceptions.ClientError as e:
            print(f"Error setting up service account: {e}")
            raise

    def test_service_account(self):
        """Test if service account credentials work"""
        try:
            response = self.client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': self.username,
                    'PASSWORD': self.password,
                    'SECRET_HASH': self.get_secret_hash()
                },
                ClientId=self.client_id
            )
            print("Service account authentication successful")
            return True
        except self.client.exceptions.ClientError as e:
            print(f"Service account authentication failed: {e}")
            return False

    def get_token(self):
        try:
            # Get Access token for Lambda access
            auth_response = self.client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': self.username,
                    'PASSWORD': self.password,
                    'SECRET_HASH': self.get_secret_hash()
                },
                ClientId=self.client_id
            )
            
            return auth_response['AuthenticationResult']['AccessToken']
        except ClientError as e:
            print(f"Error getting Cognito token: {e}")
            raise

class s3Client:
    def __init__(self, bucket, key):
        self.s3_client = boto3.client('s3',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=ACCESS_SECRET,
            region_name=REGION_NAME
        )

        self.bucket = bucket
        self.key = key

    def get_signed_url(self):
        try:
            print ('KEY ', self.bucket, self.key)
            if self.file_exists():
                url = self.s3_client.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={
                        'Bucket': self.bucket,
                        'Key': self.key,
                        'ResponseContentType': 'text/csv'
                    },
                    ExpiresIn=86400
                )

                return url
            else:
                return None
        except Exception as e:
            print ('error in signed url services: ', e)
            return None


    def file_exists(self):
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=self.key)
            return True
        except self.s3_client.exceptions.ClientError as e:
            return False


class DynamoStatsTable:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=ACCESS_SECRET,
            region_name=REGION_NAME
        )

        self.table = self.dynamodb.Table('golferStats')


    def upsert_item(self, item_data, pk=None, sk=None):
        """
        Updates existing item or creates new one if it doesn't exist
    
        Args:
            table: DynamoDB table object
            pk: partition key value
            sk: sort key value
            item_data: dictionary of attributes to update/create
        """
        if not pk:
            pk = item_data.get('pk', None)
        if not sk:
            sk = item_data.get('sk', None)

        if not pk or not sk:
            print("Error: pk and sk must be provided")
            raise

        update_expr = "SET "
        expr_values = {}
        expr_names = {}
        
        for i, (key, value) in enumerate(item_data.items()):
            attr_name = f"#attr{i}"
            attr_value = f":val{i}"
            
            update_expr += f"{attr_name} = {attr_value}"
            if i < len(item_data) - 1:
                update_expr += ", "
                
            expr_names[attr_name] = key
            expr_values[attr_value] = value

        try:
            response = self.table.update_item(
                Key={
                    'pk': pk,
                    'sk': sk
                },
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_names,
                ExpressionAttributeValues=expr_values,
                ReturnValues="ALL_NEW"
            )
            return response.get('Attributes')
        except Exception as e:
            print(f"Error upserting item: {e}")
            raise

    def batch_upsert(self, items):
        """
        Batch upsert items to DynamoDB table
        
        Args:
            table: DynamoDB table object
            items: list of dictionaries, each containing:
                - pk: partition key value
                - sk: sort key value
                - data: dictionary of attributes to update/create
        Returns:
            dict with 'processed' and 'failed' items
        """
        def chunks(lst, n):
            """Split list into chunks of size n"""
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        results = {
            'processed': [],
            'failed': []
        }

        # Process items in chunks of 25 (DynamoDB batch limit)
        for chunk in chunks(items, 25):
            batch_requests = []
            
            for item in chunk:
                pk = item['pk']
                sk = item['sk']
                #item_data = item['data']
                item_data = {k: v for k, v in item.items() if k not in ['pk', 'sk']}
                
                # Prepare the update expression and attributes
                update_expr = "SET "
                expr_values = {}
                expr_names = {}
                
                for i, (key, value) in enumerate(item_data.items()):
                    attr_name = f"#attr{i}"
                    attr_value = f":val{i}"
                    
                    update_expr += f"{attr_name} = {attr_value}"
                    if i < len(item_data) - 1:
                        update_expr += ", "
                        
                    expr_names[attr_name] = key
                    expr_values[attr_value] = value

                try:
                    # Perform individual update_item within the batch
                    response = self.table.update_item(
                        Key={
                            'pk': pk,
                            'sk': sk
                        },
                        UpdateExpression=update_expr,
                        ExpressionAttributeNames=expr_names,
                        ExpressionAttributeValues=expr_values,
                        ReturnValues="ALL_NEW"
                    )
                    results['processed'].append({
                        'pk': pk,
                        'sk': sk,
                        'data': response.get('Attributes')
                    })
                except Exception as e:
                    print(f"Error processing item {pk}/{sk}: {e}")
                    results['failed'].append({
                        'pk': pk,
                        'sk': sk,
                        'data': item_data,
                        'error': str(e)
                    })

        return results
    
    def get_item(self, pk, sk):
        """
        Get item from DynamoDB table

        Args:
            table: DynamoDB table object
            pk: partition key value
            sk: sort key value
        """
        try:
            response = self.table.get_item(
                Key={
                    'pk': pk,
                    'sk': sk
                }
            )
            return response.get('Item')
        except Exception as e:
            print(f"Error getting item: {e}")
            raise


    

