# TesterX

**TesterX**: AI-Driven Automated API Testing Engine, Safeguarding Modern Software Development

TesterX is an AI-driven automated API testing engine designed to intelligently generate comprehensive and efficient API test cases based on the OpenAPI specification. This significantly enhances quality assurance efficiency and reliability in modern software development. TesterX leverages the powerful capabilities of Large Language Models (LLMs) to not only understand the functionality and business logic of API interfaces but also automatically generate various types of test cases, including functional testing, boundary testing, scenario testing, and exception testing. This helps development teams quickly identify and fix potential defects, ensuring the delivery of high-quality software products.

## Language Options

- [简体中文](docs/README_zh.md)

## 🌟 Core Features

- **🤖 LLM-Based Intelligent Test Case Generation**:

  - Utilizes advanced natural language processing and understanding technologies to deeply analyze OpenAPI specifications and intelligently infer the business semantics and data structures of APIs.
  - Automatically generates comprehensive and high-quality test cases covering various testing scenarios, greatly reducing the workload of manual test case writing.

- **📚 Comprehensive Support for OpenAPI 3.1.x Specification**:

  - Seamlessly integrates with the OpenAPI 3.1.x specification, compatible with both JSON and YAML format specification files.
  - Ensures synchronization with the latest API specification standards, providing robust testing support for modern API development.

- **🎯 Automatic Generation of Business Scenario Test Cases**:

  - Goes beyond simple interface testing, capable of understanding and simulating real business processes, automatically generating complex business scenario test cases spanning multiple API interfaces.
  - Helps developers verify the correctness and stability of APIs in actual business scenarios.

- **📊 Integrated Allure Test Reports**:

  - Seamlessly integrates with the popular Allure test report framework, generating beautiful and detailed test reports.
  - Provides rich visualization of test execution data, helping teams quickly locate issues and analyze test results.

- **⚡ High-Performance Test Execution Based on pytest**:

  - Employs the lightweight and powerful pytest testing framework as the test executor, ensuring efficient and stable execution of test cases.
  - Supports flexible test case organization and execution methods, easily integrated into existing development and CI/CD processes.

- **🔄 Automatic Maintenance and Update of Test Cases**:

  - Capable of monitoring changes in API specifications, intelligently analyzing the impact of changes on test cases, and automatically updating and maintaining test cases.
  - Reduces test case maintenance costs and ensures test cases always remain synchronized with the latest API definitions.

## 🚀 Quick Start

Just a few simple steps to start using TesterX to automatically generate and execute tests for your APIs:

1.  **Prepare OpenAPI Specification File**:

    - Ensure you have prepared an API description file compliant with the OpenAPI 3.1.x specification, supporting JSON or YAML format.

2.  **Install TesterX**

3.  **Run Test Case Generation Command**:

    ```bash
    testerx add_api_docs --spec_path api-spec.json
    ```

    - Use the `add_api_docs` subcommand to add your OpenAPI specification file to TesterX's knowledge base. Replace `api-spec.json` with the path to your OpenAPI specification file.

4.  **Generate Test Cases**:

    ```bash
    testerx generate_testcase --requirements "Generate comprehensive test cases for user registration and login interfaces"
    ```

    - Use the `generate_testcase` subcommand and provide a test requirement description. TesterX will intelligently generate test cases based on the knowledge base and requirements. You can modify the requirement description as needed to generate different types of test cases.

5.  **Execute Tests**:

    ```bash
    testerx run
    ```

    - Run the `run` command to execute all generated test cases. TesterX will automatically execute the tests and generate detailed test reports.

## 📂 Project Structure Overview

### Directory Details

- **`projects/` Directory**:

  - Used to store data for each test project, automatically generated by the AI engine after analyzing the OpenAPI specification.
  - Includes:
    - API interface function descriptions
    - Request/response data structures
    - Business rule definitions
    - Test data templates

- **`testcases/` Directory**:

  - Stores test cases automatically generated by TesterX.
  - Divided into two categories:
    - `api_tests/`: Basic functional tests and boundary tests for single API interfaces, etc.
    - `scenarios/`: Scenario integration test cases simulating real business processes, such as user registration and login flows, order creation and payment flows, etc.

