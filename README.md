# QRFormify

A serverless form builder that generates QR codes for easy form sharing and data collection. Users can create custom forms, share them via QR codes, and view submissions through secure magic links.

## What This Application Does

QRFormify allows you to:
1. Create custom forms with various field types
2. Generate QR codes that link directly to your forms
3. Collect form submissions from users who scan the QR code
4. Receive email notifications when someone submits your form
5. View all submissions through a secure magic link sent to your email

## How AWS Lambda is Used in This Project

This application runs entirely on AWS Lambda functions - there are no traditional servers involved. Here's how Lambda handles different parts of the application:

### The Five Lambda Functions

**1. Form Creation (CreateFormFunction)**
When you create a new form, this Lambda function:
- Takes your form fields and generates a unique ID
- Creates a QR code image that contains the form URL
- Saves the form definition to DynamoDB
- Sends you an email with the QR code and magic link
- Returns the QR code data to display in your browser

**2. Form Display (GetFormFunction)**
When someone scans your QR code, this Lambda function:
- Receives the form ID from the URL
- Looks up the form definition in DynamoDB
- Returns the form structure so it can be displayed to the user

**3. Form Submission (SubmitFormFunction)**
When someone fills out and submits your form, this Lambda function:
- Validates the submitted data
- Saves the submission to DynamoDB
- Updates a counter showing how many submissions you've received
- Sends you an email notification about the new submission

**4. Viewing Submissions (ViewSubmissionsFunction)**
When you click the magic link in your email, this Lambda function:
- Verifies that you have permission to view the submissions
- Retrieves all submissions for your form from DynamoDB
- Returns the data in a format that can be displayed on a webpage

**5. Web Interface (FrontendFunction)**
This is the most unusual part - instead of hosting the website on a separate service, this Lambda function:
- Serves the entire web application (HTML, CSS, and JavaScript)
- Handles the initial page load when you visit the application
- Contains all the code for the form builder interface

### Why Lambda Works Well Here

Lambda functions are a good fit for this application because:

- **Event-driven**: Each function only runs when something specific happens (form creation, QR scan, submission, etc.)
- **No server maintenance**: AWS handles all the underlying infrastructure
- **Automatic scaling**: If many people scan your QR codes at once, AWS automatically creates more function instances
- **Cost-effective**: You only pay when the functions actually run

### How Lambda Connects to Other AWS Services

Each Lambda function uses AWS's SDK (boto3) to interact with other services:

- **DynamoDB**: Functions read and write form data using `boto3.resource('dynamodb')`
- **SES (Email)**: Functions send emails using `boto3.client('ses')`
- **API Gateway**: All functions are triggered by HTTP requests through API Gateway

The functions are written in Python and follow a standard pattern:
```python
def lambda_handler(event, context):
    # Get request data from the 'event' parameter
    # Do the actual work (save data, send email, etc.)
    # Return a response
```

## Technical Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Lambda        │
│   (Lambda)      │───▶│                 │───▶│   Functions     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐             │
│   Amazon SES    │    │   DynamoDB      │◀────────────┘
│   (Email)       │    │   (Database)    │
└─────────────────┘    └─────────────────┘
```

### AWS Services Used
- **AWS Lambda**: All application logic (5 functions)
- **API Gateway**: HTTP endpoints and routing
- **DynamoDB**: Database for forms and submissions
- **SES**: Email notifications
- **IAM**: Permissions management
- **SAM**: Deployment and infrastructure management


## Prerequisites 📋

- AWS CLI installed and configured
- AWS SAM CLI installed
- Python 3.9+
- An AWS account with appropriate permissions

### Installation

1. **Install AWS CLI**:
   ```bash
   # macOS
   curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
   sudo installer -pkg AWSCLIV2.pkg -target /
   
   # Linux
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

2. **Install SAM CLI**:
   ```bash
   # macOS
   brew install aws-sam-cli
   
   # Linux
   pip install aws-sam-cli
   ```

3. **Configure AWS credentials**:
   ```bash
   aws configure
   ```

## Quick Start 🚀

1. **Clone/Download the project**:
   ```bash
   cd QRFormify
   ```

2. **Deploy the application**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Follow the deployment prompts** and note the output URLs.

