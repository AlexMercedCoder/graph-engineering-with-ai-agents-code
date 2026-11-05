# AuditService

## Overview

AuditService records every governed data access. Each record holds the caller, the dataset, the columns returned, and the policy decision that allowed or denied the access.

## Data

AuditService stores records in the audit Iceberg table. Records are append-only and are retained for seven years.

## Integrations

It depends on the user service for identity resolution: a record carries the resolved user, not the raw token.

## Operations

Writes are buffered for up to five seconds and flushed in batches. If a flush fails, the buffer is retried with exponential backoff until it succeeds, and the service stops accepting new events after ten minutes of failed flushes, so an outage is visible rather than silent.
