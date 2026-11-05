# Gate checks

`check.txt` is `tools/check-gates.py` against `server/http_server.py`, including a JSON-RPC batch carrying the out-of-scope call. `no-audience-check.txt` is the same run against a copy whose `verify_token` skips the audience comparison (`if entry is None:`) and listens on port 8775: check 2 fails because the server lets a token issued for `https://billing.example.com/mcp` past authentication and the tool answers it.
