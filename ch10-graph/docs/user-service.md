# UserService

## Overview

UserService owns users and soft deletes. It exposes the UsersAPI and validates the session tokens that the gateway forwards.

## Data

UserService stores users in the users Postgres database. A deleted user keeps their row with a deletion timestamp, so orders and audit records still resolve.

## Configuration

It is configured by ORDER_DB_URL for its read replica, a historical name kept because three deployment scripts read it.

## Operations

Token validation results are cached for sixty seconds. A token revoked inside that window is still accepted until the cache entry expires.
