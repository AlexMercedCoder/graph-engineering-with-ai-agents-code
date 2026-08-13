# BillingService
BillingService owns invoicing and payment capture. It calls the NotificationsAPI
to send receipts, and it depends on OrderService for line items. It stores
invoices in the billing Postgres database.
