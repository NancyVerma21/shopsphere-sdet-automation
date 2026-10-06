# ShopSphere — Test Plan

## 1. Objective

Validate the functional behavior, business rules, access controls, data consistency and critical end-to-end workflows of ShopSphere.

## 2. Scope

### In Scope
- Registration, login and logout
- Product browsing, search, filtering and sorting
- Product details and stock behavior
- Cart operations and calculations
- Checkout and simulated payment
- Order creation, history and cancellation
- Profile and address management
- Admin authentication and access control
- API validation
- Database validation
- Negative and boundary scenarios
- Regression, smoke and end-to-end checks

### Out of Scope
- Real payment gateway processing
- Production performance benchmarking
- Real customer data
- Real-world delivery operations

## 3. Test Levels

- System testing
- Integration testing
- End-to-end testing
- API testing
- Database validation

## 4. Test Types

- Functional
- Negative
- Boundary
- Smoke
- Sanity
- Regression
- Compatibility
- Security-related access-control checks

## 5. Test Environment

| Component | Environment |
|---|---|
| Application | Deployed ShopSphere application |
| Browser automation | Chromium via Playwright |
| Database | MySQL |
| API | REST-style application endpoints |
| Automation | Python + Pytest + Playwright |
| CI/CD | GitHub Actions |
| Reporting | Allure |

## 6. Entry Criteria

- Application is reachable.
- Database is available.
- Test data is available.
- Required environment variables are configured.
- Test build is deployed.

## 7. Exit Criteria

- Planned test suite has been executed.
- Results are recorded.
- Critical defects are documented.
- Known expected failures are distinguished from unexpected failures.
- Test summary is published.

## 8. Defect Classification

Severity and priority are assigned according to user/business impact. Known seeded defects are mapped to BUG IDs and expected-failure automation tests where applicable.

## 9. Deliverables

- BRD
- Test Plan
- Test Scenarios
- Test Cases
- Test Data
- RTM
- Bug Reports
- Test Execution
- Test Summary
