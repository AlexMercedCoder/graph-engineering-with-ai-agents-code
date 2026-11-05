# PaymentsService

## Overview

PaymentsService exposes the PaymentsAPI. It wraps the external payment provider so that no other service holds provider credentials.

## Data

It stores authorizations in the payments Postgres database, with the provider's reference for each one.

## Integrations

It calls the NotificationsAPI on a declined authorization, so the customer hears about a decline even when checkout has already returned.

PaymentsService is maintained by the same team as BillingService.

## Configuration

It is configured by PAYMENT_API_KEY and CAPTURE_TIMEOUT. CAPTURE_TIMEOUT is in seconds and defaults to 30.

## Operations

Calls to the provider are retried on network errors only, never on a decline, because retrying a decline can trigger the provider's fraud checks.
