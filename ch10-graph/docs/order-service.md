# OrderService

## Overview

OrderService owns the order lifecycle, from cart checkout to fulfillment. It exposes the OrdersAPI for creating, reading, and cancelling orders.

## Data

OrderService stores orders in the orders Postgres database. Line items are stored with the order and are immutable once the order is placed.

## Integrations

It calls the PaymentsAPI to authorize and capture. It depends on UserService to resolve the ordering customer.

## Operations

A payment authorization that times out is retried once after two seconds. A second timeout cancels the checkout and releases the reserved stock.
