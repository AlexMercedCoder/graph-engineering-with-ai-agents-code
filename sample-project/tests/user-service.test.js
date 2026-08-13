import { test } from 'node:test';
import assert from 'node:assert/strict';
import { listActiveUsers, findUser } from '../src/services/user-service.js';

test('listActiveUsers excludes soft-deleted users', (t, done) => {
  listActiveUsers((err, users) => {
    assert.equal(err, null);
    assert.equal(users.length, 2);
    assert.ok(users.every((u) => u.deleted_at === null));
    done();
  });
});

test('findUser returns null for an unknown id', (t, done) => {
  findUser(999, (err, user) => {
    assert.equal(err, null);
    assert.equal(user, null);
    done();
  });
});
