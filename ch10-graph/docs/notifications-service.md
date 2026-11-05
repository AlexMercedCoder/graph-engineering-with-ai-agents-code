# NotificationsService

## Overview

NotificationsService exposes the NotificationsAPI. Any service that needs to send an email, an SMS, or a push message hands it to this API instead of talking to a provider directly.

## Data

It stores queued messages in the notifications Redis instance. A message stays queued until a provider accepts it or its retries run out.

## Delivery and retries

Its retry semantics are three attempts with a 250ms backoff, configured by RETRY_ATTEMPTS. A message that fails all three attempts moves to the dead-letter list, and the caller is not told. Callers that need confirmation poll the message status.

## Operations

Provider credentials rotate monthly. During a rotation the queue keeps accepting messages and holds them until the new credentials load.
