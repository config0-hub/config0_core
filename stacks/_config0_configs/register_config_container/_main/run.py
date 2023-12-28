def run(stackargs):

    #####################################
    stack = newStack(stackargs)
    #####################################

    stack.parse.add_required(key="docker_host")
    stack.parse.add_required(key="docker_guest")
    stack.parse.add_required(key="sched_type")
    stack.parse.add_required(key="sched_name")

    stack.parse.add_optional(key="ports")
    stack.parse.add_optional(key="auto_ssh_port")
    stack.parse.add_optional(key="auto_http_port")
    stack.parse.add_optional(key="ssh_port")
    stack.parse.add_optional(key="http_port")

    # Initialize Variables in stack
    stack.init_variables()

    ##############################################

    if stack.get_attr("auto_ssh_port") and stack.get_attr("ports") and ":22" in stack.ports: 
        stack.logger.warn("Cannot auto assign ssh port when it is already specified.  Skipping ...")

    elif stack.get_attr("auto_ssh_port") or stack.get_attr("ssh_port"):
        stack.ssh_port = stack.get_docker_guest_ssh_port(docker_host=stack.docker_host,
                                                         ssh_port=stack.ssh_port)

        stack.logger.debug("The ssh_port assigned is {}".format(stack.ssh_port))

    if stack.get_attr("auto_http_port") and stack.get_attr("ports") and ":80" in stack.ports: 
        stack.logger.warn("Cannot auto assign ssh port when it is already specified.  Skipping ...")

    elif stack.get_attr("auto_http_port") or stack.get_attr("http_port"):

        stack.http_port = stack.get_docker_guest_http_port(docker_host=stack.docker_host,
                                                           http_port=stack.http_port)

        stack.logger.debug("The http_port assigned is {}".format(stack.http_port))

    if stack.get_attr("ssh_port") and stack.ports: 
        stack.ports = "{},{}:22".format(stack.ports,stack.ssh_port)

    if stack.get_attr("ssh_port") and not stack.get_attr("ports"): 
        stack.ports = "{}:22".format(stack.ssh_port)

    # if http_port and ports: ports = "{},{}:80".format(ports,http_port)
    # if http_port and not ports: ports = "{}:80".format(http_port)

    # We simply assign the http_port, we don't use it since 
    # the guest container is used to launch the real "deploy" container
    # that will utilize the http_port

    # Create template for subsequenty docker hosts
    cmd = "server shelloutconfig execute"
    order_type = "remote_shelloutconfig::api"
    role = "host/execute"

    default_values = {}
    default_values["hostname"] = stack.docker_host
    default_values["shelloutconfigs"] = "gary:::public::docker/docker_guest_cp_template"
    default_values["ip_key"] = "private_ip"
    default_values["env_file"] = "{}.env".format(stack.docker_host)

    custom_envs = "CLUSTER={} SCHED_TYPE={} DOCKER_HOSTNAME={} DOCKER_PORTS={} SSH_PORT={} SCHED_NAME={}".format(stack.cluster,
                                                                                                                 stack.sched_type,
                                                                                                                 stack.docker_guest,
                                                                                                                 stack.ports,
                                                                                                                 stack.ssh_port,
                                                                                                                 stack.sched_name)

    stack.logger.debug("custom_envs:\n {}".format(custom_envs))

    default_values["custom_envs"] = custom_envs
    human_description = "Creating Docker Guest for sched_name = {}".format(stack.sched_name)

    stack.insert_builtin_cmd(cmd,
                             order_type=order_type,
                             role=role,
                             display=None,
                             human_description=human_description,
                             default_values=default_values)
   
    # We need to allocate the http_port that this guest container will
    # will use for the deploy
    # register the guest into the engine
    if stack.get_attr("http_port") and stack.get_attr("ports"): 
        stack.ports = "{},{}:80".format(stack.ports,stack.http_port)

    if stack.get_attr("http_port") and not stack.get_attr("ports"): 
        stack.ports = "{}:80".format(stack.http_port)

    cmd = "docker guest add"
    order_type = "register-docker_guest::api"
    role = "cloud/server"

    default_values = {}
    default_values["docker_host"] = stack.docker_host
    default_values["docker_guest"] = stack.docker_guest
    default_values["ports"] = stack.ports
    default_values["build_dir"] = "{}/{}/{}/{}".format("/var/tmp/docker/build",
                                                       stack.cluster,
                                                       stack.sched_type,
                                                       stack.sched_name)

    stack.insert_builtin_cmd(cmd,
                             order_type=order_type,
                             human_description='Registering docker_guest "{}" on "{}".'.format(stack.docker_guest,stack.docker_host),
                             display=True,
                             default_values=default_values,
                             role=role)

    # Add host to the engine
    cmd = "host add"
    order_type = "add-host::api"
    role = "host/add"

    overide_values = {"tags":None}
    overide_values["hostname"] = stack.docker_guest
    overide_values["docker_guest"] = True

    human_description = 'Adding/Recording host "{}"'.format(stackargs["docker_guest"])
    long_description = "Adds host = {} to Jiffy".format(stackargs["docker_guest"])

    stack.insert_builtin_cmd(cmd,
                             order_type=order_type,
                             role=role,
                             human_description=human_description,
                             long_description=long_description,
                             display=None,
                             overide_values=overide_values)

    return stack.get_results(stackargs.get("destroy_instance"))
