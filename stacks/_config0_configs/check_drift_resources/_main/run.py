def run(stackargs):

    stack = newStack(stackargs)

    stack.parse.add_required(key="drift_protection",
                             default="True")

    stack.parse.add_optional(key="ref_schedule_id",
                             default="null")

    stack.parse.add_optional(key="resource_type",
                             default="null")

    stack.add_substack('config0-publish:::config0_core::check_drift_resource')

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_substacks()

    if stack.drift_protection:
        match = {"drift_protection":True}
    else:
        match = {}

    if stack.ref_schedule_id:
        match["schedule_id"] = stack.ref_schedule_Id

    if stack.resource_type:
        match["resource_type"] = stack.resource_type

    resources_to_chk = stack.get_resource(match=match)

    if not resources_to_chk:
        stack.logger.warn("There are no other resources to validate for drift")
        return stack.get_results()

    stack.set_parallel()

    for resource in resources_to_chk:
        inputargs = {
            "overide_values": {
                "resource_id":resource["id"],
            },
            "automation_phase":"infrastructure",
            "human_description":f'check drift {resource.get("name")}',
            "display":True
        }
        stack.check_drift_resource.insert(**inputargs)

    stack.wait_to_complete()

    return stack.get_results()
