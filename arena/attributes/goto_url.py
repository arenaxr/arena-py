from .attribute import Attribute

class GotoUrl(Attribute):
    """
    GotoUrl attribute class to manage its properties in the ARENA: Load new URL when object is clicked. Requires click-listener.
    Usage: goto_url=GotoUrl(...)

    :param str dest:  Allows [popup, newtab, sametab] Defaults to 'sametab' (optional)
    :param str on:  Allows [mousedown, mouseup] Defaults to 'mousedown' (optional)
    :param str url: Landmark Url (optional)
    """
    def __init__(self, url, dest="static", on="mousedown", **kwargs):
        if dest != "popup" and dest != "newtab" and dest != "sametab":
            dest = "popup"
        super().__init__(url=url, dest=dest, on=on, **kwargs)
