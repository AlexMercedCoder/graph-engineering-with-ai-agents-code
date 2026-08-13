// A deliberately tiny in-memory database with a callback API.
// The callback style is the point: Chapter 5 migrates the service layer off it.

const tables = {
  users: [
    { id: 1, email: 'ada@example.com', name: 'Ada', deleted_at: null },
    { id: 2, email: 'grace@example.com', name: 'Grace', deleted_at: null },
    { id: 3, email: 'alan@example.com', name: 'Alan', deleted_at: '2026-01-04' },
  ],
  orders: [
    { id: 10, user_id: 1, total_cents: 4200, status: 'paid', deleted_at: null },
    { id: 11, user_id: 1, total_cents: 1350, status: 'quote', deleted_at: null },
    { id: 12, user_id: 2, total_cents: 9900, status: 'paid', deleted_at: null },
    { id: 13, user_id: 3, total_cents: 500, status: 'paid', deleted_at: null },
  ],
  payments: [
    { id: 100, order_id: 10, amount_cents: 4200, captured: true },
    { id: 101, order_id: 12, amount_cents: 9900, captured: false },
  ],
};

export function reset() {
  tables.users[2].deleted_at = '2026-01-04';
  tables.orders.forEach((o) => { o.deleted_at = null; });
}

// Old-style callback query. Accepts a table name and a predicate.
export function query(table, predicate, callback) {
  setImmediate(() => {
    const rows = tables[table];
    if (!rows) return callback(new Error(`no such table: ${table}`));
    try {
      callback(null, rows.filter(predicate).map((r) => ({ ...r })));
    } catch (err) {
      callback(err);
    }
  });
}

export function update(table, id, patch, callback) {
  setImmediate(() => {
    const row = (tables[table] || []).find((r) => r.id === id);
    if (!row) return callback(new Error(`no row ${id} in ${table}`));
    Object.assign(row, patch);
    callback(null, { ...row });
  });
}
