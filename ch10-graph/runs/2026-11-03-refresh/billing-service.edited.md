# BillingService

## Overview

BillingService owns invoicing and payment capture. It turns completed orders into invoices, captures payment against the authorization taken at checkout, and issues receipts.

## Data

BillingService stores invoices in the billing Postgres database. Invoice numbers are sequential per region and are never reused, even for voided invoices.

## Integrations

It depends on OrderService for line items. It calls the NotificationsAPI to send receipts once a capture succeeds. It calls the PaymentsAPI to refund a capture that the customer disputes.

The billing-service team also maintains the shared invoice templates.

## Operations

Invoice generation runs every fifteen minutes. A run that fails leaves its orders in the pending queue, and the next run picks them up, so a missed run delays invoices without losing them.
