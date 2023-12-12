def run(stackargs):

    #####################################
    stack = newStack(stackargs)
    #####################################

    stack.parse.add_required(key="hostname")
    stack.parse.add_required(key="add_env_var", default="true")

    # Initialize Variables in stack
    stack.init_variables()

    #####################################

    # Get the host info needed to gather ports
    host_info = stack.check_resource(name=stack.hostname, must_exists=True)[0]

    pipeline_env_var = {}

    if host_info.get("ssh_port"):
        pipeline_env_var["SSH_PORT"] = host_info["ssh_port"]

    if host_info.get("http_port"):
        pipeline_env_var["HTTP_PORT"] = host_info["http_port"]

    if pipeline_env_var:
        stack.add_run_metadata(pipeline_env_var, env_var=True)

    if stack.get_attr("add_env_var"):
        pipeline_env_var = {}
        if host_info.get("ssh_port"):
            pipeline_env_var["SSH_PORT"] = host_info["ssh_port"]
        if host_info.get("http_port"):
            pipeline_env_var["HTTP_PORT"] = host_info["http_port"]
        if pipeline_env_var:
            stack.add_run_metadata(pipeline_env_var, env_var=True)

    # Pipeline env vars to publish
    keys2pass = ["public_dns_name", "private_dns_name", "private_ip",
                 "public_ip", "ssh_port", "http_port", "docker_guest"]
    pipeline_env_var = stack.dict_to_dict(keys2pass, {}, host_info)

    if host_info.get("docker_guest"):
        pipeline_env_var["docker_guest"] = stack.hostname
    elif host_info.get("docker_host"):
        pipeline_env_var["docker_host"] = stack.hostname
    else:
        pipeline_env_var["hostname"] = stack.hostname

    if pipeline_env_var.get("public_dns_name"):
        if "public_ip" in pipeline_env_var:
            del pipeline_env_var["public_ip"]

    if pipeline_env_var.get("private_dns_name"):
        if "private_ip" in pipeline_env_var:
            del pipeline_env_var["private_ip"]

    # Determine public base endpt
    _public_base_endpt = None

    if pipeline_env_var.get("public_dns_name"):
        _public_base_endpt = pipeline_env_var["public_dns_name"]
    elif pipeline_env_var.get("public_ip"):
        _public_base_endpt = pipeline_env_var["public_ip"]

    # Provide http endpoint
    if pipeline_env_var.get("http_port") and _public_base_endpt:
        pipeline_env_var["app_endpoint"] = "http://{}:{}".format(
            _public_base_endpt, pipeline_env_var["http_port"])

    if pipeline_env_var.get("ssh_port") and _public_base_endpt:
        pipeline_env_var["ssh_cmd"] = "ssh root@{} -p {}".format(
            _public_base_endpt, pipeline_env_var["ssh_port"])

    stack.add_run_metadata(pipeline_env_var, publish=True)

    return stack.get_results(stackargs.get("destroy_instance"))
