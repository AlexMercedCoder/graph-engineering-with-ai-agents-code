import { query } from '../db.js';

// Callback-style database access. Chapter 5 migrates this to a PaymentRepository
// the reader adds, which is the part of the exercise with no worked answer.
export function findPaymentsForOrder(orderId, callback) {
  query('payments', (p) => p.order_id === orderId, callback);
}

export function uncapturedTotalCents(callback) {
  query('payments', (p) => p.captured === false, (err, rows) => {
    if (err) return callback(err);
    callback(null, rows.reduce((sum, p) => sum + p.amount_cents, 0));
  });
}
