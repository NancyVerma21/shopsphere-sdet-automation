# ShopSphere — SDET Automation Framework

[![ShopSphere SDET Tests](https://github.com/NancyVerma21/shopsphere-sdet-automation/actions/workflows/tests.yml/badge.svg)](https://github.com/NancyVerma21/shopsphere-sdet-automation/actions/workflows/tests.yml)

**Live Application:** https://shopsphere-app-5osa.onrender.com  
**Live Allure Report:** https://nancyverma21.github.io/shopsphere-sdet-automation/

---

## Project Overview

ShopSphere is a fictional e-commerce application created as a portfolio project to demonstrate practical SDET and QA automation skills.

The project covers:

- UI automation
- API testing
- Database validation
- End-to-end testing
- Authentication and authorization
- Negative and boundary testing
- Defect detection
- CI/CD execution
- Allure reporting

The application intentionally contains seeded defects so the automation framework demonstrates how an SDET detects and reports defects.

---

## Technology Stack

| Area | Technology |
|---|---|
| Language | Python 3.11 |
| Test Framework | Pytest |
| UI Automation | Playwright |
| API Testing | Requests |
| Database | MySQL |
| DB Validation | mysql-connector-python |
| Configuration | python-dotenv |
| Reporting | Allure |
| Parallel Execution | pytest-xdist |
| CI/CD | GitHub Actions |
| Application Hosting | Render |
| Database Hosting | Aiven MySQL |
| Version Control | Git + GitHub |

---

## Automation Architecture

```text
                 ShopSphere Application
                         │
           ┌─────────────┼─────────────┐
           │             │             │
           ▼             ▼             ▼
      UI Testing     API Testing   DB Validation
      Playwright      Requests       MySQL
           │             │             │
           └─────────────┼─────────────┘
                         ▼
                       Pytest
                         │
                         ▼
                  Allure Reporting
                         │
                         ▼
                   GitHub Actions
                         │
                         ▼
                    GitHub Pages
```

---

## Test Coverage

### UI Testing

- Registration
- Login
- Logout
- Product browsing
- Product search
- Filtering
- Sorting
- Product details
- Shopping cart
- Cart quantity
- Cart totals
- Checkout
- Payment flow
- Order history
- Order cancellation
- Profile management
- Address management
- Admin authentication
- Access control

### API Testing

- Authentication APIs
- Product APIs
- Cart APIs
- Order APIs
- Payment validation
- Authorization checks
- Negative API scenarios
- Response validation

### Database Testing

- User data validation
- Product data validation
- Cart persistence
- Order persistence
- Order-item validation
- Payment records
- UI/API/database consistency
- Cross-user data validation

---

## Test Execution

### Latest Successful Execution

| Metric | Result |
|---|---:|
| Total Test Cases | 63 |
| Passed | 41 |
| Expected Failures | 22 |
| Unexpected Failures | 0 |

The suite contains automated tests and intentionally expected failures for known ShopSphere application defects.

### About the 22 Expected Failures

The 22 `XFAIL` results represent intentionally seeded defects in the ShopSphere application.

They are intentionally kept unresolved so the project demonstrates:

```text
Requirement
    ↓
Test Design
    ↓
Automation
    ↓
Defect Detection
    ↓
Expected Failure
    ↓
Defect Documentation
    ↓
Retest / Regression
```

Because the known defects are marked as expected failures, the Allure report may show a 100% overall report status. This does not mean the application has zero defects.

---

## Intentionally Seeded Defects

The automation suite covers defects such as:

- Cart quantity exceeding available stock
- Incorrect price sorting
- Incorrect product search behavior
- Shipping boundary calculation issue
- Incorrect cancelled-order behavior
- Inactive-user login issue
- Logout/session invalidation issue
- Customer access to admin functionality
- Weak password validation
- Cross-user order access
- Cross-user order cancellation
- Re-cancellation of cancelled orders
- Payment/order persistence issue
- Cancellation of shipped orders

These defects are intentionally retained for QA/SDET demonstration purposes.

---

## Project Structure

```text
shopsphere-sdet-automation/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── data/
├── pages/
├── tests/
├── utils/
│
├── shopsphere-manual-qa/
│   ├── 01_Requirements/
│   ├── 02_Test_Plan/
│   ├── 03_Test_Scenarios/
│   ├── 04_Test_Cases/
│   ├── 05_Test_Data/
│   ├── 06_RTM/
│   ├── 07_Bug_Reports/
│   ├── 08_Test_Execution/
│   └── 09_Test_Summary/
│
├── .env.example
├── .gitignore
├── conftest.py
├── package-lock.json
├── package.json
├── pytest.ini
├── requirements.txt
├── TEST_EXECUTION_SUMMARY.md
└── README.md
```

---

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/NancyVerma21/shopsphere-sdet-automation.git
cd shopsphere-sdet-automation
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Install Playwright Chromium

```bash
playwright install chromium
```

### 6. Configure environment variables

Create a local `.env` file using `.env.example`.

Do not commit passwords, secrets, API keys, or database credentials.

### 7. Run all tests

```bash
pytest -v
```

### 8. Run UI tests

```bash
pytest tests/ui -v
```

### 9. Run API tests

```bash
pytest tests/api -v
```

### 10. Run database tests

```bash
pytest tests/db -v
```

### 11. Generate Allure results

```bash
pytest -v --alluredir=allure-results
```

### 12. Generate the Allure report locally

```bash
allure generate allure-results -o allure-report --clean
```

---

## Allure Reporting

The project uses Allure for detailed automated test reporting.

### Live Allure Report

https://nancyverma21.github.io/shopsphere-sdet-automation/

The report provides:

- Test execution summary
- Test suites
- Test cases
- Behaviors
- UI/API coverage
- Passed tests
- Expected failures
- Test details

---

## CI/CD Pipeline

GitHub Actions automatically executes the SDET test suite.

```text
Git Push / Pull Request
          ↓
GitHub Actions
          ↓
Install Python
          ↓
Install Dependencies
          ↓
Install Playwright
          ↓
Check Application Availability
          ↓
Execute Pytest
          ↓
Generate Allure Results
          ↓
Build Allure Report
          ↓
Upload Report
          ↓
GitHub Pages
```

### GitHub Actions

https://github.com/NancyVerma21/shopsphere-sdet-automation/actions

The latest successful workflow validates the automation framework against the deployed ShopSphere application.

---

## Security

Sensitive configuration is stored using environment variables and GitHub Actions Secrets.

Examples:

```text
BASE_URL
DB_HOST
DB_PORT
DB_USER
DB_PASSWORD
DB_NAME
SECRET_KEY
```

No passwords or production credentials are stored in the repository.

---

## QA / SDET Concepts Demonstrated

- Test automation
- Page Object Model
- Pytest fixtures
- UI automation
- API automation
- Database validation
- End-to-end testing
- Functional testing
- Negative testing
- Boundary testing
- Authentication testing
- Authorization testing
- Regression testing
- Smoke testing
- Defect validation
- Expected-failure handling
- Allure reporting
- CI/CD
- Git/GitHub

---

## Manual QA Documentation

The automation framework is supported by a complete manual QA testing lifecycle covering requirements, planning, test design, test execution, traceability, and defect management.

### QA Artifacts

- [Business Requirements Document](./shopsphere-manual-qa/01_Requirements/BRD.md)
- [Test Plan](./shopsphere-manual-qa/02_Test_Plan/TEST_PLAN.md)
- [Test Scenarios](./shopsphere-manual-qa/03_Test_Scenarios/TEST_SCENARIOS.md)
- [Test Cases](./shopsphere-manual-qa/04_Test_Cases/TEST_CASES.md)
- [Test Data](./shopsphere-manual-qa/05_Test_Data/TEST_DATA.md)
- [Requirement Traceability Matrix](./shopsphere-manual-qa/06_RTM/RTM.md)
- [Bug Reports](./shopsphere-manual-qa/07_Bug_Reports/BUG_REPORTS.md)
- [Test Execution Report](./shopsphere-manual-qa/08_Test_Execution/TEST_EXECUTION.md)
- [Test Summary Report](./shopsphere-manual-qa/09_Test_Summary/TEST_SUMMARY.md)

These artifacts provide the manual QA foundation for the automated UI, API, and database testing implemented in this project.

---

## Automation Highlights

The project demonstrates an end-to-end workflow:

```text
Requirements
     ↓
Manual Test Design
     ↓
Automation Development
     ↓
UI + API + DB Validation
     ↓
Defect Detection
     ↓
Pytest Execution
     ↓
Allure Reporting
     ↓
GitHub Actions CI/CD
     ↓
GitHub Pages
```

---

## Future Enhancements

- Cross-browser execution
- Additional API coverage
- Additional database assertions
- Advanced logging
- Screenshot and trace collection
- Performance testing
- Accessibility testing
- Dockerized execution
- Extended CI/CD quality gates

---

## Disclaimer

ShopSphere is a fictional portfolio application created for demonstrating QA and SDET automation skills.

All users, products, orders, payment information, defects and test results are fictional or simulated.

No real payment information or production credentials are used.

---

## Author

**Nancy Verma**

B.Tech — Computer Science & Engineering

GitHub:  
https://github.com/NancyVerma21
