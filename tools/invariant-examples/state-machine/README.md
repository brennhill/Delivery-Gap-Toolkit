# State Machine

Invariant test suite proving that an order state machine enforces valid transitions and prevents backward or skipped states.

## How AI fails

AI generates a `set_status()` method that accepts any status string. There are no guards: orders can go from "delivered" back to "pending", or skip from "pending" directly to "delivered" without passing through "paid" and "shipped".

## The correct pattern

Define an explicit transition map (`VALID_TRANSITIONS`) and a `transition()` method that checks it. If the requested transition is not in the map, raise `InvalidTransition`. Use a lock to serialize concurrent transitions on the same order.

## Tests

| Test | Invariant |
|------|-----------|
| `test_valid_forward_transitions` | pending -> paid -> shipped -> delivered succeeds |
| `test_backward_transition_rejected` | delivered -> paid raises InvalidTransition |
| `test_skip_transition_rejected` | pending -> delivered raises InvalidTransition |
| `test_concurrent_transitions` | Two threads racing on the same order -> state is consistent |
| `test_terminal_state_is_final` | delivered -> anything raises InvalidTransition |

## Run

```bash
pytest test_state_machine.py -v
```

## Production note

Replace the `threading.Lock` with a database conditional update: `UPDATE orders SET status = $new WHERE id = $id AND status = $old`. If zero rows are affected, the transition was invalid or another thread already moved the state. The invariant is the same: check-and-set must be atomic.
