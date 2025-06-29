import json
import boto3
import os
from decimal import Decimal
from botocore.exceptions import ClientError

# Custom JSON encoder for DynamoDB Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

dynamodb = boto3.resource('dynamodb')
forms_table = dynamodb.Table(os.environ['FORMS_TABLE'])

def lambda_handler(event, context):
    try:
        # Get form ID from path parameters
        form_id = event['pathParameters']['formId']
        
        # Get form from DynamoDB
        response = forms_table.get_item(
            Key={'formId': form_id}
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS'
                },
                'body': json.dumps({'error': 'Form not found'})
            }
        
        form = response['Item']
        
        # Check if form is active
        if not form.get('isActive', True):
            return {
                'statusCode': 410,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS'
                },
                'body': json.dumps({'error': 'Form is no longer active'})
            }
        
        # Return form data (excluding sensitive information)
        form_data = {
            'formId': form['formId'],
            'formName': form['formName'],
            'fields': form['fields'],
            'createdAt': form['createdAt'],
            'submissionCount': form.get('submissionCount', 0)
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps(form_data, cls=DecimalEncoder)
        }
        
    except ClientError as e:
        print(f"DynamoDB error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps({'error': 'Database error'})
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }
