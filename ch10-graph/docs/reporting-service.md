# ReportingService

## Overview

ReportingService builds the revenue reports. Finance reads them daily, and the monthly close uses the end-of-month snapshot.

## Integrations

It depends on BillingService for invoice totals and on OrderService for order status.

Its dashboards also show PaymentsService decline rates, which finance copies in by hand from the provider portal each week.

## Data

It stores nothing. Every report is computed on request from the services it depends on, so a report is always as current as its sources.

## Operations

Report generation has no retries. A failed report shows an error page, and the reader reloads.
