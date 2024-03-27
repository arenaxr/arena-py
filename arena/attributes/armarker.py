from .attribute import Attribute


class Armarker(Attribute):
    """
    Armarker attribute class to manage its properties in the ARENA: A location marker (such as an AprilTag, a lightAnchor, or an UWB tag), used to anchor scenes, or scene objects, in the real world.
    Usage: `armarker=Armarker(...)`

    :param bool buildable: Whether tag has 'dynamic' toggled on click. Used to position a tag, then lock into position. (optional)
    :param bool dynamic: Dynamic tag, not used for localization. E.g., to move object to which this ARMarker component is attached to. Requires permissions to update the scene (if dynamic=true). (optional)
    :param float ele: Tag elevation in meters. (optional)
    :param float lat: Tag latitude. (optional)
    :param float long: Tag longitude. (optional)
    :param str markerid: The marker id (e.g. for AprilTag 36h11 family, an integer in the range [0, 586]). Defaults to '0' (optional)
    :param str markertype: The marker type, technology-based. Allows [apriltag_36h11, lightanchor, uwb, vive, optitrack] Defaults to 'apriltag_36h11' (optional)
    :param bool publish: Publish detections. Send detections to external agents (e.g. external builder script that places new markers in the scene). If dynamic=true and publish=true, object position is not updated (left up to external agent). (optional)
    :param float size: Tag size in millimeters. Defaults to '150' (optional)
    :param str url: URL associated with the tag. (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
