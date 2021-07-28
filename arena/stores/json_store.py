import jq

from .arena_store import Store

class JSON(Store):
    """
    Class for JSON in the ARENA.
    """
    object_type = "json"

    def __init__(self, json_data={}, **kwargs):
        super().__init__(object_type=JSON.object_type, json_data=json_data, **kwargs)
        self.last_updates = []

    def update_store(self, **kwargs):
        jq_updates = kwargs.get("jq_updates", [])
        self.last_updates = jq_updates # So update handler can see changes
        new_data = self.data.json_data
        for update in jq_updates:
            new_data = jq.compile(update).input(new_data)
            new_data = (new_data.all())[0]
        self.data.json_data = new_data

        if self.update_handler:
            self.update_handler(self)

        return {"jq_updates": jq_updates}
