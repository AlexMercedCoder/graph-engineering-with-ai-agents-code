# LedgerService

## Overview

LedgerService keeps the double-entry ledger that finance closes the books from. It records every authorization, capture, and refund as a pair of entries, and the finance team reads its month-end export.

## Integrations

It depends on PaymentsService for payment events and calls the PaymentsAPI directly to look up the status of an authorization it hasn't seen captured.

## Configuration

It is configured by AUTH_HOLD_MINUTES, which it uses to decide when an uncaptured authorization has lapsed and its pending entry should be reversed.

## Operations

A reversal posted for a hold that later captures is corrected the next morning by the reconciliation job, and finance sees both entries in the month-end export.
