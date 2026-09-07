from dataclasses import dataclass

import pytest

from order_stream_service import CheckoutRequest, checkout_events


@dataclass
class Delta:
    content: str | None


@dataclass
class Choice:
    delta: Delta


@dataclass
class Chunk:
    choices: list[Choice]


class FakeCompletions:
    def create(self, **kwargs):
        assert kwargs["model"] == "auto"
        assert kwargs["stream"] is True
        return [Chunk([Choice(Delta("Ready "))]), Chunk([Choice(Delta("for pickup."))])]


class FakeClient:
    class chat:
        completions = FakeCompletions()


def test_checkout_confirms_order_after_stream():
    events = list(checkout_events(CheckoutRequest("ord-7", "Ring bell"), FakeClient()))
    assert '"type": "assistant_delta"' in events[0]
    assert '"state": "confirmed"' in events[-1]
    assert '"receipt": "Ready for pickup."' in events[-1]


def test_unknown_fulfillment_is_rejected_before_network_call():
    with pytest.raises(ValueError, match="standard or express"):
        list(checkout_events(CheckoutRequest("ord-7", "", "drone"), FakeClient()))

