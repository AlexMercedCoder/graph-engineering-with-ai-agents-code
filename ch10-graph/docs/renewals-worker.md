# RenewalsWorker

## Overview

RenewalsWorker re-bills subscriptions monthly. It runs as a scheduled job on the first of each month and works through every active subscription.

## Integrations

It depends on BillingService and calls the PaymentsAPI directly, without going through OrderService, because a renewal has no cart.

## Configuration

It is configured by AUTH_HOLD_MINUTES, which sets how long a renewal authorization is held before capture.

## Operations

A renewal whose authorization fails is retried on days three and seven. After the third failure the subscription is suspended and the customer is emailed through the normal billing receipt flow.
