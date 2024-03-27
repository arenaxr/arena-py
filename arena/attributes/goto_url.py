from .attribute import Attribute

class GotoUrl(Attribute):
    """
    GotoUrl attribute class to manage its properties in the ARENA: Load new URL when object is clicked. Requires click-listener.
    Usage: `goto_url=GotoUrl(...)`

    :param str dest: Where to open the URL. Allows [popup, newtab, sametab] Defaults to 'sametab' (optional)
    :param str on: A case-sensitive string representing the event type to listen for. See <https://developer.mozilla.org/en-US/docs/Web/Events> Web Events. Allows [mousedown, mouseup] Defaults to 'mousedown' (optional)
    :param str url: The destination url, e.g. https://example.com. (optional)
    """
    def __init__(self, url, dest="static", on="mousedown", **kwargs):
        if dest != "popup" and dest != "newtab" and dest != "sametab":
            dest = "popup"
        super().__init__(url=url, dest=dest, on=on, **kwargs)
