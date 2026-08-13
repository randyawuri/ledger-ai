from collections import defaultdict


class EventBus:

    def __init__(self):

        self._handlers = defaultdict(list)

    def subscribe(
        self,
        event,
        handler,
    ):
        self._handlers[event].append(handler)

    def publish(
        self,
        event,
    ):
        for handler in self._handlers[type(event)]:

            handler(event)