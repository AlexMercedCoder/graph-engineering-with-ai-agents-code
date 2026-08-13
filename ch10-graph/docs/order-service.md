# OrderService
OrderService owns the order lifecycle. It stores orders in the orders Postgres
database. It calls the PaymentsAPI to authorize and capture. It depends on
UserService to resolve the ordering customer.
