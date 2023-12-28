def run(stackargs):

    #from time import sleep
    #import json

    stack = newStack(stackargs)

    stack.parse.add_required(key="parallel_ids", default="null")
    stack.parse.add_required(key="sequential_ids", default="null")
    stack.parse.add_required(key="destroy_instance", default="null")
    stack.parse.add_required(key="destroy_resources", default="null")
    stack.parse.add_required(
        key="keep_resources", default='[ {"provider":"aws","resource_type":"ecr_repo"} ]')
    stack.parse.add_required(
        key="last_resources", default='[ {"resource_type":"vpc"}, {"resource_type":"private_network"} ]')
    stack.parse.add_required(key="time_increment", default=1)

    # Add substacks
    stack.add_substack('config0-hub:::config0-core::delete_schedules')
    stack.add_substack('config0-hub:::config0-core::delete_resources')

    # Initialize
    stack.init_variables()
    stack.init_substacks()

    # Pre-delete resources
    input_values = {}

    if stack.get_attr("destroy_resources"):
        stack.set_variable("destroy_resources",
                           stack.to_json(stack.destroy_resources))
        input_values["destroy_resources"] = stack.destroy_resources

    if stack.get_attr("last_resources"):
        stack.set_variable(
            "last_resources", stack.to_json(stack.last_resources))

    # if we have last_resources, we set keep resources initially to include this
    _keep_resources = []

    if stack.get_attr("keep_resources"):
        stack.set_variable(
            "keep_resources", stack.to_json(stack.keep_resources))
        _keep_resources = stack.keep_resources[:]

    # we place the last_resources in the keep resources in the initally, but we
    # use the original keep resources later at ref 532098605435
    if stack.get_attr("last_resources"):
        _keep_resources.extend(stack.last_resources)
    if _keep_resources:
        input_values["keep_resources"] = _keep_resources

    stack.logger.debug("input_values {}".format(input_values))

    if stack.get_attr("parallel_ids"):

        for num, parallel_id in enumerate(stack.parallel_ids):

            stack.set_parallel()

            input_values["ref_schedule_id"] = parallel_id
            inputargs = {"input_values": input_values}
            inputargs["automation_phase"] = "destroying_resources"
            inputargs["human_description"] = 'Delete schedule_id "{}"'.format(
                parallel_id)
            stack.delete_resources.insert(display=None, **inputargs)

    # Set unset_parallel
    stack.unset_parallel()

    # Wait until all the parallel actions complete
    stack.wait_all()

    # Destroy resources in sequence
    if stack.get_attr("sequential_ids"):
        for sequential_id in stack.sequential_ids:
            input_values["ref_schedule_id"] = sequential_id
            inputargs = {"input_values": input_values}
            inputargs["automation_phase"] = "destroying_resources"
            inputargs["human_description"] = 'Delete schedule_id "{}"'.format(
                sequential_id)

            stack.logger.debug(
                "deleting the sequential schedule_id {}".format(sequential_id))
            stack.delete_resources.insert(display=None, **inputargs)

    # if there are last_resources, we delete them now since the
    # other resources have been deleted
    # ref 532098605435
    if stack.get_attr("last_resources"):

        stack.logger.debug("last resources {}".format(stack.last_resources))

        # ref 532098605435
        if stack.get_attr("keep_resources"):
            input_values["keep_resources"] = stack.keep_resources

        finalize_ids = []
        if stack.get_attr("parallel_ids"):
            finalize_ids.extend(stack.parallel_ids)
        if stack.get_attr("sequential_ids"):
            finalize_ids.extend(stack.sequential_ids)
        finalize_ids = list(set(finalize_ids))

        for finalize_id in finalize_ids:
            stack.logger.debug("input_values {}".format(input_values))
            input_values["ref_schedule_id"] = finalize_id
            inputargs = {"input_values": input_values}
            inputargs["automation_phase"] = "destroying_resources"
            inputargs["human_description"] = 'Delete ref_schedule_id "{}"'.format(
                finalize_id)
            stack.delete_resources.insert(display=None, **inputargs)

    # Destroy the schedules
    input_values = {}
    if stack.get_attr("parallel_ids"):
        input_values["parallel_ids"] = stack.parallel_ids
    if stack.get_attr("sequential_ids"):
        input_values["sequential_ids"] = stack.sequential_ids

    inputargs = {"input_values": input_values}
    inputargs["automation_phase"] = "destroying_schedules"
    inputargs["human_description"] = 'Delete schedules stack'
    stack.delete_schedules.insert(display=None, **inputargs)

    return stack.get_results(stack.destroy_instance)
