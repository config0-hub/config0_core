def run(stackargs):

    stack = newStack(stackargs)

    stack.parse.add_required(key="resource_id")

    stack.parse.add_optional(key="resource_type",
                             default="null")

    stack.parse.add_optional(key="ref_schedule_id", 
                             default="null")

    # Initialize Variables in stack
    stack.init_variables()

    match = {"id":stack.resource_id}

    if stack.get_attr("ref_schedule_id"):
        match["schedule_id"] = stack.ref_schedule_id

    if stack.get_attr("resource_type"):
        match["resource_type"] = stack.resource_type

    resource = stack.get_resource(match=match)

    if resource and len(resource) == 1:
        stack.validate_resource(resource[0]["id"],
                                **resource[0])
    elif resource and len(resource) > 1:
        error_msg = "More than resource found for {}".format(match)
        stack.logger.error(error_msg)
        raise Exception(error_msg)

    return stack.get_results()