- **`testerx/` Directory**:

  - The core source code directory of the TesterX project.
  - Contains key modules:
    - Test case generation engine (`testerx/run/generate.py`, etc.)
    - OpenAPI specification parser (`testerx/run/openapi_parser.py`, etc.)
    - Test executor (`testerx/run/test_executor.py`, etc.)
    - Utility libraries (`testerx/utils/common_utils.py`, etc.)

## ⚙️ Working Principle

The core workflow of TesterX is as follows:

1.  **OpenAPI Specification Parsing**:

    - TesterX first parses the OpenAPI specification file (JSON/YAML format) provided by the user, extracting detailed information about API interfaces, including interface paths, request methods, request parameters, request bodies, response structures, security authentication methods, etc.
    - Utilizes the OpenAPI specification parser (`testerx/run/openapi_parser.py`) to convert the specification document into an internal data structure for subsequent analysis and processing.

2.  **LLM Business Semantics and Data Structure Analysis**:

    - TesterX's intelligent engine (located in the `tools/` directory) utilizes Large Language Models (LLMs), such as Qwen2.5-Coder (offline deployment is being considered), to perform in-depth business semantics and data structure analysis on the parsed API interface information.
    - Understands the function descriptions of each API interface, the meaning of parameters, data types, business rules, constraints, etc., providing intelligent support for subsequent test case generation.

3.  **Intelligent Test Case Generation**:

    - Based on the understanding of API business semantics and data structures, TesterX's test case generation engine (`testerx/run/generate.py`) intelligently generates comprehensive test cases, covering multiple test types:
      - **Basic Functional Testing**: Verifies whether the basic functions of the API interface meet expectations, such as successful/failed requests, data CRUD operations, etc.
      - **Parameter Boundary Testing**: For API interface parameters, generates test cases with boundary values, equivalence classes, exception values, etc., to verify the interface's processing capability and robustness for various parameter values.
      - **Business Scenario Testing**: Simulates real user business operation flows, generates scenario test cases spanning multiple API interfaces, such as testing the complete process of user registration -\> login -\> obtaining user information -\> modifying user information.
      - **Exception Condition Testing**: For various exception conditions, such as network errors, server errors, insufficient permissions, data conflicts, etc., generates corresponding test cases to verify the API interface's exception handling capabilities and whether error prompts are reasonable.

4.  **Test Execution and Detailed Report Generation**:

    - TesterX uses the pytest testing framework as the test executor (`testerx/run/test_executor.py`) to execute the generated test cases.
    - Automatically builds the test execution environment, loads test cases, and executes tests according to pytest rules.
    - Records detailed test logs and results during the test execution process.
    - After test execution is complete, TesterX integrates the Allure report framework to generate beautiful, easy-to-understand, and detailed test reports based on test results and logs (located in the `reports/allure/` directory).
    - Test reports include test case execution status, pass rate, details of failed test cases, error logs, test steps, performance indicators, etc., helping users comprehensively understand the API testing situation.

## ⏳ Project Progress

- ✅ **Completed**

  - Basic function implementation of OpenAPI specification parsing
  - curl command generation and verification function completed

- 🚧 **In Progress**

  - Basic framework construction of the memory system (for storing and managing API knowledge base)
  - Test code generation engine development (test code generation based on templates and AI)
  - Basic capability development for change monitoring (monitoring API specification changes)
  - Dialogue interaction prototype construction (users interact with TesterX through dialogue)
  - Intelligent parameter inference function added (AI intelligently infers test parameters)

- 🚀 **Planned**

  - Cross-interface scenario testing implementation (supports complex business scenario testing)
  - Improve test execution engine (improve test execution efficiency and stability)
  - CI/CD integration capability added (easy integration into continuous integration/continuous delivery pipelines)
  - Monitoring dashboard development (visual display of test results and project status)
  - User documentation writing (provide comprehensive user guides)

### 🚧 Current Work Status

The TesterX project is in an active development phase, and core functions are being gradually improved. Currently, basic functions such as OpenAPI specification parsing and curl command generation have been completed, laying the foundation for subsequent intelligent test case generation and execution. Although the project is still under development, we are committed to making it reach a usable standard as soon as possible, and will continue to iterate and optimize it. Please look forward to it.

### 🔮 Future Work Outlook

