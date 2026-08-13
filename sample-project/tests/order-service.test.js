import { test } from 'node:test';
import assert from 'node:assert/strict';
import { listOrdersForUser, totalPaidCents } from '../src/services/order-service.js';

test('listOrdersForUser returns only that user orders', (t, done) => {
  listOrdersForUser(1, (err, orders) => {
    assert.equal(err, null);
    assert.equal(orders.length, 2);
    assert.ok(orders.every((o) => o.user_id === 1));
    done();
  });
});

test('totalPaidCents counts only paid orders', (t, done) => {
  totalPaidCents((err, total) => {
    assert.equal(err, null);
    assert.equal(total, 4200 + 9900 + 500);
    done();
  });
});
