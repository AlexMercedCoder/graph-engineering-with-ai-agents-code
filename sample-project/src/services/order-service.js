import { query } from '../db.js';

// Callback-style database access. Chapter 5 migrates this to OrderRepository.
export function listOrdersForUser(userId, callback) {
  query('orders', (o) => o.user_id === userId && o.deleted_at === null, callback);
}

export function totalPaidCents(callback) {
  query('orders', (o) => o.status === 'paid' && o.deleted_at === null, (err, rows) => {
    if (err) return callback(err);
    callback(null, rows.reduce((sum, o) => sum + o.total_cents, 0));
  });
}
