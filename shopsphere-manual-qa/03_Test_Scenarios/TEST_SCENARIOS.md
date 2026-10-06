# ShopSphere — Test Scenarios

| Scenario ID | Requirement(s) | Scenario |
|---|---|---|
| TS-001 | BR-001 | Register a new customer with valid data. |
| TS-002 | BR-001 | Reject registration with missing required data. |
| TS-003 | BR-001 | Reject registration with duplicate email. |
| TS-004 | BR-001 | Validate password/confirmation rules. |
| TS-005 | BR-002 | Login with valid customer credentials. |
| TS-006 | BR-002 | Reject incorrect password. |
| TS-007 | BR-002 | Reject unknown email. |
| TS-008 | BR-002 | Validate inactive customer login behavior. |
| TS-009 | BR-003 | Logout and invalidate session. |
| TS-010 | BR-003 | Prevent protected-page access after logout. |
| TS-011 | BR-004 | Browse product catalog. |
| TS-012 | BR-004 | Open product details. |
| TS-013 | BR-004 | Display product stock correctly. |
| TS-014 | BR-005 | Search by product name. |
| TS-015 | BR-005 | Search by SKU. |
| TS-016 | BR-005 | Search with no matching data. |
| TS-017 | BR-006 | Filter by category. |
| TS-018 | BR-006 | Apply multiple supported filters. |
| TS-019 | BR-007 | Sort by price ascending. |
| TS-020 | BR-007 | Sort by price descending. |
| TS-021 | BR-008 | Add in-stock product to cart. |
| TS-022 | BR-008 | Prevent adding out-of-stock product. |
| TS-023 | BR-009 | Increase/decrease cart quantity. |
| TS-024 | BR-009 | Reject quantity above available stock. |
| TS-025 | BR-010 | Remove cart item. |
| TS-026 | BR-010 | Validate cart subtotal and line totals. |
| TS-027 | BR-011 | Open checkout with valid cart. |
| TS-028 | BR-011 | Validate address requirements. |
| TS-029 | BR-011 | Calculate shipping boundary correctly. |
| TS-030 | BR-011 | Validate checkout/order total consistency. |
| TS-031 | BR-012 | Complete simulated successful payment. |
| TS-032 | BR-012 | Execute simulated failed payment. |
| TS-033 | BR-013 | Create order after successful payment. |
| TS-034 | BR-013 | Persist order items and payment record. |
| TS-035 | BR-014 | Ensure failed payment does not create order. |
| TS-036 | BR-015 | Display customer order history. |
| TS-037 | BR-015 | Open own order details. |
| TS-038 | BR-015 | Prevent access to another customer order. |
| TS-039 | BR-016 | Display cancellation option for eligible order. |
| TS-040 | BR-016 | Hide cancellation option for cancelled order. |
| TS-041 | BR-016 | Prevent re-cancellation of cancelled order. |
| TS-042 | BR-016 | Prevent cancellation of shipped order. |
| TS-043 | BR-017 | Update profile data. |
| TS-044 | BR-017 | Add/edit/delete address. |
| TS-045 | BR-018 | Admin login and dashboard access. |
| TS-046 | BR-019 | Prevent customer access to admin functionality. |
| TS-047 | BR-020 | Prevent cross-user order access. |
| TS-048 | BR-020 | Prevent cross-user order cancellation. |
| TS-049 | BR-021 | Validate user persistence in DB. |
| TS-050 | BR-021 | Validate product/catalog persistence in DB. |
| TS-051 | BR-021 | Validate cart persistence in DB. |
| TS-052 | BR-021 | Validate order persistence in DB. |
| TS-053 | BR-021 | Validate payment persistence in DB. |
| TS-054 | BR-021 | Validate UI/API/DB order total consistency. |
| TS-055 | BR-022 | Prevent protected resource access without authentication. |
| TS-056 | BR-022 | Validate role-based API access. |
| TS-057 | BR-005 | Search by exact known SKU. |
| TS-058 | BR-006 | Reset filters and restore catalog. |
| TS-059 | BR-007 | Validate sorting with equal-price products. |
| TS-060 | BR-008 | Add same product twice and verify quantity behavior. |
| TS-061 | BR-009 | Validate quantity update recalculates totals. |
| TS-062 | BR-013 | Validate order confirmation data after successful payment. |
| TS-063 | BR-014 | Validate no completed order after failed payment. |
