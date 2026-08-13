// A router with no framework, so the project has an HTTP surface to survey
// in Chapter 1's rate-limiting example without an Express dependency.
import { listActiveUsers, findUser } from '../services/user-service.js';
import { listOrdersForUser, totalPaidCents } from '../services/order-service.js';
import { uncapturedTotalCents } from '../services/payment-service.js';

export const routes = [
  { method: 'GET', path: '/users', handler: (req, cb) => listActiveUsers(cb) },
  { method: 'GET', path: '/users/:id', handler: (req, cb) => findUser(Number(req.params.id), cb) },
  { method: 'GET', path: '/users/:id/orders', handler: (req, cb) => listOrdersForUser(Number(req.params.id), cb) },
  { method: 'GET', path: '/reports/paid-total', handler: (req, cb) => totalPaidCents(cb) },
  { method: 'GET', path: '/reports/uncaptured-total', handler: (req, cb) => uncapturedTotalCents(cb) },
];

export function listEndpoints() {
  return routes.map((r) => `${r.method} ${r.path}`);
}
