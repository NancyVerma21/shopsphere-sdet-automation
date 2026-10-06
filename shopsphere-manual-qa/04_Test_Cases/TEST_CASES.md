# ShopSphere — Detailed Test Cases


| Test Case | Scenario | Test Case | Priority | Expected Status | Defect |
|---|---|---|---|---|---|
| TC-001 | TS-001 | Registration with valid data | High | PASS | — |
| TC-002 | TS-002 | Registration with missing required field | High | PASS | — |
| TC-003 | TS-003 | Registration with duplicate email | High | PASS | — |
| TC-004 | TS-004 | Password confirmation mismatch | Medium | XFAIL | BUG-010 |
| TC-005 | TS-005 | Valid customer login | High | PASS | — |
| TC-006 | TS-006 | Invalid password rejected | High | PASS | — |
| TC-007 | TS-007 | Unknown email rejected | High | PASS | — |
| TC-008 | TS-008 | Inactive customer login behavior | High | XFAIL | BUG-007 |
| TC-009 | TS-009 | Logout ends session | High | PASS | — |
| TC-010 | TS-010 | Protected page after logout | High | XFAIL | BUG-008 |
| TC-011 | TS-011 | Browse product catalog | High | PASS | — |
| TC-012 | TS-012 | Open product details | Medium | PASS | — |
| TC-013 | TS-013 | Display product stock | Medium | PASS | — |
| TC-014 | TS-014 | Search by product name | High | XFAIL | BUG-004 |
| TC-015 | TS-015 | Search by SKU | High | PASS | — |
| TC-016 | TS-016 | No-result search | Medium | PASS | — |
| TC-017 | TS-017 | Filter by category | Medium | PASS | — |
| TC-018 | TS-018 | Multiple filters | Medium | PASS | — |
| TC-019 | TS-019 | Price sort ascending | Medium | XFAIL | BUG-003 |
| TC-020 | TS-020 | Price sort descending | Medium | PASS | — |
| TC-021 | TS-021 | Add in-stock product to cart | High | PASS | — |
| TC-022 | TS-022 | Prevent out-of-stock product add | High | PASS | — |
| TC-023 | TS-023 | Update cart quantity | High | XFAIL | BUG-002 |
| TC-024 | TS-024 | Reject quantity above stock | High | XFAIL | BUG-002 |
| TC-025 | TS-025 | Remove cart item | Medium | PASS | — |
| TC-026 | TS-026 | Cart subtotal and line total | High | XFAIL | BUG-002 |
| TC-027 | TS-027 | Open checkout | High | PASS | — |
| TC-028 | TS-028 | Address required at checkout | High | PASS | — |
| TC-029 | TS-029 | Shipping threshold boundary | High | XFAIL | BUG-005 |
| TC-030 | TS-030 | Checkout total matches order total | High | XFAIL | BUG-019 |
| TC-031 | TS-031 | Successful simulated payment | Critical | XFAIL | BUG-019 |
| TC-032 | TS-032 | Failed simulated payment | Critical | XFAIL | BUG-019 |
| TC-033 | TS-033 | Order created after success | Critical | XFAIL | BUG-019 |
| TC-034 | TS-034 | Order items/payment persisted | High | XFAIL | BUG-019 |
| TC-035 | TS-035 | No order after failed payment | Critical | XFAIL | BUG-019 |
| TC-036 | TS-036 | Order history shows customer order | High | PASS | — |
| TC-037 | TS-037 | Open own order details | High | XFAIL | BUG-012 |
| TC-038 | TS-038 | Block another customer order access | Critical | XFAIL | BUG-012 |
| TC-039 | TS-039 | Eligible order shows cancel option | High | PASS | — |
| TC-040 | TS-040 | Cancelled order hides cancel option | High | XFAIL | BUG-006 |
| TC-041 | TS-041 | Cancelled order cannot be cancelled again | High | XFAIL | BUG-015 |
| TC-042 | TS-042 | Shipped order cannot be cancelled | High | XFAIL | BUG-020 |
| TC-043 | TS-043 | Update profile | Medium | PASS | — |
| TC-044 | TS-044 | Manage address | Medium | PASS | — |
| TC-045 | TS-045 | Admin login/dashboard | High | PASS | — |
| TC-046 | TS-046 | Customer blocked from admin | Critical | XFAIL | BUG-009 |
| TC-047 | TS-047 | Cross-user order view blocked | Critical | PASS | — |
| TC-048 | TS-048 | Cross-user cancellation blocked | Critical | XFAIL | BUG-014 |
| TC-049 | TS-049 | User persistence validation | High | PASS | — |
| TC-050 | TS-050 | Product persistence validation | Medium | PASS | — |
| TC-051 | TS-051 | Cart persistence validation | High | PASS | — |
| TC-052 | TS-052 | Order persistence validation | Critical | PASS | — |
| TC-053 | TS-053 | Payment persistence validation | High | PASS | — |
| TC-054 | TS-054 | UI/API/DB total consistency | High | PASS | — |
| TC-055 | TS-055 | Unauthenticated protected-resource access | High | PASS | — |
| TC-056 | TS-056 | Role-based API access | Critical | PASS | — |
| TC-057 | TS-057 | Exact SKU search | Medium | PASS | — |
| TC-058 | TS-058 | Reset filters | Low | PASS | — |
| TC-059 | TS-059 | Equal-price sort stability | Low | PASS | — |
| TC-060 | TS-060 | Add same product twice | High | PASS | — |
| TC-061 | TS-061 | Quantity update recalculates totals | High | PASS | — |
| TC-062 | TS-062 | Successful-payment confirmation data | High | PASS | — |
| TC-063 | TS-063 | Failed payment creates no completed order | Critical | PASS | — |

> Note: The execution status above represents the portfolio execution baseline. XFAIL denotes intentionally seeded ShopSphere defects; it is not treated as an unexpected automation failure.
