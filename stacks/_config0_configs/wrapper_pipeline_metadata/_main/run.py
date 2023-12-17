def run(stackargs):

    #####################################
    stack = newStack(stackargs)
    #####################################

    stack.parse.add_required(key="run_id")
    stack.parse.add_required(key="data")
    stack.parse.add_required(key="mkey", default="default")

    # Initialize Variables in stack
    stack.init_variables()

    kwargs = {"run_id": stack.run_id}
    kwargs["data"] = stack.data
    kwargs["mkey"] = stack.mkey

    stack.run_metadata.add(**kwargs)

    return stack.get_results()
