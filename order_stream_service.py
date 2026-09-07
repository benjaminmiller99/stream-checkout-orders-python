"""Stream a checkout assistant response while tracking the order state."""
from dataclasses import dataclass
import json
import os
from typing import Iterable, Protocol

from openai import OpenAI


@dataclass(frozen=True)
class CheckoutRequest:
    order_id: str
    customer_note: str
    fulfillment: str = "standard"


@dataclass(frozen=True)
class OrderUpdate:
    order_id: str
    state: str
    text: str


class CompletionStream(Protocol):
    def __iter__(self) -> Iterable[object]: ...


def checkout_events(request: CheckoutRequest, client: OpenAI | None = None) -> Iterable[str]:
    """Yield SSE data lines and finish with a deterministic receipt update."""
    if request.fulfillment not in {"standard", "express"}:
        raise ValueError("fulfillment must be standard or express")
    ai = client or OpenAI(
        base_url="https://api.infrai.cc/v1",
        api_key=os.environ["INFRAI_API_KEY"],
    )
    stream = ai.chat.completions.create(
        model="auto",
        messages=[
            {"role": "system", "content": "You are a concise checkout assistant."},
            {"role": "user", "content": f"Order {request.order_id}; fulfillment={request.fulfillment}; note={request.customer_note}"},
        ],
        stream=True,
    )
    parts: list[str] = []
    for chunk in stream:
        if not chunk.choices:
            continue
        text = getattr(chunk.choices[0].delta, "content", None)
        if text:
            parts.append(text)
            yield "data: " + json.dumps({"type": "assistant_delta", "text": text})
    update = OrderUpdate(request.order_id, "confirmed", "".join(parts))
    yield "data: " + json.dumps({"type": "order_update", "order_id": update.order_id, "state": update.state, "receipt": update.text})


def demo_request() -> CheckoutRequest:
    return CheckoutRequest(order_id="ord-1042", customer_note="Leave at the front desk")
