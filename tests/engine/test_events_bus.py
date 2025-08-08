from src.engine.events import SimpleEventBus, make_event, RUN_START

def test_simple_event_bus_publish_subscribe():
    bus = SimpleEventBus()
    seen = []
    def handler(ev):
        seen.append(ev.name)
    bus.subscribe(handler)
    bus.publish(make_event(RUN_START, {"x": 1}))
    assert RUN_START in seen
