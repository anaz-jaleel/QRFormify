import json
import boto3
import os
import uuid
from datetime import datetime
from decimal import Decimal
from botocore.exceptions import ClientError

# Custom JSON encoder for DynamoDB Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')
forms_table = dynamodb.Table(os.environ['FORMS_TABLE'])
submissions_table = dynamodb.Table(os.environ['SUBMISSIONS_TABLE'])

def lambda_handler(event, context):
    try:
        # Get form ID from path parameters
        form_id = event['pathParameters']['formId']
        
        # Parse request body
        body = json.loads(event['body'])
        
        if 'responses' not in body:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': 'Missing required field: responses'}, cls=DecimalEncoder)
            }
        
        # Get form details
        form_response = forms_table.get_item(
            Key={'formId': form_id}
        )
        
        if 'Item' not in form_response:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': 'Form not found'}, cls=DecimalEncoder)
            }
        
        form = form_response['Item']
        
        # Check if form is active
        if not form.get('isActive', True):
            return {
                'statusCode': 410,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': 'Form is no longer active'}, cls=DecimalEncoder)
            }
        
        # Validate submission against form fields
        form_fields = form['fields']
        responses = body['responses']
        
        # Check required fields
        for field in form_fields:
            field_id = field['id']
            if field.get('required', False) and (field_id not in responses or not responses[field_id]):
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'POST, OPTIONS'
                    },
                    'body': json.dumps({'error': f'Required field "{field["label"]}" is missing'})
                }
        
        # Create submission
        submission_id = str(uuid.uuid4())
        submission_data = {
            'submissionId': submission_id,
            'formId': form_id,
            'responses': responses,
            'submittedAt': datetime.utcnow().isoformat(),
            'ipAddress': event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'unknown')
        }
        
        # Save submission to DynamoDB
        submissions_table.put_item(Item=submission_data)
        
        # Update form submission count
        forms_table.update_item(
            Key={'formId': form_id},
            UpdateExpression='ADD submissionCount :inc',
            ExpressionAttributeValues={':inc': 1}
        )
        
        # Send notification email to form creator
        try:
            # Prepare submission summary for email
            submission_summary = []
            for field in form_fields:
                field_id = field['id']
                field_label = field['label']
                response_value = responses.get(field_id, 'No response')
                submission_summary.append(f"<strong>{field_label}:</strong> {response_value}")
            
            email_html = f"""
            <html>
            <body>
                <h2>New Form Submission Received</h2>
                <p><strong>Form:</strong> {form['formName']}</p>
                <p><strong>Submission ID:</strong> {submission_id}</p>
                <p><strong>Submitted At:</strong> {submission_data['submittedAt']}</p>
                
                <h3>Responses:</h3>
                <div>
                    {'<br>'.join(submission_summary)}
                </div>
                
                <p>You can view all submissions by clicking the magic link in your original form creation email.</p>
            </body>
            </html>
            """
            
            ses.send_email(
                Source='anazjaleel@gmail.com',  # Verified email address
                Destination={'ToAddresses': [form['email']]},
                Message={
                    'Subject': {'Data': f'New submission for "{form["formName"]}"'},
                    'Body': {
                        'Html': {'Data': email_html}
                    }
                }
            )
        except Exception as e:
            print(f"Failed to send notification email: {str(e)}")
            # Continue even if email fails
        
        return {
            'statusCode': 201,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'submissionId': submission_id,
                'message': 'Form submitted successfully'
            })
        }
        
    except ClientError as e:
        print(f"DynamoDB error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
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
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'error': 'Internal server error'}, cls=DecimalEncoder)
        }
