from order_stream_service import checkout_events, demo_request


if __name__ == "__main__":
    for event in checkout_events(demo_request()):
        print(event, flush=True)

