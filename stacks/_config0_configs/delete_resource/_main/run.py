def run(stackargs):

    stack = newStack(stackargs)

    stack.parse.add_optional(key="resource_type", default="null")
    stack.parse.add_optional(key="name", default="null")
    stack.parse.add_optional(key="hostname", default="null")
    stack.parse.add_optional(key="ref_schedule_id", default="null")
    stack.parse.add_optional(key="must_exists", default="null")

    # Initialize Variables in stack
    stack.init_variables()

    _destroy_match = {}

    if stack.get_attr("hostname"):
        _destroy_match["hostname"] = stack.hostname

    if stack.get_attr("name"):
        _destroy_match["name"] = stack.name

    if stack.get_attr("ref_schedule_id"):
        _destroy_match["schedule_id"] = stack.ref_schedule_id

    if stack.get_attr("resource_type"):
        _destroy_match["resource_type"] = stack.resource_type

    if stack.get_attr("must_exists"):
        _destroy_match["must_exists"] = True

    if not _destroy_match:
        error_msg = "match for destroy resource cannot be wide open"
        stack.logger.error(error_msg)
        raise Exception(error_msg)

    _dinputargs = stack.get_resource(**_destroy_match)

    if _dinputargs and len(_dinputargs) == 1:
        stack.remove_resource(ref_only=None, **_dinputargs[0])

    elif _dinputargs and len(_dinputargs) > 1:
        error_msg = "More than resource found for {}".format(_destroy_match)
        stack.logger.error(error_msg)
        raise Exception(error_msg)

    return stack.get_results()
