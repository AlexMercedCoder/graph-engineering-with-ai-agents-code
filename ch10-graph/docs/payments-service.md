# PaymentsService
PaymentsService exposes the PaymentsAPI. It calls the NotificationsAPI on a
declined authorization. It is configured by PAYMENT_API_KEY and CAPTURE_TIMEOUT.
It stores authorizations in the payments Postgres database.
