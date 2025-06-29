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
submissions_table = dynamodb.Table(os.environ['SUBMISSIONS_TABLE'])

def lambda_handler(event, context):
    try:
        # Get form ID from path parameters
        form_id = event['pathParameters']['formId']
        
        # Get magic token from query parameters
        query_params = event.get('queryStringParameters') or {}
        magic_token = query_params.get('token')
        
        if not magic_token:
            return {
                'statusCode': 401,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS'
                },
                'body': json.dumps({'error': 'Magic token required'}, cls=DecimalEncoder)
            }
        
        # Get form details and verify magic token
        form_response = forms_table.get_item(
            Key={'formId': form_id}
        )
        
        if 'Item' not in form_response:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS'
                },
                'body': json.dumps({'error': 'Form not found'}, cls=DecimalEncoder)
            }
        
        form = form_response['Item']
        
        # Verify magic token
        if form.get('magicToken') != magic_token:
            return {
                'statusCode': 403,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS'
                },
                'body': json.dumps({'error': 'Invalid magic token'}, cls=DecimalEncoder)
            }
        
        # Get all submissions for this form
        submissions_response = submissions_table.query(
            IndexName='FormIndex',
            KeyConditionExpression='formId = :formId',
            ExpressionAttributeValues={':formId': form_id},
            ScanIndexForward=False  # Sort by submission time descending
        )
        
        submissions = submissions_response.get('Items', [])
        
        # Format submissions for response
        formatted_submissions = []
        for submission in submissions:
            formatted_submission = {
                'submissionId': submission['submissionId'],
                'submittedAt': submission['submittedAt'],
                'responses': submission['responses'],
                'ipAddress': submission.get('ipAddress', 'unknown')
            }
            formatted_submissions.append(formatted_submission)
        
        # Prepare response data
        response_data = {
            'formId': form_id,
            'formName': form['formName'],
            'formFields': form['fields'],
            'createdAt': form['createdAt'],
            'totalSubmissions': len(formatted_submissions),
            'submissions': formatted_submissions
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps(response_data, cls=DecimalEncoder)
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
            'body': json.dumps({'error': 'Database error'}, cls=DecimalEncoder)
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
            'body': json.dumps({'error': 'Internal server error'}, cls=DecimalEncoder)
        }
