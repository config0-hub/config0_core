def run(stackargs):

    stack = newStack(stackargs)

    # Add default variables
    #stack.parse.add_required(key="run_id")
    #stack.parse.add_required(key="schedule_id")
    stack.parse.add_required(key="callback_api_endpoint")
    stack.parse.add_required(key="callback_token")
    stack.parse.add_required(key="sched_token")
    stack.parse.add_required(key="status")

    stack.parse.add_required(key="edata",default="null")
    stack.parse.add_required(key="cluster_id",default="null")
    stack.parse.add_required(key="epassphrase",default="null")
    stack.parse.add_required(key="project_id",default="null")
    stack.parse.add_required(key="sched_destroy",default="null")

    # Init the variables
    stack.init_variables()

    # call to report run
    values = {"schedule_id":stack.schedule_id}
    values["run_id"] = stack.run_id
    values["cluster"] = stack.cluster
    values["instance"] = stack.instance
    values["status"] = stack.status
    values["sched_token"] = stack.sched_token

    if stack.get_attr("epassphrase"):
        values["epassphrase"] = stack.epassphrase

    if stack.get_attr("edata"):
        values["edata"] = stack.edata

    if stack.get_attr("cluster_id"): 
        values["cluster_id"] = stack.cluster_id

    # If the callback is confirm the destroying of a project/schedule ids
    if stack.get_attr("sched_destroy") and stack.get_attr("project_id"):
        values["sched_destroy"] = stack.project_id

    default_values = { "http_method": "post" }
    default_values["api_endpoint"] = stack.callback_api_endpoint
    default_values["callback"] = stack.callback_token
    default_values["values"] = "{}".format(str(stack.dict2str(values)))

    human_description = "Report/callback to SaasS schedule_id={}, run_id={}".format(stack.schedule_id,
                                                                                    stack.run_id)

    stack.insert_builtin_cmd("execute restapi",
                             order_type="saas-report_sched::api",
                             default_values=default_values,
                             human_description=human_description,
                             display=True,
                             role="config0/api/execute")

    # need to place this in the scheduler
    # destroy the queue qhost worker for the run_id
    #stack.destroy_qhost(run_id=stack.run_id,schedule_id=stack.schedule_id)

    return stack.get_results()
