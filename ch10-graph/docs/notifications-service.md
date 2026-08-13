# NotificationsService
NotificationsService exposes the NotificationsAPI. It stores queued messages in
the notifications Redis instance. Its retry semantics are three attempts with a
250ms backoff, configured by RETRY_ATTEMPTS.
