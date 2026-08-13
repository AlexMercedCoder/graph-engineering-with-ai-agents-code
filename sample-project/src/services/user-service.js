import { query, update } from '../db.js';

// Callback-style database access. Chapter 5 migrates this to UserRepository.
export function listActiveUsers(callback) {
  query('users', (u) => u.deleted_at === null, callback);
}

export function findUser(id, callback) {
  query('users', (u) => u.id === id, (err, rows) => {
    if (err) return callback(err);
    callback(null, rows[0] ?? null);
  });
}

export function softDeleteUser(id, when, callback) {
  update('users', id, { deleted_at: when }, callback);
}
