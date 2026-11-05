# SearchService

## Overview

SearchService indexes orders for the storefront, so customers can search their own order history by product, date, or status.

## Integrations

It depends on OrderService and reads order changes from it every minute.

## Data

It stores its index in the search OpenSearch cluster. The index can be rebuilt from OrderService at any time and is never backed up.

## Operations

A failed reindex batch is retried five times with a ten-second delay, then skipped and logged. Skipped batches are picked up by the nightly full rebuild.
