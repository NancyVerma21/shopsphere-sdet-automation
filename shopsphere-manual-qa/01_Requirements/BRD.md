# ShopSphere — Business Requirements Document (BRD)

## 1. Document Purpose

ShopSphere is a fictional e-commerce web application used as a portfolio QA/SDET project. This BRD defines the functional scope used for manual test design and automation.

## 2. Business Goal

Provide customers with a complete shopping journey from account creation and product discovery through cart, checkout, simulated payment, order history and order cancellation, while providing administrators with controlled product and order management capabilities.

## 3. User Roles

| Role | Purpose |
|---|---|
| Customer | Register, authenticate, browse products, manage cart, checkout, view and manage own orders/profile |
| Administrator | Authenticate and access administrative product/order/customer visibility functions |

## 4. Functional Requirements

| ID | Requirement |
|---|---|
| BR-001 | Customer registration shall validate required user information and create a customer account. |
| BR-002 | Customer login shall authenticate valid credentials and reject invalid or inactive credentials. |
| BR-003 | Customer logout shall terminate the authenticated session and protect subsequent protected-page access. |
| BR-004 | Customers shall browse products and view product details including price and stock information. |
| BR-005 | Product search shall return products matching supported search criteria. |
| BR-006 | Customers shall filter products using available filters. |
| BR-007 | Customers shall sort products using supported sorting options, including price sorting. |
| BR-008 | Customers shall add products to the cart when stock permits. |
| BR-009 | Cart quantity changes shall respect stock constraints and update totals correctly. |
| BR-010 | Customers shall remove cart items and cart totals shall remain consistent. |
| BR-011 | Checkout shall require valid customer/address information and calculate the order total correctly, including shipping rules. |
| BR-012 | Simulated payment shall support successful and failed payment outcomes. |
| BR-013 | A successful payment shall create/persist the order and associated order data. |
| BR-014 | A failed payment shall not create a completed order. |
| BR-015 | Customers shall view their own order history and order details. |
| BR-016 | Customers shall cancel eligible orders according to order status rules and shall not cancel ineligible orders. |
| BR-017 | Customers shall manage their profile and saved addresses. |
| BR-018 | Administrators shall access administrative functionality after successful admin authentication. |
| BR-019 | Customers shall not access administrative functionality. |
| BR-020 | Customer order data shall be isolated so one customer cannot view or modify another customer’s orders. |
| BR-021 | Database records shall remain consistent with UI/API operations for users, products, carts, orders, order items and payments. |
| BR-022 | Application access shall protect authenticated and role-restricted resources. |

## 5. Non-Functional Expectations

- The web application should be usable in a supported modern browser.
- Critical customer workflows should provide clear success and validation feedback.
- Sensitive configuration and credentials must not be exposed in source control.

## 6. Assumptions

- Payment processing is simulated for testing.
- ShopSphere is a fictional portfolio application.
- Seeded application defects are intentionally retained for QA demonstration.
- The database contains the ShopSphere tables used by the automation framework.
