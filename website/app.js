// QRFormify Application
class QRFormify {
    constructor() {
        this.apiBaseUrl = 'https://your-api-gateway-url.amazonaws.com/dev'; // Will be replaced after deployment
        this.formFields = [];
        this.fieldCounter = 0;
        this.init();
    }

    init() {
        this.bindEvents();
        this.handleRouting();
    }

    bindEvents() {
        // Navigation events
        document.getElementById('create-form-btn').addEventListener('click', () => this.showFormCreation());
        document.getElementById('back-to-landing').addEventListener('click', () => this.showLanding());
        document.getElementById('back-to-edit').addEventListener('click', () => this.showFormCreation());
        document.getElementById('create-another').addEventListener('click', () => this.showLanding());

        // Form building events
        document.getElementById('add-field-btn').addEventListener('click', () => this.showFieldTypeModal());
        document.getElementById('preview-form-btn').addEventListener('click', () => this.previewForm());
        document.getElementById('save-form-btn').addEventListener('click', () => this.createForm());
        document.getElementById('confirm-create').addEventListener('click', () => this.createForm());

        // Modal events
        document.getElementById('close-modal').addEventListener('click', () => this.hideFieldTypeModal());
        document.querySelectorAll('.field-type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.addField(e.target.closest('.field-type-btn').dataset.type));
        });

