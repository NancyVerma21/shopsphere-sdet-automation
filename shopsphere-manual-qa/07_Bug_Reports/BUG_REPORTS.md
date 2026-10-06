# ShopSphere — Bug Reports

These defects are intentionally retained in the portfolio application to demonstrate defect detection and reporting.

| Bug ID | Summary | Severity | Priority | Status |
|---|---|---|---|---|
| BUG-002 | Cart quantity can exceed available stock | High | High | Application accepts/retains a quantity above available stock. |
| BUG-003 | Price sorting does not consistently sort by price | Medium | Medium | Returned order can be inconsistent with requested price sort. |
| BUG-004 | Search by product name can return incorrect results | High | High | Search behavior can fail to return the expected product. |
| BUG-005 | Shipping boundary calculation is incorrect | High | High | Boundary behavior is incorrect for the targeted subtotal. |
| BUG-006 | Cancelled order still exposes Cancel action | High | High | Cancel action remains available. |
| BUG-007 | Inactive user can authenticate | High | High | Application can allow inactive user login. |
| BUG-008 | Logout does not fully invalidate protected session | Critical | High | Protected resource can remain accessible after logout. |
| BUG-009 | Customer can access admin functionality | Critical | Critical | Customer can reach protected admin functionality. |
| BUG-010 | Password validation accepts weak four-character password | Medium | Medium | Weak password can be accepted. |
| BUG-012 | Customer can access another customer order | Critical | Critical | Cross-user order access is possible. |
| BUG-014 | Customer can cancel another customer order | Critical | Critical | Cross-user cancellation can succeed. |
| BUG-015 | Cancelled order can be cancelled again | High | High | Re-cancellation remains available. |
| BUG-019 | Payment/order persistence behavior is incorrect | Critical | Critical | Payment/order persistence can be inconsistent with expected behavior. |
| BUG-020 | Shipped order exposes cancellation action | High | High | Cancel action remains visible for shipped order. |

## Defect Details

### BUG-002 — Cart quantity can exceed available stock

**Severity:** High  
**Priority:** High  
**Requirement Area:** Order/cart stock rule

**Steps to Reproduce**
1. Set cart quantity above product stock
2. Observe the application behavior.

**Expected Result**
Quantity above stock is rejected

**Actual Result**
Application accepts/retains a quantity above available stock.

**Status**
Application accepts/retains a quantity above available stock.

### BUG-003 — Price sorting does not consistently sort by price

**Severity:** Medium  
**Priority:** Medium  
**Requirement Area:** Product sorting

**Steps to Reproduce**
1. Sort products by price ascending/descending
2. Observe the application behavior.

**Expected Result**
Products are ordered numerically by price

**Actual Result**
Returned order can be inconsistent with requested price sort.

**Status**
Returned order can be inconsistent with requested price sort.

### BUG-004 — Search by product name can return incorrect results

**Severity:** High  
**Priority:** High  
**Requirement Area:** Product search

**Steps to Reproduce**
1. Search using a known product name
2. Observe the application behavior.

**Expected Result**
Matching products are returned

**Actual Result**
Search behavior can fail to return the expected product.

**Status**
Search behavior can fail to return the expected product.

### BUG-005 — Shipping boundary calculation is incorrect

**Severity:** High  
**Priority:** High  
**Requirement Area:** Checkout shipping rule

**Steps to Reproduce**
1. Use subtotal at the defined free-shipping boundary
2. Observe the application behavior.

**Expected Result**
Shipping charge follows boundary rule

**Actual Result**
Boundary behavior is incorrect for the targeted subtotal.

**Status**
Boundary behavior is incorrect for the targeted subtotal.

### BUG-006 — Cancelled order still exposes Cancel action

**Severity:** High  
**Priority:** High  
**Requirement Area:** Order cancellation

**Steps to Reproduce**
1. Open an already-cancelled order
2. Observe the application behavior.

**Expected Result**
Cancel action is hidden/disabled

**Actual Result**
Cancel action remains available.

**Status**
Cancel action remains available.

### BUG-007 — Inactive user can authenticate

**Severity:** High  
**Priority:** High  
**Requirement Area:** Authentication

**Steps to Reproduce**
1. Attempt login with inactive account
2. Observe the application behavior.

**Expected Result**
Login is rejected

**Actual Result**
Application can allow inactive user login.

**Status**
Application can allow inactive user login.

### BUG-008 — Logout does not fully invalidate protected session

**Severity:** Critical  
**Priority:** High  
**Requirement Area:** Session security

**Steps to Reproduce**
1. Login, logout, then access protected page
2. Observe the application behavior.

**Expected Result**
Protected page requires fresh authentication

**Actual Result**
Protected resource can remain accessible after logout.

**Status**
Protected resource can remain accessible after logout.

### BUG-009 — Customer can access admin functionality

**Severity:** Critical  
**Priority:** Critical  
**Requirement Area:** Authorization

**Steps to Reproduce**
1. Authenticate as customer and access admin area/API
2. Observe the application behavior.

**Expected Result**
Access denied

**Actual Result**
Customer can reach protected admin functionality.

**Status**
Customer can reach protected admin functionality.

### BUG-010 — Password validation accepts weak four-character password

**Severity:** Medium  
**Priority:** Medium  
**Requirement Area:** Registration validation

**Steps to Reproduce**
1. Register using a 4-character password
2. Observe the application behavior.

**Expected Result**
Weak password rejected

**Actual Result**
Weak password can be accepted.

**Status**
Weak password can be accepted.

### BUG-012 — Customer can access another customer order

**Severity:** Critical  
**Priority:** Critical  
**Requirement Area:** Order authorization

**Steps to Reproduce**
1. Use Customer A session to open Customer B order
2. Observe the application behavior.

**Expected Result**
Access denied

**Actual Result**
Cross-user order access is possible.

**Status**
Cross-user order access is possible.

### BUG-014 — Customer can cancel another customer order

**Severity:** Critical  
**Priority:** Critical  
**Requirement Area:** Order authorization

**Steps to Reproduce**
1. Attempt cancellation using another customer session
2. Observe the application behavior.

**Expected Result**
Access denied

**Actual Result**
Cross-user cancellation can succeed.

**Status**
Cross-user cancellation can succeed.

### BUG-015 — Cancelled order can be cancelled again

**Severity:** High  
**Priority:** High  
**Requirement Area:** Order lifecycle

**Steps to Reproduce**
1. Cancel an order twice
2. Observe the application behavior.

**Expected Result**
Second cancellation blocked

**Actual Result**
Re-cancellation remains available.

**Status**
Re-cancellation remains available.

### BUG-019 — Payment/order persistence behavior is incorrect

**Severity:** Critical  
**Priority:** Critical  
**Requirement Area:** Checkout/payment

**Steps to Reproduce**
1. Complete simulated payment and verify persistence
2. Observe the application behavior.

**Expected Result**
Payment/order state is consistent

**Actual Result**
Payment/order persistence can be inconsistent with expected behavior.

**Status**
Payment/order persistence can be inconsistent with expected behavior.

### BUG-020 — Shipped order exposes cancellation action

**Severity:** High  
**Priority:** High  
**Requirement Area:** Order lifecycle

**Steps to Reproduce**
1. Open shipped order
2. Observe the application behavior.

**Expected Result**
Cancellation is unavailable

**Actual Result**
Cancel action remains visible for shipped order.

**Status**
Cancel action remains visible for shipped order.

