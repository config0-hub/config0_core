def run(stackargs):

    stack = newStack(stackargs)

    stack.parse.add_required(key="description", default="null")

    # Initialize Variables in stack
    stack.init_variables()

    if not stack.get_attr("description"):
        stack.description = "This is an empty stack"
        stackargs["description"] = stack.description

    cmd = 'echo "{}"'.format(stack.description)

    stack.add_external_cmd(cmd=cmd,
                           order_type="empty_stack::shellout",
                           human_description=stack.description,
                           display=True,
                           role="external/cli/execute")

    return stack.get_results()
