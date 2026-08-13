import { query } from '../db.js';

// Callback-style database access. Chapter 5 migrates this to UserRepository.
export function findByEmail(email, callback) {
  query('users', (u) => u.email === email && u.deleted_at === null, (err, rows) => {
    if (err) return callback(err);
    callback(null, rows[0] ?? null);
  });
}

export function isActive(email, callback) {
  findByEmail(email, (err, user) => {
    if (err) return callback(err);
    callback(null, Boolean(user));
  });
}
