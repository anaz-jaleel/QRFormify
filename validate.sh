#!/bin/bash

# QRFormify Project Validation Script
echo "🔍 Validating QRFormify project structure..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track validation status
VALIDATION_PASSED=true

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1 (missing)${NC}"
        VALIDATION_PASSED=false
    fi
}

# Function to check if directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅ $1/ (directory)${NC}"
    else
        echo -e "${RED}❌ $1/ (missing directory)${NC}"
        VALIDATION_PASSED=false
    fi
}

echo -e "${BLUE}📁 Checking project structure...${NC}"

# Check root files
check_file "template.yaml"
check_file "samconfig.toml"
check_file "deploy.sh"
check_file "README.md"
check_file "validate.sh"

# Check source directory and files
check_dir "src"
check_file "src/create_form.py"
check_file "src/get_form.py"
check_file "src/submit_form.py"
check_file "src/view_submissions.py"
check_file "src/requirements.txt"

# Check website directory and files
check_dir "website"
check_file "website/index.html"
check_file "website/styles.css"
check_file "website/app.js"
check_file "website/error.html"

echo ""
echo -e "${BLUE}🔧 Checking file permissions...${NC}"

# Check if deploy script is executable
if [ -x "deploy.sh" ]; then
    echo -e "${GREEN}✅ deploy.sh is executable${NC}"
else
    echo -e "${YELLOW}⚠️  deploy.sh is not executable (run: chmod +x deploy.sh)${NC}"
fi

echo ""
echo -e "${BLUE}📋 Checking Python requirements...${NC}"

# Check Python requirements format
if [ -f "src/requirements.txt" ]; then
    echo -e "${GREEN}✅ requirements.txt found${NC}"
    echo "📦 Dependencies:"
    while IFS= read -r line; do
        if [[ ! -z "$line" && ! "$line" =~ ^# ]]; then
            echo "   - $line"
        fi
    done < "src/requirements.txt"
else
    echo -e "${RED}❌ requirements.txt missing${NC}"
    VALIDATION_PASSED=false
fi

echo ""
echo -e "${BLUE}🏗️  Checking SAM template...${NC}"

# Basic SAM template validation
if [ -f "template.yaml" ]; then
    if grep -q "AWS::Serverless" "template.yaml"; then
        echo -e "${GREEN}✅ SAM template format detected${NC}"
    else
        echo -e "${RED}❌ Invalid SAM template format${NC}"
        VALIDATION_PASSED=false
    fi
    
    # Check for required resources
    if grep -q "AWS::DynamoDB::Table" "template.yaml"; then
        echo -e "${GREEN}✅ DynamoDB tables defined${NC}"
    else
        echo -e "${RED}❌ DynamoDB tables missing${NC}"
        VALIDATION_PASSED=false
    fi
    
    if grep -q "AWS::Serverless::Function" "template.yaml"; then
        echo -e "${GREEN}✅ Lambda functions defined${NC}"
    else
        echo -e "${RED}❌ Lambda functions missing${NC}"
        VALIDATION_PASSED=false
    fi
    
    if grep -q "AWS::S3::Bucket" "template.yaml"; then
        echo -e "${GREEN}✅ S3 bucket defined${NC}"
    else
        echo -e "${RED}❌ S3 bucket missing${NC}"
        VALIDATION_PASSED=false
    fi
fi

echo ""
echo -e "${BLUE}🌐 Checking frontend files...${NC}"

# Check HTML structure
if [ -f "website/index.html" ]; then
    if grep -q "QRFormify" "website/index.html"; then
        echo -e "${GREEN}✅ HTML title and branding present${NC}"
    else
        echo -e "${YELLOW}⚠️  HTML branding may be missing${NC}"
    fi
    
    if grep -q "app.js" "website/index.html"; then
        echo -e "${GREEN}✅ JavaScript file linked${NC}"
    else
        echo -e "${RED}❌ JavaScript file not linked${NC}"
        VALIDATION_PASSED=false
    fi
    
    if grep -q "styles.css" "website/index.html"; then
        echo -e "${GREEN}✅ CSS file linked${NC}"
    else
        echo -e "${RED}❌ CSS file not linked${NC}"
        VALIDATION_PASSED=false
    fi
fi

# Check JavaScript API configuration
if [ -f "website/app.js" ]; then
    if grep -q "apiBaseUrl" "website/app.js"; then
        echo -e "${GREEN}✅ API configuration found in JavaScript${NC}"
    else
        echo -e "${RED}❌ API configuration missing in JavaScript${NC}"
        VALIDATION_PASSED=false
    fi
fi

echo ""
echo -e "${BLUE}📊 Project Statistics:${NC}"

# Count files and lines
TOTAL_FILES=$(find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" -o -name "*.yaml" -o -name "*.md" \) | wc -l)
TOTAL_LINES=$(find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.html" -o -name "*.css" -o -name "*.yaml" \) -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")

echo "📁 Total project files: $TOTAL_FILES"
echo "📝 Total lines of code: $TOTAL_LINES"

# File sizes
if command -v du &> /dev/null; then
    PROJECT_SIZE=$(du -sh . 2>/dev/null | cut -f1 || echo "unknown")
    echo "💾 Project size: $PROJECT_SIZE"
fi

echo ""
if [ "$VALIDATION_PASSED" = true ]; then
    echo -e "${GREEN}🎉 Project validation passed! QRFormify is ready to deploy.${NC}"
    echo ""
    echo -e "${BLUE}🚀 Next steps:${NC}"
    echo "1. Run './deploy.sh' to deploy the application"
    echo "2. Configure your AWS credentials if not already done"
    echo "3. Verify email address in Amazon SES"
    echo "4. Test the application functionality"
else
    echo -e "${RED}❌ Project validation failed. Please fix the issues above.${NC}"
    exit 1
fi
