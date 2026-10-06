# ShopSphere — Test Data

## Users

| Data | Example | Purpose |
|---|---|---|
| Valid customer email | qa.customer@example.com | Standard customer flows |
| Invalid email | invalid-email | Registration/login negative case |
| Duplicate email | existing customer email | Duplicate registration |
| Valid password | TestPassword@123 | Standard authentication |
| Weak password | Test | Password boundary/negative case |
| Admin role | admin test account configured in environment | Admin authentication/authorization |
| Inactive user | Seeded inactive account | Inactive-login validation |

## Products

The seeded catalog used by ShopSphere includes:

| SKU | Product | Price | Stock |
|---|---|---:|---:|
| P001 | Wireless Mouse | 799.00 | 45 |
| P002 | Mechanical Keyboard | 2499.00 | 25 |
| P003 | Laptop Stand | 1299.00 | 30 |
| P004 | Bluetooth Speaker | 1999.00 | 20 |
| P005 | Smart LED Bulb | 699.00 | 50 |
| P006 | Cotton T-Shirt | 599.00 | 60 |
| P007 | Casual Sneakers | 2199.00 | 18 |
| P008 | Travel Backpack | 1799.00 | 22 |
| P009 | Desk Organizer | 499.00 | 35 |
| P010 | USB-C Hub | 1599.00 | 15 |
| P011 | Bluetooth Speaker Mini | 999.00 | 0 |

## Boundary Data

- Quantity = 0
- Quantity = 1
- Quantity = stock value
- Quantity = stock + 1
- Checkout subtotal at shipping threshold
- Checkout subtotal just below threshold
- Checkout subtotal just above threshold

## Payment Simulation

- Successful simulated payment input
- Failed simulated payment input

## Security / Authorization Data

- Customer credentials attempting admin endpoint access
- Customer A attempting Customer B order access
- Customer A attempting Customer B order cancellation

> All values are fictional test data. No real payment credentials are used.
