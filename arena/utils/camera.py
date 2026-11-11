def camera_username(camera_id):
    parts = camera_id.split("_", 2)
    if (
        len(parts) == 3
        and parts[0] == "camera"
        and len(parts[1]) == 10
        and parts[1].isdigit()
    ):
        return parts[2]
    return camera_id.rsplit("_", 1)[0] if "_" in camera_id else camera_id
