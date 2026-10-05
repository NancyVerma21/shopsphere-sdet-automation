# ShopSphere SDET Test Execution Summary

## Execution Overview

| Metric | Result |
|---|---:|
| Total Test Cases | 63 |
| Passed | 41 |
| Expected Failures | 22 |
| Unexpected Failures | 0 |
| Automation Coverage | UI + API + Database |

## Important Note About Allure

The Allure dashboard may display **100%** because the 22 intentionally failing tests are implemented as
`pytest.xfail` tests.

This does **not** mean that no defects were found.

The 22 expected failures represent known defects intentionally seeded in the
ShopSphere Application Under Test (AUT).

## Known Defects Detected by Automation

The automation suite currently detects and documents defects including:

- BUG-002 — Cart quantity can exceed available stock
- BUG-003 — Product price sorting is incorrect
- BUG-004 — Product-name search returns incorrect results
- BUG-005 — Free-shipping boundary condition is incorrect
- BUG-006 — Cancel action is incorrectly available for cancelled orders
- BUG-007 — Inactive account can log in
- BUG-008 — Logout does not fully invalidate the session
- BUG-009 — Customer can access admin functionality
- BUG-010 — Four-character password is accepted
- BUG-012 — Customer can access another customer's order
- BUG-014 — Customer can cancel another customer's order
- BUG-015 — Cancelled order can be cancelled again
- BUG-019 — Successful payment exposes an order persistence defect
- BUG-020 — Cancel action is incorrectly available for shipped orders

Additional defect mappings are maintained in the project test/defect documentation.

## Final Interpretation

The suite demonstrates that the automation framework can:

1. Execute UI and API regression tests.
2. Validate database state using MySQL.
3. Detect intentionally seeded application defects.
4. Separate expected AUT defects from unexpected automation failures.
5. Run against the deployed ShopSphere application.
6. Execute through GitHub Actions CI.

### Result

41 tests passed successfully and 22 known AUT defects were detected/documented, with 0 unexpected test failures.