class EventDispatcher:

    def __init__(self):
        self.handlers = {}

    def register(
        self,
        event_type,
        handler,
    ):
        self.handlers.setdefault(
            event_type,
            [],
        ).append(handler)

    def dispatch(self, event):

        for handler in self.handlers.get(type(event), []):

            handler(event)