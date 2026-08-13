import { test } from 'node:test';
import assert from 'node:assert/strict';
import { findPaymentsForOrder, uncapturedTotalCents } from '../src/services/payment-service.js';

test('findPaymentsForOrder finds the payment for an order', (t, done) => {
  findPaymentsForOrder(10, (err, rows) => {
    assert.equal(err, null);
    assert.equal(rows.length, 1);
    assert.equal(rows[0].amount_cents, 4200);
    done();
  });
});

test('uncapturedTotalCents sums uncaptured payments', (t, done) => {
  uncapturedTotalCents((err, total) => {
    assert.equal(err, null);
    assert.equal(total, 9900);
    done();
  });
});
