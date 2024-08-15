def convert_bytes(size_in_bytes: int) -> str:
    """Convert bytes to a human-readable string format (KB, MB, GB, etc.)."""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    size = size_in_bytes
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1

    return f"{size:.2f} {units[unit_index]}"


def fix_dict(
    reference_dict: dict, target_dict: dict, remove: bool = False
) -> tuple[dict, bool]:
    """Fix a dictionary to match a default dictionary.

    Make sure the target dictionary has all the keys of the default dictionary.
    True = dictionary is valid
    False = dictionary needed fixing
    """

    if not isinstance(target_dict, dict):
        target_dict = reference_dict
        return target_dict, False

    ret_val = True
    # add missing keys
    for key, value in reference_dict.items():
        if target_dict.get(key) is None:
            target_dict[key] = value
            ret_val = False
    # remove extra keys
    if remove:
        keys_to_remove = [key for key in target_dict if key not in reference_dict]
        for key in keys_to_remove:
            del target_dict[key]
            ret_val = False

    return target_dict, ret_val
