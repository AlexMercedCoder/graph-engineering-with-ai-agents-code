import { test } from 'node:test';
import assert from 'node:assert/strict';
import { UserRepository } from '../src/repositories/user-repository.js';
import { OrderRepository } from '../src/repositories/order-repository.js';

test('UserRepository.findActive matches the service behaviour', async () => {
  const users = await new UserRepository().findActive();
  assert.equal(users.length, 2);
});

test('OrderRepository.findPaid matches the service behaviour', async () => {
  const orders = await new OrderRepository().findPaid();
  assert.equal(orders.length, 3);
});
