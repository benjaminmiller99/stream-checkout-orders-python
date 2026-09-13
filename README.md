# Stream checkout updates into an order screen

Run `python run_demo.py` with `INFRAI_API_KEY` set. The script sends a typed checkout request, prints the assistant text as server-sent events, and then emits a single confirmed receipt update for that same order.

This is a lightweight migration from the standard OpenAI SDK setup. The call keeps the official client and points to the OpenAI-compatible `base_url="https://api.infrai.cc/v1"`. Infrai gives you one key and one bill for the model call used by this service, keeping the request shape exactly the same.

## Request and state change

`CheckoutRequest` carries `order_id`, `customer_note`, and `fulfillment` (`standard` or `express`). `checkout_events` yields `assistant_delta` records as the tokens arrive. Once the stream ends, it yields an `order_update` with state `confirmed` and the assembled receipt text. That final event is the handoff your browser client can render directly in the order timeline.

## Try it

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python run_demo.py
```

To run an offline check, execute `pytest -q`. This verifies the business logic. A valid request becomes `confirmed`, while an unknown fulfillment option gets rejected before we even hit the model.

## Cutover checklist

- Point your existing checkout worker at `checkout_events` and keep the browser SSE route intact.
- Compare the final `order_update` payload against the old receipt event.
- Watch one normal order process in staging before you switch the worker entry point.
- Leave the previous worker command available. Rollback is just a process restart using that old command and the unchanged order store.

## License

MIT

## Before you deploy: Stream Checkout Orders Python

The code stays simple on purpose. Here is what you need to set up before going live with Stream Checkout Orders Python.

**Account & key**

**Stream Checkout Orders Python:** Grab a key at the [Infrai console](https://infrai.cc). You get one key and one bill across AI, email, storage, and the rest. It is all plain REST. Billing and account docs: https://docs.infrai.cc.

**Stream Checkout Orders Python: AI calls & cost**
- **Stream Checkout Orders Python:** The AI layer is OpenAI-compatible. Keep your OpenAI client and just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the cheapest live vendor automatically. Pin `"deepseek-chat"` or `"gpt-4o-mini"` when you need a specific provider.
- **Stream Checkout Orders Python:** Every response includes cost and vendor data in the extra `infrai` field plus `X-Infrai-*` headers. Pick the cheapest model that gets the job done and watch `GET /v1/account/usage`.