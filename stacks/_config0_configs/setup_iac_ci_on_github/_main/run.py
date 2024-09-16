def run(stackargs):

    import json

    stack = newStack(stackargs)

    stack.parse.add_required(key="stateful_id",
                             types="str")

    stack.parse.add_required(key="reource_type",
                             types="str")

    stack.parse.add_optional(key="iac_ci_repo",
                             types="str")

    stack.parse.add_optional(key="iac_ci_pr_strategy",
                             default="folder",
                             types="str")

    # add shelloutconfigs
    stack.add_shelloutconfig('config0-publish:::config0_core::iac_ci_s3_to_repo')

    # initialize
    stack.init_variables()
    stack.init_shelloutconfigs()

    iac_ci_github_token = stack.inputvars.get("iac_ci_github_token")
    if not iac_ci_github_token:
        raise Exception("we need a iac_ci_github_token")

    stack.set_variable("iac_ci_folder",
                       f'{stack.project_name}/{stack.stateful_id}')

    if not stack.get_attr("iac_ci_repo"):
        stack.set_variable("iac_ci_repo",
                           stack.inputvars.get("iac_ci_repo"))

    if not stack.get_attr("iac_ci_repo"):
        raise Exception("cannot set up iac ci - missing a repository")

    if stack.iac_ci_pr_strategy == "folder":
        stack.set_variable("iac_ci_branch",
                           stack.inputvars.get("iac_ci_branch", "main"))
    elif "iac_ci_pr_strategy" == "branch":
        stack.set_variable("iac_ci_branch",
                           stack.iac_ci_folder)

    resource_info = stack.get_resource(
        match={
            "stateful_id":stack.stateful_id,
            "resource_type":stack.resource_type
        },
        must_be_one=True)[0]

    remote_stateful_bucket = resource_info["remote_stateful_bucket"]
    iac_src_s3_loc = f's3://{remote_stateful_bucket}/{stack.stateful_id}'

    env_vars = {
        "IAC_REPO_FOLDER":stack.iac_ci_folder,
        "IAC_CI_BRANCH":stack.iac_ci_branch,
        "IAC_CI_REPO": stack.iac_ci_repo,
        "IAC_SRC_S3_LOC": iac_src_s3_loc
    }

    env_vars.update({
        "GITHUB_TOKEN":iac_ci_github_token,
        "GITHUB_NICKNAME": stack.nickname

    })

    human_description = 'IAC CI Gitops setup stateful_id "{}"'.format(stack.stateful_id)

    inputargs = {
        "human_description": human_description,
        "env_vars": json.dumps(env_vars),
        "retries": 1,
        "timeout": 180,
        "wait_last_run": 20,
        "display": True
    }

    stack.iac_ci_s3_to_repo.run(**inputargs)

    return stack.get_results()
