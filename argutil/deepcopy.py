def deepcopy(obj):
    if isinstance(obj, dict):
        return deepcopy_dict(obj)
    elif isinstance(obj, list):
        return deepcopy_list(obj)
    elif isinstance(obj, set):
        return deepcopy_set(obj)
    else:
        return obj


def deepcopy_dict(obj):
    return {
        deepcopy(k): deepcopy(v) for k, v in obj.items()
    }


def deepcopy_list(obj):
    return [deepcopy(v) for v in obj]


def deepcopy_set(obj):
    return {deepcopy(v) for v in obj}
