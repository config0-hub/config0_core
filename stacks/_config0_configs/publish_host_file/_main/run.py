def run(stackargs):

    #####################################
    stack = newStack(stackargs)
    #####################################

    stack.parse.add_required(key="hostname")
    stack.parse.add_required(key="ssh_key_name")
    stack.parse.add_required(key="remote_file")
    stack.parse.add_required(key="key")

    # Initialize Variables in stack
    stack.init_variables()

    contents = stack.host_fetch_contents(remote=stack.remote_file,
                                         hostname=stack.hostname,
                                         ssh_key_name=stack.ssh_key_name)

    pipeline_env_var = {stack.key: str(contents)}
    stack.publish(pipeline_env_var)

    return stack.get_results(stackargs.get("destroy_instance"))
