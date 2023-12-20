def run(stackargs):

    stack = newStack(stackargs)

    # Add required arguments
    stack.parse.add_required(key="parallel_ids",default="null")
    stack.parse.add_required(key="sequential_ids",default="null")
    stack.parse.add_required(key="destroy_instance",default="null")
    stack.parse.add_optional(key="parallel_overide",default="null")

    # Initialize Variables in stack
    stack.init_variables()

    # Do parallel schedule deletes
    default_values = {}
    cmd = 'schedule delete'
    role = "schedule/delete"
    order_type = "delete_sched::api"

    if stack.get_attr("parallel_ids") and not isinstance(stack.parallel_ids,list): 
        stack.parallel_ids = [ stack.parallel_ids ]

    if stack.get_attr("sequential_ids") and not isinstance(stack.sequential_ids,list): 
        stack.sequential_ids = [ stack.sequential_ids ]

    all_schedule_ids = []

    if stack.get_attr("parallel_ids"): 
        all_schedule_ids.extend(stack.parallel_ids)

    if stack.get_attr("sequential_ids"): 
        all_schedule_ids.extend(stack.sequential_ids)

    stack.set_parallel()

    # parallel overide set True
    if stack.get_attr("parallel_overide") and all_schedule_ids:

        stack.logger.debug("Executing delete schedule_ids in parallel")

        for num,parallel_id in enumerate(all_schedule_ids):
            default_values["ref_schedule_id"] = parallel_id
            human_description = 'Delete schedule_id "{}"'.format(parallel_id)

            stack.insert_builtin_cmd(cmd,
                                     order_type=order_type,
                                     human_description=human_description,
                                     display=None,
                                     role=role,
                                     default_values=default_values)

            # We need a reference for the dependencies for parallelism
            # if num == 0: stack.set_parallel()

        return stack.get_results(None)

    # Delete parallel schedules
    if stack.get_attr("parallel_ids"):

        for num,parallel_id in enumerate(stack.parallel_ids):
            default_values["ref_schedule_id"] = parallel_id
            human_description = 'Delete schedule_id "{}"'.format(parallel_id)

            stack.insert_builtin_cmd(cmd,
                                     order_type=order_type,
                                     human_description=human_description,
                                     display=None,
                                     role=role,
                                     default_values=default_values)

            # We need a reference for the dependencies for parallelism
            # if num == 0: stack.set_parallel()

    # Delete sequential ids
    if not stack.get_attr("sequential_ids"):
        return stack.get_results(stack.destroy_instance)

    # Set unset_parallel
    stack.unset_parallel()

    # Wait until all actions complete
    stack.wait_all()

    for sequential_id in stack.sequential_ids:
        default_values["ref_schedule_id"] = sequential_id
        human_description = 'Delete schedule_id "{}"'.format(sequential_id)

        stack.insert_builtin_cmd(cmd,
                                 order_type=order_type,
                                 human_description=human_description,
                                 display=None,
                                 role=role,
                                 default_values=default_values)

    return stack.get_results(None)
