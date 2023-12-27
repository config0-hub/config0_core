def run(stackargs):

    #####################################
    stack = newStack(stackargs)
    #####################################

    stack.parse.add_required(key="run_id")
    stack.parse.add_required(key="data")
    stack.parse.add_required(key="mkey", default="default")

    # Initialize Variables in stack
    stack.init_variables()

    inputargs = {"run_id": stack.run_id}
    inputargs["data"] = stack.data
    inputargs["mkey"] = stack.mkey

    stack.run_metadata.add(**inputargs)

    return stack.get_results()
