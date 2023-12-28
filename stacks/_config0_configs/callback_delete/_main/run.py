def run(stackargs):

    stack = newStack(stackargs)

    # required stack args
    stack.parse.add_required(key="parallel_ids", default="null")
    stack.parse.add_required(key="sequential_ids", default="null")
    stack.parse.add_required(
        key="keep_resources", default='[ {"provider":"aws","resource_type":"ecr_repo"} ]')

    # this is parallel overide to delete resources and schedules in parallel
    # we name it "parallel" to keep it simple
    stack.parse.add_optional(key="parallel", default="true")

    # Add substacks
    stack.add_substack('config0-hub:::config0-core::delete_schedules')
    stack.add_substack('config0-hub:::config0-core::delete_resources_by_time')
    # stack.add_substack('config0-hub:::config0-core::delete_resources')

    # Initialize
    stack.init_variables()
    stack.init_substacks()

    # Get all the schedule_ids
    ref_schedule_ids = stack.parallel_ids[:]
    ref_schedule_ids.extend(stack.sequential_ids[:])

    # Delete resources
    input_values = {"ref_schedule_ids": ref_schedule_ids}

    if stack.get_attr("keep_resources"):
        input_values["keep_resources"] = stack.keep_resources

    if stack.get_attr("parallel") not in ["None", "null", None, False, "false"]:
        input_values["parallel_overide"] = True

    inputargs = {"input_values": input_values}
    stack.delete_resources_by_time.insert(display=None, **inputargs)

    stack.wait_all()

    # Destroy the schedules
    input_values = {}

    if stack.get_attr("parallel_ids"):
        input_values["parallel_ids"] = stack.parallel_ids

    if stack.get_attr("sequential_ids"):
        input_values["sequential_ids"] = stack.sequential_ids

    if stack.get_attr("parallel") not in ["None", "null", None, False, "false"]:
        input_values["parallel_overide"] = True

    inputargs = {"input_values": input_values}
    inputargs["automation_phase"] = "destroying_schedules"
    inputargs["human_description"] = 'Delete schedules stack'
    stack.delete_schedules.insert(display=None, **inputargs)

    return stack.get_results(None)
