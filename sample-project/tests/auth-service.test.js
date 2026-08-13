import { test } from 'node:test';
import assert from 'node:assert/strict';
import { findByEmail, isActive } from '../src/services/auth-service.js';

test('findByEmail ignores soft-deleted users', (t, done) => {
  findByEmail('alan@example.com', (err, user) => {
    assert.equal(err, null);
    assert.equal(user, null);
    done();
  });
});

test('isActive is true for a live user', (t, done) => {
  isActive('ada@example.com', (err, active) => {
    assert.equal(err, null);
    assert.equal(active, true);
    done();
  });
});
