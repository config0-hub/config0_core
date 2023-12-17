def run(stackargs):

    #from time import sleep

    stack = newStack(stackargs)

    stack.parse.add_required(key="destroy_resources", default="null")
    stack.parse.add_required(key="keep_resources", default="null")
    stack.parse.add_required(key="ref_schedule_id")

    # Initialize Variables in stack
    stack.init_variables()

    # If there are no resources for the schedule id, we completed
    if not stack.get_resource(ref_schedule_id=stack.ref_schedule_id):
        stack.logger.warn("There are no resources to delete for schedule {}".format(stack.ref_schedule_id))
        return stack.get_results(None)

    # Delete destroy resources as specified and in order
    if stack.get_attr("destroy_resources"):

        destroy_resources = stack.to_json(stack.destroy_resources)

        stack.logger.debug("destroy resources include {}".format(destroy_resources))

        for destroy_resource in destroy_resources:

            destroy_resource["ref_schedule_id"] = stack.ref_schedule_id

            resources = stack.get_resource(**destroy_resource)

            if not resources:
                continue

            for resource in resources:

                # put this in as an order so it's no blocking?
                stack.logger.debug("removing resource {}".format(resource))

                stack.remove_resource(ref_only=None, 
                                      **resource)

    # Determine if any other resource exists
    all_resources = stack.get_resource(ref_schedule_id=stack.ref_schedule_id)

    if not all_resources:
        stack.logger.warn("There are no other resources to delete for schedule {}".format(
            stack.ref_schedule_id))
        return stack.get_results(None)

    # See if there are any keep resources
    keep_resource_ids = []

    # Gather the id for the keep resources
    if stack.get_attr("keep_resources"):
        keep_resources = stack.to_json(stack.keep_resources)
        stack.logger.debug("keep resources first include {}".format(keep_resources))

        for keep_resource in keep_resources:
            keep_resource["ref_schedule_id"] = stack.ref_schedule_id
            stack.logger.debug("searching for keep resource {}".format(keep_resource))
            resources = stack.get_resource(**keep_resource)

            if not resources:
                continue

            for resource in resources:

                stack.logger.debug("keep resource id {}".format(resource["_id"]))

                keep_resource_ids.append(resource["_id"])

    stack.logger.debug("keep resource ids {}".format(keep_resource_ids))

    # Remove keep resource ids
    # we ignore ones with a parent, since
    # the parent will destroy its children
    remaining_resources = []

    for resource in all_resources:

        if resource.get("parent"):
            stack.logger.debug(
                "resource name {} has a parent ...skipping".format(resource.get("name")))
            continue

        if resource["_id"] in keep_resource_ids:
            continue

        remaining_resources.append(resource)

    stack.logger.debug("remaining_resources {}".format(remaining_resources))

    if not remaining_resources:
        stack.logger.warn("There are no other remaining resources to delete for schedule {}".format(
            stack.ref_schedule_id))
        return stack.get_results(None)

    # Delete remaining resources if any exists
    for resource in remaining_resources:
        stack.logger.debug("delete resources {}".format(resource))
        # put this in as an order so it's not blocking?
        stack.remove_resource(ref_only=None, **resource)

    return stack.get_results(None)
