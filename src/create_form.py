import json
import boto3
import uuid
import qrcode
import io
import base64
from datetime import datetime
import os

dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')
forms_table = dynamodb.Table(os.environ['FORMS_TABLE'])

def lambda_handler(event, context):
    try:
        # Parse request body
        body = json.loads(event['body'])
        
        # Validate required fields
        if 'email' not in body or 'formName' not in body or 'fields' not in body:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': 'Missing required fields: email, formName, fields'})
            }
        
        # Generate unique form ID
        form_id = str(uuid.uuid4())
        
        # Create form URL for QR code
        # Get the API Gateway URL from environment or headers
        host = event.get('headers', {}).get('Host', 'unknown-host')
        api_gateway_url = f"https://{host}/dev"
        form_url = f"{api_gateway_url}/form/{form_id}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(form_url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        img_buffer = io.BytesIO()
        qr_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        qr_code_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Save form to DynamoDB
        form_data = {
            'formId': form_id,
            'email': body['email'],
            'formName': body['formName'],
            'fields': body['fields'],
            'qrCodeBase64': qr_code_base64,
            'formUrl': form_url,
            'createdAt': datetime.utcnow().isoformat(),
            'isActive': True,
            'submissionCount': 0
        }
        
        forms_table.put_item(Item=form_data)
        
        # Send email with QR code and magic link for viewing submissions
        magic_token = str(uuid.uuid4())
        
        # Store magic token for later verification
        forms_table.update_item(
            Key={'formId': form_id},
            UpdateExpression='SET magicToken = :token',
            ExpressionAttributeValues={':token': magic_token}
        )
        
        view_submissions_url = f"{form_url}/view?token={magic_token}"
        
        # Send email with QR code
        email_html = f"""
        <html>
        <body>
            <h2>Your QR Form has been created!</h2>
            <p><strong>Form Name:</strong> {body['formName']}</p>
            <p><strong>Form ID:</strong> {form_id}</p>
            
            <h3>QR Code:</h3>
            <img src="data:image/png;base64,{qr_code_base64}" alt="QR Code" style="max-width: 300px;">
            
            <h3>Form URL:</h3>
            <p><a href="{form_url}">{form_url}</a></p>
            
            <h3>View Submissions:</h3>
            <p><a href="{view_submissions_url}">Click here to view form submissions</a></p>
            
            <p>Share the QR code or URL to start collecting responses!</p>
        </body>
        </html>
        """
        
        try:
            ses.send_email(
                Source='anazjaleel@gmail.com',  # Verified email address
                Destination={'ToAddresses': [email]},
                Message={
                    'Subject': {'Data': f'QRFormify: Your form "{body["formName"]}" is ready!'},
                    'Body': {
                        'Html': {'Data': email_html}
                    }
                }
            )
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            # Continue even if email fails
        
        return {
            'statusCode': 201,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'formId': form_id,
                'qrCodeBase64': qr_code_base64,
                'formUrl': form_url,
                'viewSubmissionsUrl': view_submissions_url,
                'message': 'Form created successfully'
            })
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
            'body': json.dumps({'error': 'Internal server error'})
        }
