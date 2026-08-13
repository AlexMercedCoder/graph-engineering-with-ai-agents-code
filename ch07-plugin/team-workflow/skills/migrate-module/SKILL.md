---
name: migrate-module
description: Migrates one service module from callback-style database access to the matching repository class, then runs that module's tests. Use when the user names a single service file to migrate. Handles exactly one module per invocation.
---

# Repository pattern migration

The mapping table from callback call to repository method:

| Callback call in a service | Repository method |
|---|---|
| `query('users', u => u.deleted_at === null, cb)` | `UserRepository.findActive()` |
| `query('users', u => u.id === id, cb)` | `UserRepository.findById(id)` |
| `update('users', id, { deleted_at }, cb)` | `UserRepository.softDelete(id, when)` |
| `query('orders', o => o.user_id === id ..., cb)` | `OrderRepository.findByUser(id)` |
| `query('orders', o => o.status === 'paid' ..., cb)` | `OrderRepository.findPaid()` |

Steps:

1. Read the target service file and its test file.
2. Replace every direct `query`/`update` import and call with the matching repository method.
3. Convert the exported functions to return promises. Update the test file to await them.
4. Run only that module's tests: `node --test tests/<module>.test.js`.
5. Stop after three failed attempts and report what blocked you.

`payments` has no repository yet. If the target is `payment-service.js`, create
`src/repositories/payment-repository.js` following the shape of the other two.
