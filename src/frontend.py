import json
import os

def lambda_handler(event, context):
    # Get the API Gateway URL from the event headers
    host = event.get('headers', {}).get('Host', 'unknown-host')
    api_gateway_url = f"https://{host}"
    
    # Read the HTML template and inject the API URL
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QRFormify - Create QR Code Forms</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
            color: white;
        }

        header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }

        .hero {
            background: white;
            padding: 60px 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
            margin-bottom: 40px;
        }

        .hero h2 {
            font-size: 2.5rem;
            margin-bottom: 20px;
            color: #333;
        }

        .hero p {
            font-size: 1.2rem;
            margin-bottom: 30px;
            color: #666;
        }

        .btn {
            display: inline-block;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            margin: 5px;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .form-builder {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 40px;
            display: none;
        }

        .form-section {
            margin-bottom: 30px;
        }

        .form-section label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
        }

        .form-section input,
        .form-section textarea,
        .form-section select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        .form-section input:focus,
        .form-section textarea:focus,
        .form-section select:focus {
            outline: none;
            border-color: #667eea;
        }

        .form-section small {
            display: block;
            margin-top: 5px;
            color: #888;
            font-size: 14px;
        }

        .form-actions {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 30px;
        }

        .success-message {
            background: #28a745;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
        }

        .error-message {
            background: #dc3545;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
        }

        .qr-result {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
            display: none;
        }

        #qr-code-container {
            margin: 30px 0;
            display: flex;
            justify-content: center;
        }

        #qr-code-container img {
            max-width: 300px;
            border: 5px solid #667eea;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }

            header h1 {
                font-size: 2rem;
            }

            .hero {
                padding: 30px 20px;
            }

            .hero h2 {
                font-size: 1.8rem;
            }

            .form-builder {
                padding: 20px;
            }

            .form-actions {
                flex-direction: column;
            }

            .btn {
                width: 100%;
                text-align: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1><i class="fas fa-qrcode"></i> QRFormify</h1>
            <p>Create beautiful forms with QR codes</p>
        </header>

        <!-- Landing Page -->
        <div id="landing-page">
            <div class="hero">
                <h2>Generate QR Codes, Design Forms, Collect Data</h2>
                <p>Create custom forms, generate QR codes, and collect responses with email notifications.</p>
                <button id="create-form-btn" class="btn btn-primary">
                    <i class="fas fa-plus"></i> Create New Form
                </button>
            </div>
        </div>

        <!-- Form Creation Page -->
        <div id="form-creation" class="form-builder">
            <h2><i class="fas fa-edit"></i> Create Your Form</h2>
            
            <div class="form-section">
                <label for="form-name">Form Name:</label>
                <input type="text" id="form-name" placeholder="Enter form name" required>
            </div>

            <div class="form-section">
                <label for="creator-email">Your Email:</label>
                <input type="email" id="creator-email" placeholder="your.email@example.com" required>
                <small>You'll receive submissions and a magic link to view all responses</small>
            </div>

            <div class="form-section">
                <h3><i class="fas fa-list"></i> Form Fields</h3>
                <div id="form-fields"></div>
                <button id="add-field-btn" class="btn btn-primary">
                    <i class="fas fa-plus"></i> Add Text Field
                </button>
            </div>

            <div class="form-actions">
                <button id="save-form-btn" class="btn btn-primary">
                    <i class="fas fa-save"></i> Create Form & Generate QR
                </button>
                <button id="back-to-landing" class="btn">
                    <i class="fas fa-arrow-left"></i> Back
                </button>
            </div>
        </div>

        <!-- QR Code Display -->
        <div id="qr-display" class="qr-result">
            <h2><i class="fas fa-check-circle"></i> Form Created Successfully!</h2>
            <div id="qr-code-container"></div>
            <div id="form-details"></div>
            <p class="success-message">
                <i class="fas fa-envelope"></i> 
                A confirmation email with your QR code and magic link has been sent to your email address.
            </p>
            <button id="create-another" class="btn btn-primary">
                <i class="fas fa-plus"></i> Create Another Form
            </button>
        </div>

        <!-- Messages -->
        <div id="success-message" style="display: none;"></div>
        <div id="error-message" style="display: none;"></div>
    </div>

    <script>
        const API_BASE_URL = '{api_gateway_url}';
        let formFields = [];
        let fieldCounter = 0;

        // Event handlers
        document.getElementById('create-form-btn').addEventListener('click', showFormCreation);
        document.getElementById('back-to-landing').addEventListener('click', showLanding);
        document.getElementById('create-another').addEventListener('click', showLanding);
        document.getElementById('add-field-btn').addEventListener('click', addField);
        document.getElementById('save-form-btn').addEventListener('click', createForm);

        function showLanding() {
            document.getElementById('landing-page').style.display = 'block';
            document.getElementById('form-creation').style.display = 'none';
            document.getElementById('qr-display').style.display = 'none';
            resetForm();
        }

        function showFormCreation() {
            document.getElementById('landing-page').style.display = 'none';
            document.getElementById('form-creation').style.display = 'block';
            document.getElementById('qr-display').style.display = 'none';
        }

        function showQRDisplay() {
            document.getElementById('landing-page').style.display = 'none';
            document.getElementById('form-creation').style.display = 'none';
            document.getElementById('qr-display').style.display = 'block';
        }

        function addField() {
            const fieldId = `field_${++fieldCounter}`;
            const field = {
                id: fieldId,
                type: 'text',
                label: `Field ${fieldCounter}`,
                placeholder: '',
                required: false
            };

            formFields.push(field);
            renderFormFields();
        }

        function renderFormFields() {
            const container = document.getElementById('form-fields');
            container.innerHTML = '';

            formFields.forEach((field, index) => {
                const fieldHtml = `
                    <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <h4>${field.label}</h4>
                            <button type="button" onclick="removeField(${index})" style="background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <div>
                                <label>Field Label:</label>
                                <input type="text" value="${field.label}" onchange="updateField(${index}, 'label', this.value)">
                            </div>
                            <div>
                                <label>Placeholder:</label>
                                <input type="text" value="${field.placeholder}" onchange="updateField(${index}, 'placeholder', this.value)">
                            </div>
                        </div>
                        <div style="margin-top: 10px;">
                            <label>
                                <input type="checkbox" ${field.required ? 'checked' : ''} onchange="updateField(${index}, 'required', this.checked)">
                                Required Field
                            </label>
                        </div>
                    </div>
                `;
                container.innerHTML += fieldHtml;
            });
        }

        function updateField(index, property, value) {
            if (formFields[index]) {
                formFields[index][property] = value;
            }
        }

        function removeField(index) {
            formFields.splice(index, 1);
            renderFormFields();
        }

        function resetForm() {
            document.getElementById('form-name').value = '';
            document.getElementById('creator-email').value = '';
            formFields = [];
            fieldCounter = 0;
            renderFormFields();
        }

        async function createForm() {
            const formName = document.getElementById('form-name').value.trim();
            const email = document.getElementById('creator-email').value.trim();

            if (!formName || !email || formFields.length === 0) {
                showError('Please fill in all fields and add at least one form field');
                return;
            }

            if (!isValidEmail(email)) {
                showError('Please enter a valid email address');
                return;
            }

            const formData = {
                formName: formName,
                email: email,
                fields: formFields
            };

            try {
                const response = await fetch(`${API_BASE_URL}/api/forms`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                const result = await response.json();

                if (response.ok) {
                    displayQRCode(result);
                    showSuccess('Form created successfully! Check your email for the QR code and magic link.');
                } else {
                    throw new Error(result.error || 'Failed to create form');
                }
            } catch (error) {
                showError(`Error creating form: ${error.message}`);
            }
        }

        function displayQRCode(formData) {
            document.getElementById('qr-code-container').innerHTML = 
                `<img src="data:image/png;base64,${formData.qrCodeBase64}" alt="QR Code">`;
            
            document.getElementById('form-details').innerHTML = `
                <div style="text-align: left; margin: 20px 0;">
                    <p><strong>Form URL:</strong> <a href="${formData.formUrl}" target="_blank">${formData.formUrl}</a></p>
                    <p><strong>View Submissions:</strong> <a href="${formData.viewSubmissionsUrl}" target="_blank">Magic Link</a></p>
                </div>
            `;
            
            showQRDisplay();
        }

        function isValidEmail(email) {
            const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
            return emailRegex.test(email);
        }

        function showError(message) {
            const errorDiv = document.getElementById('error-message');
            errorDiv.innerHTML = `<div class="error-message"><i class="fas fa-exclamation-triangle"></i> ${message}</div>`;
            errorDiv.style.display = 'block';
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }

        function showSuccess(message) {
            const successDiv = document.getElementById('success-message');
            successDiv.innerHTML = `<div class="success-message"><i class="fas fa-check-circle"></i> ${message}</div>`;
            successDiv.style.display = 'block';
            setTimeout(() => {
                successDiv.style.display = 'none';
            }, 5000);
        }

        // Handle URL routing for form display
        if (window.location.pathname.includes('/form/')) {
            const formId = window.location.pathname.split('/form/')[1];
            loadForm(formId);
        }

        async function loadForm(formId) {
            try {
                const response = await fetch(`${API_BASE_URL}/api/forms/${formId}`);
                const formData = await response.json();

                if (response.ok) {
                    renderFormForSubmission(formData);
                } else {
                    showError('Form not found');
                }
            } catch (error) {
                showError(`Error loading form: ${error.message}`);
            }
        }

        function renderFormForSubmission(formData) {
            document.body.innerHTML = `
                <div class="container">
                    <header>
                        <h1><i class="fas fa-qrcode"></i> QRFormify</h1>
                        <p>Form Submission</p>
                    </header>
                    <div class="hero">
                        <h2>${formData.formName}</h2>
                        <form id="submission-form">
                            ${formData.fields.map(field => `
                                <div class="form-section">
                                    <label for="${field.id}">${field.label}${field.required ? ' *' : ''}</label>
                                    <input type="${field.type}" id="${field.id}" name="${field.id}" placeholder="${field.placeholder}" ${field.required ? 'required' : ''}>
                                </div>
                            `).join('')}
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-paper-plane"></i> Submit Form
                            </button>
                        </form>
                    </div>
                </div>
            `;

            document.getElementById('submission-form').addEventListener('submit', (e) => {
                e.preventDefault();
                submitForm(formData.formId, formData.fields);
            });
        }

        async function submitForm(formId, fields) {
            const formData = new FormData(document.getElementById('submission-form'));
            const responses = {};

            fields.forEach(field => {
                responses[field.id] = formData.get(field.id) || '';
            });

            try {
                const response = await fetch(`${API_BASE_URL}/api/forms/${formId}/submit`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ responses })
                });

                const result = await response.json();

                if (response.ok) {
                    alert('Form submitted successfully! Thank you for your response.');
                    document.getElementById('submission-form').reset();
                } else {
                    throw new Error(result.error || 'Failed to submit form');
                }
            } catch (error) {
                alert(`Error submitting form: ${error.message}`);
            }
        }
    </script>
</body>
</html>"""

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, OPTIONS'
        },
        'body': html_content.replace('{api_gateway_url}', api_gateway_url + '/dev')
    }
