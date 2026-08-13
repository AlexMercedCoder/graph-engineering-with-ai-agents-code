import { query, update } from '../db.js';

// The repository pattern the project is migrating toward: promise-based,
// one place per table, no query construction anywhere else.
export class UserRepository {
  findActive() {
    return new Promise((resolve, reject) => {
      query('users', (u) => u.deleted_at === null, (err, rows) =>
        err ? reject(err) : resolve(rows));
    });
  }

  findById(id) {
    return new Promise((resolve, reject) => {
      query('users', (u) => u.id === id, (err, rows) =>
        err ? reject(err) : resolve(rows[0] ?? null));
    });
  }

  softDelete(id, when) {
    return new Promise((resolve, reject) => {
      update('users', id, { deleted_at: when }, (err, row) =>
        err ? reject(err) : resolve(row));
    });
  }
}