4. **Verify email address in Amazon SES** (required for email functionality).

## Manual Deployment 🔧

If you prefer to deploy manually:

1. **Install dependencies**:
   ```bash
   pip install -r src/requirements.txt -t src/
   ```

2. **Build the SAM application**:
   ```bash
   sam build
   ```

3. **Deploy**:
   ```bash
   sam deploy --guided
   ```

4. **Update frontend configuration** and upload to S3.

## Usage 📱

### Creating a Form

1. Visit the QRFormify website
2. Click "Create New Form"
3. Fill in your email and form name
4. Add form fields using the field builder
5. Preview your form
6. Click "Create Form & Generate QR"
7. Your QR code will be generated and emailed to you

### Form Field Types

- **Text Input**: Single-line text
- **Email**: Email validation(removed)
- **Number**: Numeric input(removed)
- **Text Area**: Multi-line text(removed)
- **Dropdown**: Select from options(removed)
- **Radio Buttons**: Single choice from options(removed)
- **Checkboxes**: Multiple choice from options(removed)

### Viewing Submissions

- Use the magic link sent to your email
- View all form submissions in real-time
- Download submission data (future feature)

## Configuration ⚙️

### Email Setup

1. **Verify your email domain in Amazon SES**:
   ```bash
   aws ses verify-email-identity --email-address your-email@domain.com
   ```

2. **Update Lambda functions** to use your verified email domain.

### Custom Domain (Optional)

1. Set up a custom domain in Route 53
2. Configure CloudFront distribution
3. Update CORS settings

## API Endpoints 🔌

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/forms` | Create new form |
| GET | `/api/forms/{formId}` | Get form details |
| POST | `/api/forms/{formId}/submit` | Submit form response |
| GET | `/api/forms/{formId}/submissions` | View submissions (with magic token) |

## File Structure 📁

```
QRFormify/
├── template.yaml           # SAM template
├── samconfig.toml          # SAM configuration
├── deploy.sh              # Deployment script
├── README.md              # This file
├── src/                   # Lambda functions
│   ├── create_form.py     # Form creation
│   ├── get_form.py        # Form retrieval
│   ├── submit_form.py     # Form submission
│   ├── view_submissions.py # View submissions
│   └── requirements.txt   # Python dependencies
└── website/               # Frontend files
    ├── index.html         # Main HTML
    ├── styles.css         # Styling
    └── app.js            # JavaScript logic
```

## Environment Variables 🌍

The following environment variables are automatically set:

- `FORMS_TABLE`: DynamoDB table for forms
- `SUBMISSIONS_TABLE`: DynamoDB table for submissions
- `CORS_ORIGIN`: CORS configuration

## Security 🔒

- Magic links for secure submission viewing
- Input validation and sanitization
- AWS IAM roles with least privilege
- CORS protection
- Form data encryption at rest

## Troubleshooting 🔧

### Common Issues

1. **Email not sending**: Verify your email in Amazon SES
2. **CORS errors**: Check API Gateway CORS configuration
3. **Lambda timeout**: Increase timeout in template.yaml
4. **DynamoDB errors**: Check IAM permissions

### Logs and Monitoring

- View CloudWatch logs for Lambda functions
- Monitor API Gateway metrics
- Check DynamoDB metrics

## Cost Estimation 💰

QRFormify uses serverless architecture, so you only pay for what you use:

- **Lambda**: ~$0.20 per 1M requests
- **DynamoDB**: ~$1.25 per million read/write requests
- **S3**: ~$0.023 per GB storage
- **SES**: ~$0.10 per 1,000 emails

Estimated cost for 1,000 forms with 10,000 submissions: **~$5-10/month**

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License 📄

This project is licensed under the MIT License.

## Support 💬

For support and questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review AWS documentation

## Roadmap 🗺️

- [ ] Form analytics dashboard
- [ ] CSV export functionality
- [ ] Custom branding options
- [ ] Form templates
- [ ] Integration with external services
- [ ] Advanced field validation
- [ ] Multi-language support

## Credits 👏

Built with:
- AWS Lambda
- AWS DynamoDB
- AWS S3
- AWS SES
- AWS API Gateway
- QR Code generation libraries
- Font Awesome icons

---

**Happy form building with QRFormify!** 🎉
