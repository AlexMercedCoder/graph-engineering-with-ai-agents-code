# ApiGateway

## Overview

ApiGateway fronts every public endpoint. Clients never reach a service directly; every request enters through the gateway, which terminates TLS, applies rate limits per client key, and forwards the request to the owning service.

## Integrations

ApiGateway calls the OrdersAPI and the UsersAPI. It depends on the user service for token validation, so a request with an expired token is rejected at the edge before any service sees it.

ApiGateway and SearchService share the same on-call rotation, because both sit on the storefront's critical path.

## Configuration

Rate limits are read from GATEWAY_RATE_LIMITS at startup. Changing them requires a rolling restart.

## Operations

The gateway does not retry failed upstream requests. A 5xx from a service is passed to the client unchanged, and the client library decides whether to retry.
