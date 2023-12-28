def run(stackargs):

    stack = newStack(stackargs)

    stack.parse.add_required(key="groups")
    stack.parse.add_required(key="hostname")

    # Initialize Variables in stack
    stack.init_variables()
    stack.add_groups_to_host(groups=stack.groups, hostname=stack.hostname)

    return stack.get_results()
