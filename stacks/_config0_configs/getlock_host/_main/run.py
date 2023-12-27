def run(stackargs):

    #####################################
    stack = newStack(stackargs)
    #####################################

    stack.parse.add_required(key="docker_host")
    stack.parse.add_required(key="docker_guest")
    stack.parse.add_required(key="sched_type")
    stack.parse.add_required(key="sched_name")
    stack.parse.add_required(key="add_env_var",default="true")
    stack.parse.add_required(key="destroy_instance",default="null")

    stack.parse.add_optional(key="publish2pipeline",default="null")
    stack.parse.add_optional(key="add_groups",default="null")

    #stack.add_substack('config0-hub:::config0-core::register_config_container')
    stack.add_substack('config0-hub:::config0-core::publish_info')

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_substacks()

    # Check for consistency sched_type and sched_name
    if not stack.get_attr("sched_type") or stack.sched_type == "None":
        msg = "sched_type cannot be None"
        stack.ehandle.NeedMoreInfo(message=msg)

    if not stack.get_attr("sched_name") or stack.sched_name == "None":
        msg = "sched_name cannot be None"
        stack.ehandle.NeedMoreInfo(message=msg)

    # request_lock:
    cmd = 'host add queue_locks'
    order_type = "add2queue-hostlock::api"
    role = "insert/queue"

    default_values = {}
    default_values["hostname"] = stack.docker_host

    human_description = 'Submit request to use hostname "{}"'.format(stack.docker_host)

    stack.insert_builtin_cmd(cmd,
                             order_type=order_type,
                             human_description=human_description,
                             display=None,
                             role=role,
                             default_values=default_values)

    # get lock
    cmd = 'host get lock'
    order_type = "get-hostlock::api"
    role = "get/lock"

    default_values = {}
    default_values["hostname"] = stack.docker_host

    human_description = 'Waiting for hostname "{}" to free up'.format(stack.docker_host)
    stack.insert_builtin_cmd(cmd,
                             order_type=order_type,
                             human_description=human_description,
                             display=True,
                             role=role,
                             default_values=default_values)

    # Need to get lock first for docker_host
    # Set up the shared mounted directories
    if stack.get_attr("add_groups"): 
        stack.add_group_orders(stack.add_groups,hostname=stack.docker_host,unassign=True)

    # registers jiffy host
    optional_keys = []
    optional_keys.append("ports")
    optional_keys.append("auto_ssh_port")
    optional_keys.append("auto_http_port")
    optional_keys.append("ssh_port")
    optional_keys.append("http_port")

    required_keys = ["docker_host" ]
    required_keys.append("docker_guest")
    required_keys.append("sched_type")
    required_keys.append("sched_name")

    stack.register_jiffyhost.insert(optional_keys=optional_keys,
                                    required_keys=required_keys)

    # publish 2 pipeline
    if stack.get_attr("publish2pipeline"):
        overide_values = {}
        overide_values["hostname"] = stack.docker_guest
        overide_values["add_env_var"] = stack.add_env_var
        inputargs = {"overide_values":overide_values}
        inputargs["automation_phase"] = "continuous_delivery"
        inputargs["human_description"] = 'Publish info for dock_guest"{}"'.format(stack.docker_guest)
        stack.publish_info.insert(display=True,**inputargs)

    # remove request_lock
    cmd = 'host remove lock'
    order_type = "remove-hostlock::api"
    role = "remove/lock"

    default_values = {}
    default_values["hostname"] = stack.docker_host
    human_description = 'Removing lock docker_guest "{}" on "{}"'.format(stack.docker_guest,
                                                                         stack.docker_host)

    stack.insert_builtin_cmd(cmd,
                             order_type=order_type,
                             human_description=human_description,
                             display=True,
                             role=role,
                             default_values=default_values)

    return stack.get_results(stack.destroy_instance)
