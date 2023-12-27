def sorted_keystr(items,key,reverse=None):

    from operator import itemgetter

    key_str = "_tmp_sort_{}-str".format(str(key))

    for item in items:
        item[key_str] = str(item[key])

    new_items = sorted(items,
                       key=itemgetter(key_str),
                       reverse=reverse)

    for new_item in new_items:
        del new_item[key_str]

    return new_items

def _get_delete_resources(stack, stackargs, keep_resource_ids=None):

    parallel_overides = []
    parallel_resources = []
    sequentialize_resources = []
    added_ids = []

    ref_schedule_ids = stack.to_list(stack.ref_schedule_ids)

    for ref_schedule_id in ref_schedule_ids:

        _resources = stack.get_resource(ref_schedule_id=ref_schedule_id)

        if not _resources:
            continue

        for _resource in _resources:
            _id = _resource["_id"]
            if _id in added_ids:
                continue
            if keep_resource_ids and _id in keep_resource_ids:
                continue
            added_ids.append(_id)

            if _resource.get("query_only") or _resource.get("parent"):
                parallel_resources.append(_resource)
                continue

            try:
                _resource["checkin"] = int(_resource["checkin"])
            except:
                # just set it to pass so it gets added last
                _resource["checkin"] = 1000000000

            sequentialize_resources.append(_resource)

    stack.logger.debug("parallel_resources ids {}".format(
        [_r["_id"] for _r in parallel_resources]))
    stack.logger.debug("sequentialize_resources ids {}".format(
        [_r["_id"] for _r in sequentialize_resources]))

    if parallel_resources:
        parallel_overides.extend(parallel_resources)
    if sequentialize_resources:
        parallel_overides.extend(sequentialize_resources)

    results = {"parallel_resources": parallel_resources,
               "parallel_overides": parallel_overides,
               "sequentialize_resources": sorted_keystr(sequentialize_resources, 
                                                        key="checkin", 
                                                        reverse=True),
               "added_ids": added_ids}

    return results


def _get_keep_resources(stack, stackargs):

    # Gather the id for the keep resources
    if not stack.get_attr("keep_resources"):
        return

    _resources = stack.to_json(stack.keep_resources)
    stack.logger.debug("keep resources first include {}".format(_resources))

    _resource_ids = []

    for _resource in _resources:
        for ref_schedule_id in stack.ref_schedule_ids:
            _resource["ref_schedule_id"] = ref_schedule_id
            stack.logger.debug("searching for keep resource {}".format(_resource))
            resources = stack.get_resource(**_resource)
            if not resources:
                continue

            for resource in resources:
                stack.logger.debug("keep resource id {}".format(resource["_id"]))
                _resource_ids.append(resource["_id"])

    stack.logger.debug("keep resource ids {}".format(_resource_ids))

    return _resource_ids


def run(stackargs):

    #from time import sleep

    stack = newStack(stackargs)

    # required stack args
    stack.parse.add_required(key="keep_resources", default="null")
    stack.parse.add_required(key="ref_schedule_ids")
    stack.parse.add_optional(key="parallel_overide", default="null")

    # Initialize Variables in stack
    stack.init_variables()

    keep_resource_ids = _get_keep_resources(stack, 
                                            stackargs)

    all_resources = _get_delete_resources(stack, 
                                          stackargs, 
                                          keep_resource_ids=keep_resource_ids)

    stack.set_parallel()

    # parallel overide set True
    if stack.get_attr("parallel_overide") and all_resources.get("parallel_overides"):

        stack.logger.debug("Parallel overide set True")
        stack.logger.debug("Executing destroy resources in parallel")

        for resource in all_resources["parallel_overides"]:

            stack.logger.debug("removing resource {}".format(resource))

            stack.remove_resource(ref_only=None, 
                                  **resource)

        return stack.get_results(None)

    # parallel and sequential
    if all_resources.get("parallel_resources"):

        for resource in all_resources["parallel_resources"]:

            stack.logger.debug("removing resource {}".format(resource))

            stack.remove_resource(ref_only=None, 
                                  **resource)

    # Set unset_parallel
    stack.unset_parallel()

    # Wait until all actions complete
    stack.wait_all()

    for resource in all_resources["sequentialize_resources"]:

        stack.logger.debug("removing resource {}".format(resource))

        stack.remove_resource(ref_only=None, 
                              **resource)

    return stack.get_results(None)
