import { query } from '../db.js';

export class OrderRepository {
  findByUser(userId) {
    return new Promise((resolve, reject) => {
      query('orders', (o) => o.user_id === userId && o.deleted_at === null,
        (err, rows) => (err ? reject(err) : resolve(rows)));
    });
  }

  findPaid() {
    return new Promise((resolve, reject) => {
      query('orders', (o) => o.status === 'paid' && o.deleted_at === null,
        (err, rows) => (err ? reject(err) : resolve(rows)));
    });
  }
}
