def run(stackargs):

    stack = newStack(stackargs)

    stack.parse.add_required(key="vars_set_name")

    stack.parse.add_optional(key="env_vars_hash", default='null')
    stack.parse.add_optional(key="labels_hash", default='null')
    stack.parse.add_optional(key="arguments_hash", default='null')

    stack.parse.add_optional(key="evaluate", default='null')

    # Initialize Variables in stack
    stack.init_variables()

    stack.set_variable("_env_vars", {})
    stack.set_variable("_labels", {})
    stack.set_variable("_arguments", {})

    resource = {'name': stack.vars_set_name,
                'label': stack.vars_set_name,
                'values': {}}

    if stack.get_attr("env_vars_hash"):
        resource["values"]["env_vars"] = stack.b64_decode(stack.env_vars_hash)

    if stack.get_attr("labels_hash"):

        stack.set_variable("_labels",
                           stack.b64_decode(stack.labels_hash))

        resource["values"]["labels"] = stack._labels

    if stack.get_attr("arguments_hash"):

        stack.set_variable("_arguments",
                           stack.b64_decode(stack.arguments_hash))

        resource["values"]["arguments"] = stack._arguments

    if stack.get_attr("_arguments") and stack.get_attr("evaluate"):

        arguments = stack.eval_vars(stack._arguments,
                                    strict=True)

        for _key, _value in arguments.items():
            resource["values"]["arguments"][_key] = _value

    if resource:
        stack.insert_vars_set(values=resource,
                              labels=stack._labels)

        description = 'added a variable set name {}'.format(
            stack.vars_set_name)
    else:
        description = 'failed to add variable set name {}'.format(
            stack.vars_set_name)

    stack.add_external_cmd(cmd="sleep 1",
                           order_type="empty_stack::shellout",
                           human_description=description,
                           display=True,
                           role="external/cli/execute")

    return stack.get_results(stackargs.get("destroy_instance"))
