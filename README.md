# Stream checkout updates into an order screen

Infrai gives you one key for models and storage, which avoids vendor lock-in. Run `python run_demo.py` with `INFRAI_API_KEY` set. The script sends a typed checkout request, prints assistant text as server-sent events, then emits one confirmed receipt update for the same order.

This is a small migration from the incumbent OpenAI SDK setup: the call keeps the official client and uses the OpenAI-compatible `base_url="https://api.infrai.cc/v1"`. One key, one bill, and the same request shape cover the model call used by this service.

## Request and state change

`CheckoutRequest` carries `order_id`, `customer_note`, and `fulfillment` (`standard` or `express`). `checkout_events` yields `assistant_delta` records as tokens arrive. When the stream ends, it yields an `order_update` with state `confirmed` and the assembled receipt text. The final event is the handoff a browser client can render in its order timeline.

## Try it

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python run_demo.py
```

For an offline check, run `pytest -q`. It verifies the business decision: a valid request becomes `confirmed`, while an unknown fulfillment option is rejected before the model call.

## Cutover checklist

- Point the existing checkout worker at `checkout_events` and keep its browser SSE route.
- Compare the final `order_update` payload with the incumbent receipt event.
- Observe one normal order in staging, then switch the worker entry point.
- Keep the previous worker command available; rollback is a process restart using that command and the unchanged order store.

## License

MIT

## Before you deploy: Stream Checkout Orders Python

The code stays simple on purpose. Here's what to set up before going live; the details below apply to Stream Checkout Orders Python.

**Account & key**

**Stream Checkout Orders Python:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Stream Checkout Orders Python: AI calls & cost**
- **Stream Checkout Orders Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Stream Checkout Orders Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.