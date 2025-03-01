# Task: API Analysis, Verification, and Documentation Generation for {{api_path}}

**Objective:** To analyze, verify, and generate comprehensive documentation for the {{api_path}} API endpoint.

## 1. API Analysis:

* **Basic Information:** Extract the API path, method, parameters, etc.
* **Business Scenario:** Clearly define the purpose and application scenarios of the API.
* **Permission Requirements:** Identify the required permission verification methods (e.g., token, role).
* **Dependencies:** Analyze the calling sequence and data dependencies with other APIs.

## 2. API Verification (Test Environment: {{base_url}}):

* **Parameter Validation:**
    * Test for missing required parameters.
    * Test for incorrect parameter formats.
    * Test parameter boundary values.
* **Permission Validation:**
    * Test without a token.
    * Test with an expired token.
    * Test with an incorrect token.
* **Functional Validation:**
    * Test with a normal request.
    * Verify the response format.
    * Verify the response fields.
* **Boundary Condition Testing:**
    * Debug the API and test boundary conditions.

## 3. Documentation Generation (using store_memory for subsequent search embedding):

* **Basic Information:** API path, method, description.
* **Parameter Description:** Parameter name, type, whether required, description.
* **Dependent APIs:** List all dependent APIs.
* **Call Example:** Provide a curl command example.
* **Error Response:** Record possible error codes and error messages.

## 4. Error Handling:

* If the API call fails, record the request parameters, error response, error code, and possible causes in detail.

**Input Context:**

* **System Information:** Test environment, Base URL: {{base_url}}
* **API Documentation:** {{api_doc}} (used to determine API business logic)

**Execution Steps:**

1. Analyze the {{api_path}} API based on the input context.
2. Debug the API and test various scenarios according to the verification steps.
3. Generate detailed API documentation and store it using store_memory.
4. Use the complete_step command to end the current step and pass the necessary information for the next step.

**Notes:**

* Ensure that the API debugging is correct before generating the documentation.
* The generated documentation should be highly relevant to the API.

---

# Task: API Analysis, Verification, and Documentation Generation for {{api_path}}

**Objective:** To analyze, verify, and generate comprehensive documentation for the {{api_path}} API endpoint.

## 1. API Analysis:

* **Basic Information:** Extract the API path, method, parameters, etc.
* **Business Scenario:** Clearly define the purpose and application scenarios of the API.
* **Permission Requirements:** Identify the required permission verification methods (e.g., token, role).
* **Dependencies:** Analyze the calling sequence and data dependencies with other APIs.

## 2. API Verification (Test Environment: {{base_url}}):

* **Parameter Validation:**
    * Test for missing required parameters.
    * Test for incorrect parameter formats.
    * Test parameter boundary values.
* **Permission Validation:**
    * Test without a token.
    * Test with an expired token.
    * Test with an incorrect token.
* **Functional Validation:**
    * Test with a normal request.
    * Verify the response format.
    * Verify the response fields.
* **Boundary Condition Testing:**
    * Debug the API and test boundary conditions.

## 3. Documentation Generation (using store_memory for subsequent search embedding):

* **Basic Information:** API path, method, description.
* **Parameter Description:** Parameter name, type, whether required, description.
* **Dependent APIs:** List all dependent APIs.
* **Call Example:** Provide a curl command example.
* **Error Response:** Record possible error codes and error messages.

## 4. Error Handling:

* If the API call fails, record the request parameters, error response, error code, and possible causes in detail.

**Input Context:**

* **System Information:** Test environment, Base URL: {{base_url}}
* **API Documentation:** {{api_doc}} (used to determine API business logic)

**Execution Steps:**

1. Analyze the {{api_path}} API based on the input context.
2. Debug the API and test various scenarios according to the verification steps.
3. Generate detailed API documentation and store it using store_memory.
4. Use the complete_step command to end the current step and pass the necessary information for the next step.

**Notes:**

* Ensure that the API debugging is correct before generating the documentation.
* The generated documentation should be highly relevant to the API.