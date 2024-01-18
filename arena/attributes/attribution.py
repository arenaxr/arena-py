from .attribute import Attribute


class Attribution(Attribute):
    """
    Attribution attribute class to manage its properties in the ARENA: Attribution Component. Saves attribution data in any entity.
    Usage: attribution=Attribution(...)
    
    :param str author: Author name; e.g. “Vaptor-Studio”; defaults to 'Unknown' (optional)
    :param str authorURL: Author homepage/profile; e.g. https://sketchfab.com/VapTor (optional)
    :param str license: License summary/short name; e.g. “CC-BY-4.0”.; defaults to 'Unknown' (optional)
    :param str licenseURL: License URL; e.g. http://creativecommons.org/licenses/by/4.0/ (optional)
    :param str source: Model source e.g. “Sketchfab”.; defaults to 'Unknown' (optional)
    :param str sourceURL: Model source URL; e.g. https://sketchfab.com/models/2135501583704537907645bf723685e7 (optional)
    :param str title: Model title; e.g. “Spinosaurus”.; defaults to 'No Title' (optional)
    :param bool extractAssetExtras: Extract attribution info from asset extras; will override attribution info given (default: true); defaults to 'True' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
