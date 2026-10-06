# ShopSphere — Test Execution Report

## Execution Baseline

The latest verified CI execution baseline used by the portfolio is:

| Metric | Result |
|---|---:|
| Test Cases Collected | 63 |
| Passed | 41 |
| Expected Failures (XFAIL) | 22 |
| Unexpected Failures | 0 |

## Execution Scope

- UI automation using Playwright
- API validation
- MySQL database validation
- Authentication and authorization checks
- Cart, checkout and order workflows
- Negative and boundary validation

## Interpretation

The 22 XFAIL results correspond to intentionally seeded ShopSphere application defects. They are expected outcomes explicitly documented by BUG IDs. The successful baseline therefore represents a test suite with no unexpected failures, while the application still contains known defects by design.

## CI/CD

The suite executes through GitHub Actions and publishes Allure reporting to GitHub Pages.

## Environment Incident History

An earlier CI execution produced widespread database connection failures because the Aiven MySQL service was unavailable. After the service was restored, subsequent CI execution returned to the expected green baseline. This demonstrates the difference between infrastructure availability failures and application defects.
