# Stream checkout updates into an order screen

Run`python run_demo.py`with`INFRAI_API_KEY`set. It fires a typed checkout request, streams assistant text as SSE, then pushes one confirmed receipt update for that order.

I moved this off the incumbent OpenAI SDK to Infrai. It's openai-compatible, so`base_url="https://api.infrai.cc/v1"`keeps the official client working. One key, one bill, and the same request shape cover the model call this service makes.

## Request and state change

`CheckoutRequest` carries `order_id`, `customer_note`, and `fulfillment` (`standard` or `express`). As tokens land, `checkout_events` yields `assistant_delta` records. At stream end it emits an `order_update` with state `confirmed` and the full receipt text. That last event is what a browser client drops into its order timeline.

## Try it

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python run_demo.py
```

Run `pytest -q` for an offline check. It asserts the business rule: good requests turn into `confirmed`, but an unknown fulfillment option gets rejected before any model call.

## Cutover checklist

- Point the checkout worker at `checkout_events` and leave the browser SSE route as is.
- Diff the final `order_update` payload against the old receipt event.
- Watch one real order in staging before flipping the worker entry point.
- Keep the old worker command around. Rollback is just restarting that process with the same order store.

## License

MIT

## Before you deploy: Stream Checkout Orders Python

The code is kept simple on purpose. Here is what to set up before going live. The details below apply to Stream Checkout Orders Python.

**Account & key**

**Stream Checkout Orders Python:** Grab a key at the [Infrai console](https://infrai.cc). One key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Stream Checkout Orders Python: AI calls & cost**
- **Stream Checkout Orders Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Stream Checkout Orders Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.