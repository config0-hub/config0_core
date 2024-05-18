def run(stackargs):

    stack = newStack(stackargs)

    # if you want to look up a worker with a different run_id
    # very uncommon
    stack.parse.add_required(key="overide_run_id", default="null")

    # Initialize Variables in stack
    stack.init_variables()

    worker_info = stack.get_worker_info(run_id=stack.overide_run_id)

    stack.publish(worker_info)

    return stack.get_results()
