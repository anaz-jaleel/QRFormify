#!/bin/bash

# QRFormify Deployment Script
set -e

echo "🚀 Starting QRFormify deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo -e "${RED}❌ SAM CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check AWS credentials
echo -e "${BLUE}🔍 Checking AWS credentials...${NC}"
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured. Please run 'aws configure'.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ AWS credentials configured${NC}"

# Get AWS account ID and region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${AWS_DEFAULT_REGION:-us-east-1}

echo -e "${BLUE}📍 Deploying to account: ${AWS_ACCOUNT_ID} in region: ${AWS_REGION}${NC}"

# Install Python dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
pip install -r src/requirements.txt -t src/ || {
    echo -e "${RED}❌ Failed to install Python dependencies${NC}"
    exit 1
}

# Build SAM application
echo -e "${BLUE}🔨 Building SAM application...${NC}"
sam build || {
    echo -e "${RED}❌ SAM build failed${NC}"
    exit 1
}

echo -e "${GREEN}✅ SAM build successful${NC}"

# Deploy SAM application
echo -e "${BLUE}🚢 Deploying SAM application...${NC}"
sam deploy --guided || {
    echo -e "${RED}❌ SAM deployment failed${NC}"
    exit 1
}

echo -e "${GREEN}✅ SAM deployment successful${NC}"

# Get the API Gateway endpoint
echo -e "${BLUE}🔍 Getting API Gateway endpoint...${NC}"
API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name qrformify \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text)

if [ -z "$API_ENDPOINT" ]; then
    echo -e "${RED}❌ Could not retrieve API endpoint${NC}"
    exit 1
fi

echo -e "${GREEN}✅ API Endpoint: ${API_ENDPOINT}${NC}"

# Get the S3 website URL
WEBSITE_URL=$(aws cloudformation describe-stacks \
    --stack-name qrformify \
    --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' \
    --output text)

if [ -z "$WEBSITE_URL" ]; then
    echo -e "${RED}❌ Could not retrieve website URL${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Website URL: ${WEBSITE_URL}${NC}"

# Update the JavaScript file with the correct API endpoint
echo -e "${BLUE}🔧 Updating frontend with API endpoint...${NC}"
sed -i.bak "s|https://your-api-gateway-url.amazonaws.com/dev|${API_ENDPOINT}|g" website/app.js

# Get S3 bucket name
S3_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name qrformify \
    --query 'Stacks[0].Resources[?LogicalResourceId==`WebsiteBucket`].PhysicalResourceId' \
    --output text)

if [ -z "$S3_BUCKET" ]; then
    echo -e "${RED}❌ Could not retrieve S3 bucket name${NC}"
    exit 1
fi

# Upload website files to S3
echo -e "${BLUE}📤 Uploading website files to S3...${NC}"
aws s3 sync website/ s3://${S3_BUCKET}/ --delete || {
    echo -e "${RED}❌ Failed to upload website files${NC}"
    exit 1
}

echo -e "${GREEN}✅ Website files uploaded successfully${NC}"

# Set up SES email verification (optional)
echo -e "${YELLOW}📧 Note: You need to verify 'noreply@qrformify.com' in Amazon SES to send emails.${NC}"
echo -e "${YELLOW}   Alternatively, update the email addresses in the Lambda functions to use a verified domain.${NC}"

echo ""
echo -e "${GREEN}🎉 QRFormify deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📱 Application URLs:${NC}"
echo -e "   Frontend: ${WEBSITE_URL}"
echo -e "   API: ${API_ENDPOINT}"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "1. Verify email address in Amazon SES for sending notifications"
echo "2. Update CORS settings if needed"
echo "3. Test form creation and QR code generation"
echo "4. Share the website URL to start using QRFormify!"
echo ""
echo -e "${GREEN}✨ Happy form building!${NC}"
