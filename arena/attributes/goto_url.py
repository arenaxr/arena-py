from .attribute import Attribute

class GotoUrl(Attribute):
    """
    GotoUrl Attribute.
    Usage: goto_url=GotoUrl(...)
    """
    def __init__(self, url, dest="static", on="mousedown"):
        if dest != "popup" and dest != "newtab" and dest != "sametab":
            dest = "popup"
        super().__init__(url=url, dest=dest, on=on)
