def run(stackargs):

    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="callback_api_endpoint")
    stack.parse.add_required(key="callback_token")
    stack.parse.add_required(key="sched_token")
    stack.parse.add_required(key="status")

    stack.parse.add_required(key="bucket_key",
                             default="null")

    stack.parse.add_required(key="payload",
                             default="null")

    stack.parse.add_required(key="cluster_id",
                             default="null")

    stack.parse.add_required(key="project_id",
                             default="null")

    stack.parse.add_required(key="sched_destroy",
                             default="null")

    # Init the variables
    stack.init_variables()

    # call to report run
    values = {
        "schedule_id": stack.schedule_id,
        "run_id": stack.run_id,
        "cluster": stack.cluster,
        "instance": stack.instance,
        "status": stack.status,
        "sched_token": stack.sched_token
    }

    if stack.get_attr("bucket_key"):
        values["bucket_key"] = stack.bucket_key

    if stack.get_attr("cluster_id"): 
        values["cluster_id"] = stack.cluster_id

    # If the callback is confirm the destroying of a project/schedule ids
    if stack.get_attr("sched_destroy") and stack.get_attr("project_id"):
        values["sched_destroy"] = stack.project_id

    default_values = {
        "http_method": "post",
        "api_endpoint": stack.callback_api_endpoint,
        "callback": stack.callback_token,"values": "{}".format(str(stack.dict2str(values)))
    }

    human_description = "Report/callback to SaasS schedule_id={}, run_id={}".format(stack.schedule_id,
                                                                                    stack.run_id)

    if stack.get_attr("bucket_key") and stack.get_attr("payload"):
        stack.add_dict_to_s3(stack.payload,
                             bucket_key=stack.bucket_key)

    stack.insert_builtin_cmd("execute restapi",
                             order_type="saas-report_sched::api",
                             default_values=default_values,
                             human_description=human_description,
                             display=True,
                             role="config0/api/execute")

    return stack.get_results()