        // Form validation
        document.getElementById('form-name').addEventListener('input', this.validateForm.bind(this));
        document.getElementById('creator-email').addEventListener('input', this.validateForm.bind(this));
    }

    handleRouting() {
        const path = window.location.pathname;
        const urlParams = new URLSearchParams(window.location.search);
        
        if (path.includes('/form/')) {
            const formId = path.split('/form/')[1].split('/')[0];
            if (path.includes('/view')) {
                const token = urlParams.get('token');
                this.viewSubmissions(formId, token);
            } else {
                this.loadForm(formId);
            }
        } else {
            this.showLanding();
        }
    }

    // Navigation methods
    showLanding() {
        this.hideAllSections();
        document.getElementById('landing-page').style.display = 'block';
        this.resetForm();
    }

    showFormCreation() {
        this.hideAllSections();
        document.getElementById('form-creation').style.display = 'block';
    }

    showFormPreview() {
        this.hideAllSections();
        document.getElementById('form-preview').style.display = 'block';
    }

    showQRDisplay() {
        this.hideAllSections();
        document.getElementById('qr-display').style.display = 'block';
    }

    showFormDisplay() {
        this.hideAllSections();
        document.getElementById('form-display').style.display = 'block';
    }

    showSubmissionsView() {
        this.hideAllSections();
        document.getElementById('submissions-view').style.display = 'block';
    }

    hideAllSections() {
        const sections = ['landing-page', 'form-creation', 'form-preview', 'qr-display', 'form-display', 'submissions-view'];
        sections.forEach(section => {
            document.getElementById(section).style.display = 'none';
        });
    }

    // Form field management
    showFieldTypeModal() {
        document.getElementById('field-type-modal').style.display = 'flex';
    }

    hideFieldTypeModal() {
        document.getElementById('field-type-modal').style.display = 'none';
    }

    addField(type) {
        this.hideFieldTypeModal();
        
        const fieldId = `field_${++this.fieldCounter}`;
        const field = {
            id: fieldId,
            type: type,
            label: `${this.getFieldTypeLabel(type)} ${this.fieldCounter}`,
            placeholder: '',
            required: false,
            options: type === 'select' || type === 'radio' || type === 'checkbox' ? ['Option 1'] : []
        };

        this.formFields.push(field);
        this.renderFormFields();
    }

    getFieldTypeLabel(type) {
        const labels = {
            text: 'Text Field',
            email: 'Email Field',
            number: 'Number Field',
            textarea: 'Text Area',
            select: 'Dropdown',
            radio: 'Radio Button',
            checkbox: 'Checkbox'
        };
        return labels[type] || 'Field';
    }

    renderFormFields() {
        const container = document.getElementById('form-fields');
        container.innerHTML = '';

        this.formFields.forEach((field, index) => {
            const fieldHtml = this.createFieldEditor(field, index);
            container.appendChild(fieldHtml);
        });

        this.validateForm();
    }

    createFieldEditor(field, index) {
        const div = document.createElement('div');
        div.className = 'field-item';
        div.innerHTML = `
            <div class=\"field-header\">
                <h4><i class=\"fas fa-${this.getFieldIcon(field.type)}\"></i> ${field.label}</h4>
                <div class=\"field-controls\">
                    <button type=\"button\" class=\"btn btn-danger\" onclick=\"qrFormify.removeField(${index})\">
                        <i class=\"fas fa-trash\"></i>
                    </button>
                </div>
            </div>
            <div class=\"field-config\">
                <div>
                    <label>Field Label:</label>
                    <input type=\"text\" value=\"${field.label}\" onchange=\"qrFormify.updateField(${index}, 'label', this.value)\">
                </div>
                <div>
                    <label>Placeholder:</label>
                    <input type=\"text\" value=\"${field.placeholder}\" onchange=\"qrFormify.updateField(${index}, 'placeholder', this.value)\">
                </div>
                <div class=\"checkbox-group\">
                    <input type=\"checkbox\" ${field.required ? 'checked' : ''} onchange=\"qrFormify.updateField(${index}, 'required', this.checked)\">
                    <label>Required Field</label>
                </div>
                ${this.needsOptions(field.type) ? this.createOptionsEditor(field, index) : ''}
            </div>
        `;
        return div;
    }

    getFieldIcon(type) {
        const icons = {
            text: 'font',
            email: 'envelope',
            number: 'hashtag',
            textarea: 'align-left',
            select: 'list',
            radio: 'dot-circle',
            checkbox: 'check-square'
        };
        return icons[type] || 'question';
    }

    needsOptions(type) {
        return ['select', 'radio', 'checkbox'].includes(type);
    }

    createOptionsEditor(field, fieldIndex) {
        return `
            <div class=\"options-list\">
                <label>Options:</label>
                <div id=\"options-${fieldIndex}\">
                    ${field.options.map((option, optIndex) => `
                        <div class=\"option-item\">
                            <input type=\"text\" value=\"${option}\" onchange=\"qrFormify.updateOption(${fieldIndex}, ${optIndex}, this.value)\">
                            <button type=\"button\" class=\"btn btn-danger\" onclick=\"qrFormify.removeOption(${fieldIndex}, ${optIndex})\">
                                <i class=\"fas fa-times\"></i>
                            </button>
                        </div>
                    `).join('')}
                </div>
                <button type=\"button\" class=\"btn btn-secondary\" onclick=\"qrFormify.addOption(${fieldIndex})\">
                    <i class=\"fas fa-plus\"></i> Add Option
                </button>
            </div>
        `;
    }

    updateField(index, property, value) {
        if (this.formFields[index]) {
            this.formFields[index][property] = value;
            this.validateForm();
        }
    }

    removeField(index) {
        this.formFields.splice(index, 1);
        this.renderFormFields();
    }

    addOption(fieldIndex) {
        if (this.formFields[fieldIndex]) {
            this.formFields[fieldIndex].options.push(`Option ${this.formFields[fieldIndex].options.length + 1}`);
            this.renderFormFields();
        }
    }

    updateOption(fieldIndex, optionIndex, value) {
        if (this.formFields[fieldIndex] && this.formFields[fieldIndex].options[optionIndex] !== undefined) {
            this.formFields[fieldIndex].options[optionIndex] = value;
        }
    }

    removeOption(fieldIndex, optionIndex) {
        if (this.formFields[fieldIndex] && this.formFields[fieldIndex].options.length > 1) {
            this.formFields[fieldIndex].options.splice(optionIndex, 1);
            this.renderFormFields();
        }
    }

    validateForm() {
        const formName = document.getElementById('form-name').value.trim();
        const creatorEmail = document.getElementById('creator-email').value.trim();
        const hasFields = this.formFields.length > 0;

        const isValid = formName && creatorEmail && this.isValidEmail(creatorEmail) && hasFields;
        
        document.getElementById('preview-form-btn').disabled = !isValid;
        document.getElementById('save-form-btn').disabled = !isValid;
        
        return isValid;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
        return emailRegex.test(email);
    }

    // Form preview
    previewForm() {
        if (!this.validateForm()) {
            this.showError('Please fill in all required fields and add at least one form field');
            return;
        }

        const formName = document.getElementById('form-name').value;
        const previewHtml = this.generateFormHTML(formName, this.formFields, true);
        
        document.getElementById('preview-content').innerHTML = previewHtml;
        this.showFormPreview();
    }

    generateFormHTML(formName, fields, isPreview = false) {
        const formClass = isPreview ? 'form-container' : 'form-container';
        return `
            <div class=\"${formClass}\">
                <h2>${formName}</h2>
                <form id=\"${isPreview ? 'preview-form' : 'submission-form'}\">
                    ${fields.map(field => this.generateFieldHTML(field, isPreview)).join('')}
                    ${!isPreview ? `
                        <div class=\"form-actions\">
                            <button type=\"submit\" class=\"btn btn-primary\">
                                <i class=\"fas fa-paper-plane\"></i> Submit Form
                            </button>
                        </div>
                    ` : ''}
                </form>
            </div>
        `;
    }

    generateFieldHTML(field, isPreview = false) {
        const disabled = isPreview ? 'disabled' : '';
        const required = field.required ? 'required' : '';
        
        let fieldHTML = `
            <div class=\"form-field\">
                <label for=\"${field.id}\">${field.label}${field.required ? ' *' : ''}</label>
        `;

        switch (field.type) {
            case 'textarea':
                fieldHTML += `<textarea id=\"${field.id}\" name=\"${field.id}\" placeholder=\"${field.placeholder}\" ${required} ${disabled}></textarea>`;
                break;
            case 'select':
                fieldHTML += `
                    <select id=\"${field.id}\" name=\"${field.id}\" ${required} ${disabled}>
                        <option value=\"\">Choose an option...</option>
                        ${field.options.map(option => `<option value=\"${option}\">${option}</option>`).join('')}
                    </select>
                `;
                break;
            case 'radio':
                fieldHTML += `
                    <div class=\"radio-group\">
                        ${field.options.map((option, index) => `
                            <div class=\"radio-option\">
                                <input type=\"radio\" id=\"${field.id}_${index}\" name=\"${field.id}\" value=\"${option}\" ${required} ${disabled}>
                                <label for=\"${field.id}_${index}\">${option}</label>
                            </div>
                        `).join('')}
                    </div>
                `;
                break;
            case 'checkbox':
                fieldHTML += `
                    <div class=\"checkbox-group\">
                        ${field.options.map((option, index) => `
                            <div class=\"checkbox-option\">
                                <input type=\"checkbox\" id=\"${field.id}_${index}\" name=\"${field.id}\" value=\"${option}\" ${disabled}>
                                <label for=\"${field.id}_${index}\">${option}</label>
                            </div>
                        `).join('')}
                    </div>
                `;
                break;
            default:
                fieldHTML += `<input type=\"${field.type}\" id=\"${field.id}\" name=\"${field.id}\" placeholder=\"${field.placeholder}\" ${required} ${disabled}>`;
        }

        fieldHTML += '</div>';
        return fieldHTML;
    }

    // Form creation
    async createForm() {
        if (!this.validateForm()) {
            this.showError('Please fill in all required fields');
            return;
        }

        this.showLoading();

        const formData = {
            formName: document.getElementById('form-name').value,
            email: document.getElementById('creator-email').value,
            fields: this.formFields
        };

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/forms`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok) {
                this.hideLoading();
                this.displayQRCode(result);
                this.showSuccess('Form created successfully! Check your email for the QR code and magic link.');
            } else {
                throw new Error(result.error || 'Failed to create form');
            }
        } catch (error) {
            this.hideLoading();
            this.showError(`Error creating form: ${error.message}`);
        }
    }

    displayQRCode(formData) {
        document.getElementById('qr-code-container').innerHTML = 
            `<img src=\"data:image/png;base64,${formData.qrCodeBase64}\" alt=\"QR Code\">`;
        
        document.getElementById('form-details').innerHTML = `
            <div style=\"text-align: left; margin: 20px 0;\">
                <p><strong>Form URL:</strong> <a href=\"${formData.formUrl}\" target=\"_blank\">${formData.formUrl}</a></p>
                <p><strong>View Submissions:</strong> <a href=\"${formData.viewSubmissionsUrl}\" target=\"_blank\">Magic Link</a></p>
            </div>
        `;
        
        this.showQRDisplay();
    }

    // Form loading and submission
    async loadForm(formId) {
        this.showLoading();

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/forms/${formId}`);
            const formData = await response.json();

            if (response.ok) {
                this.hideLoading();
                this.renderFormForSubmission(formData);
            } else {
                throw new Error(formData.error || 'Form not found');
            }
        } catch (error) {
            this.hideLoading();
            this.showError(`Error loading form: ${error.message}`);
        }
    }

    renderFormForSubmission(formData) {
        const formHTML = this.generateFormHTML(formData.formName, formData.fields, false);
        document.getElementById('form-container').innerHTML = formHTML;
        
        document.getElementById('submission-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitForm(formData.formId, formData.fields);
        });

        this.showFormDisplay();
    }

    async submitForm(formId, fields) {
        const formData = new FormData(document.getElementById('submission-form'));
        const responses = {};

        // Process form data
        fields.forEach(field => {
            if (field.type === 'checkbox') {
                const checkedValues = [];
                field.options.forEach((option, index) => {
                    if (formData.get(`${field.id}_${index}`)) {
                        checkedValues.push(option);
                    }
                });
                responses[field.id] = checkedValues.join(', ');
            } else {
                responses[field.id] = formData.get(field.id) || '';
            }
        });

        this.showLoading();

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/forms/${formId}/submit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ responses })
            });

            const result = await response.json();

            if (response.ok) {
                this.hideLoading();
                this.showSuccess('Form submitted successfully! Thank you for your response.');
                document.getElementById('submission-form').reset();
            } else {
                throw new Error(result.error || 'Failed to submit form');
            }
        } catch (error) {
            this.hideLoading();
            this.showError(`Error submitting form: ${error.message}`);
        }
    }

    // Submissions viewing
    async viewSubmissions(formId, token) {
        if (!token) {
            this.showError('Magic token is required to view submissions');
            return;
        }

        this.showLoading();

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/forms/${formId}/submissions?token=${token}`);
            const data = await response.json();

            if (response.ok) {
                this.hideLoading();
                this.renderSubmissions(data);
            } else {
                throw new Error(data.error || 'Failed to load submissions');
            }
        } catch (error) {
            this.hideLoading();
            this.showError(`Error loading submissions: ${error.message}`);
        }
    }

    renderSubmissions(data) {
        const container = document.getElementById('submissions-container');
        
        let html = `
            <h2><i class=\"fas fa-chart-bar\"></i> Form Submissions</h2>
            <div style=\"margin-bottom: 30px;\">
                <h3>${data.formName}</h3>
                <p><strong>Total Submissions:</strong> ${data.totalSubmissions}</p>
                <p><strong>Form Created:</strong> ${new Date(data.createdAt).toLocaleDateString()}</p>
            </div>
        `;

        if (data.submissions.length === 0) {
            html += '<p>No submissions yet.</p>';
        } else {
            data.submissions.forEach((submission, index) => {
                html += `
                    <div class=\"submission-item\">
                        <div class=\"submission-header\">
                            <h4>Submission #${index + 1}</h4>
                            <div>
                                <small>Submitted: ${new Date(submission.submittedAt).toLocaleString()}</small><br>
                                <small>IP: ${submission.ipAddress}</small>
                            </div>
                        </div>
                        <div class=\"submission-responses\">
                            ${data.formFields.map(field => {
                                const response = submission.responses[field.id] || 'No response';
                                return `
                                    <div class=\"response-item\">
                                        <div class=\"response-label\">${field.label}</div>
                                        <div class=\"response-value\">${response}</div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                `;
            });
        }

        container.innerHTML = html;
        this.showSubmissionsView();
    }

    // Utility methods
    resetForm() {
        document.getElementById('form-name').value = '';
        document.getElementById('creator-email').value = '';
        this.formFields = [];
        this.fieldCounter = 0;
        this.renderFormFields();
    }

    showLoading() {
        document.getElementById('loading-overlay').style.display = 'block';
    }

    hideLoading() {
        document.getElementById('loading-overlay').style.display = 'none';
    }

    showError(message) {
        document.getElementById('error-text').textContent = message;
        document.getElementById('error-message').style.display = 'block';
        setTimeout(() => {
            document.getElementById('error-message').style.display = 'none';
        }, 5000);
    }

    showSuccess(message) {
        document.getElementById('success-text').textContent = message;
        document.getElementById('success-message').style.display = 'block';
        setTimeout(() => {
            document.getElementById('success-message').style.display = 'none';
        }, 5000);
    }
}

// Initialize the application
const qrFormify = new QRFormify();
