def run(stackargs):

    stack = newStack(stackargs)

    stack.parse.add_required(key="ttl", default="7200")
    stack.add_substack('config0-hub:::config0-core::publish_worker')

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_substacks()

    inputargs = {"input_values": {}}
    inputargs["timeout"] = int(stack.ttl) + 900
    inputargs["automation_phase"] = "debug_machine"
    inputargs["human_description"] = "publish the debug worker in the panel"
    stack.publish_worker.insert(display=True, **inputargs)

    cmd = 'sleep {}'.format(stack.ttl)

    stack.add_external_cmd(cmd=cmd,
                           order_type="sleep::shellout",
                           human_description="This is machine to debug for ttl {}".format(
                               stack.ttl),
                           display=True,
                           role="external/cli/execute")

    return stack.get_results()