- **More Powerful AI Engine**:

  - Continuously optimize and fine-tune LLM models, such as Qwen2.5-Coder, to improve API semantic understanding and test case generation capabilities.
  - **Strive to achieve offline deployment of LLM models** to reduce reliance on third-party APIs, improve system stability and security, and reduce usage costs.

- **More Intelligent Testing Strategies**:

  - Explore and apply more advanced AI technologies, such as reinforcement learning, generative adversarial networks, etc., to achieve more intelligent testing strategies, such as automatically exploring potential API defects, automatically optimizing test case sets, etc.

- **Richer Extensibility**:

  - Provide richer plug-ins and extension mechanisms to facilitate users to customize and extend TesterX's functions according to their own needs, such as supporting more test report formats, integrating more third-party tools, supporting custom test case generation templates, etc.

## 💡 Usage Examples

The following examples demonstrate how to use TesterX for API testing:

Okay, please wait a moment, I will modify the "Usage Examples" section according to your instructions to make it more consistent with the actual operation process you described. The modified "Usage Examples" steps will be adjusted to first modify the `config_example.py` file and rename it to `config.py`, and then proceed with subsequent operations.

Here is the modified **Usage Examples** section:

## 💡 Usage Examples

The following examples demonstrate how to use TesterX for API testing:

### 1\. Configure Project (Modify `config_example.py` and Rename to `config.py`)

In your project root directory, you will find a `config_example.py` file. Please configure your project according to the following steps:

- **Open the `config_example.py` file**: Use a text editor to open the `config_example.py` file.

- **Modify Configuration Information**: According to your actual API environment, modify the following configuration items:

  ```python
      API_INFO = {
          "OHMYGPT": {
              "KEY": "sk-*",
              "BASE_URL": "[https://c-z0-api-01.hash070.com/v1](https://c-z0-api-01.hash070.com/v1)"
          },
          "TXYUN": {
              "KEY": "sk-*",
              "BASE_URL": "[https://api.lkeap.cloud.tencent.com/v1](https://api.lkeap.cloud.tencent.com/v1)"
          }
      }

      EMBEDDING_MODEL = {"format": "openai", "provider": "OHMYGPT", "model": "text-embedding-3-small", }
      CHAT_MODEL = {"format": "openai", "provider": "OHMYGPT", "model": "gpt-4o"}
  ```

  Please be sure to replace `BASE_URL` with the root address of the actual API service you want to test.

- **Rename to `config.py`**: After modification, rename the `config_example.py` file to `config.py`. TesterX will read the configuration information in the `config.py` file.

### 2\. Add OpenAPI Specification to Knowledge Base

```bash
testerx add_api_docs --spec_path ./config.json
```

- Use the `add_api_docs` command to add the OpenAPI specification to TesterX's knowledge base through the project configuration file.

### 3\. Generate Test Cases

```bash
# Generate API single interface test cases (based on knowledge base and default strategy)
testerx generate_testcase --requirements "Generate basic functional test cases for all API interfaces"

# Generate business scenario test cases (e.g., user registration and login scenario)
testerx generate_testcase --requirements "Simulate the complete business process of user registration and login, and generate scenario test cases"
```

- Use the `generate_testcase` command and provide different requirement descriptions to generate different types of test cases. TesterX will intelligently generate test cases based on requirements and API information in the knowledge base.

### 4\. Execute Tests

```bash
# Execute all generated test cases
testerx run

# Execute test cases for a specified scenario (e.g., login_flow scenario)
testerx run --scenario login_flow

# Execute test cases for a specified API interface (e.g., user_login interface)
testerx run --api user_login
```

- Use the `run` command to execute test cases.
  - Without any parameters, it defaults to executing all generated test cases.
  - Use the `--scenario` parameter to specify executing test cases for a specific scenario.
  - Use the `--api` parameter to specify executing test cases for a specific API interface.

### 5\. Generate and View Test Reports

```bash
# Generate Allure test report (default in reports/allure directory)
testerx report

# Start Allure service and view test report in browser
allure serve reports/allure
```

- Use the `report` command to generate an Allure test report.
- Use the `allure serve` command to start the Allure service and open the test report in a browser to analyze test results in detail.

## 📜 License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details

---

**Thank you for your attention and use of TesterX\!** If you have any questions, suggestions, or contributions, you are welcome to submit Issues or Pull Requests through the GitHub repository. Let's work together to build a more intelligent and efficient API testing tool\!
