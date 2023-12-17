def run(stackargs):

    import json

    # instantiate stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="run_id")
    stack.parse.add_required(key="commit_info")
    # stack.parse.add_required(key="job_name")
    # stack.parse.add_required(key="sched_name")

    # Initialize Variables in stack
    stack.init_variables()

    # Format the commit info
    if isinstance(stack.commit_info, str):
        try:
            stack.commit_info = json.loads(stack.commit_info)
        except:
            stack.commit_info = eval(stack.commit_info)

    keys2pass = ["author",
                 "message",
                 "commit_hash",
                 "event_type",
                 "sha",
                 "repo_ref",
                 "authored_date",
                 "repo_url"]

    # Print out the commit info
    stack.logger.aggmsg("", new=True)
    stack.logger.aggmsg("commit_info")
    stack.logger.aggmsg("type {}".format(type(stack.commit_info)))
    stack.logger.aggmsg(stack.commit_info)
    stack.logger.aggmsg("", prt=True, cmethod="debug_highlight")

    # Parse the commit info to place in the run metadata
    inserts = stack.dict_to_dict(keys2pass, {}, stack.commit_info)

    commit_url = stack.commit_info.get("url")
    if commit_url:
        inserts["commit_url"] = commit_url

    compare_url = stack.commit_info.get("compare")
    if compare_url:
        inserts["compare_url"] = compare_url

    repo_branch = stack.commit_info.get("branch")
    if repo_branch:
        inserts["repo_branch"] = repo_branch

    if not inserts.get("commit_hash"):
        inserts["commit_hash"] = inserts.get("sha")

    if not inserts.get("commit_hash"):
        inserts["commit_hash"] = inserts.get("repo_ref")

    # Use wrapper to publish
    # mkey -> Publish
    stack.publish(inserts)

    # Return run metadata with mkey "code"
    keys2pass = ["branch",
                 "committer",
                 "committed_date"]

    if commit_url:
        inserts["url"] = commit_url
    if compare_url:
        inserts["compare"] = compare_url
    if not inserts.get("repo_ref"):
        inserts["repo_ref"] = inserts["commit_hash"]
    if not inserts.get("sha"):
        inserts["sha"] = inserts["commit_hash"]

    # Direct insert to run
    inputargs = {"run_id": stack.run_id}
    inputargs["data"] = {"commit": inserts}
    inputargs["mkey"] = "code"
    stack.run_metadata.add(**inputargs)

    return stack.get_results()


def example():
    '''
{u'author': u'Config0',
 u'authored_date': u'2018-05-10T16:18:26Z',
 u'branch': u'flask_dev',
 u'commit_hash': u'693e0b418a8a8ec5d4ac15d945d43ca061eb4d77',
 u'committed_date': u'2018-05-10T16:18:26Z',
 u'committer': u'Config0',
 u'compare': u'https://github.com/bill12252016/template_param_cd_control/compare/45e6b7ce28f4...693e0b418a8a',
 u'email': u'info@config0.com',
 u'event_type': u'push',
 u'message': u'autocommit by config0 for deploy.',
 u'url': u'https://github.com/bill12252016/template_param_cd_control/commit/693e0b418a8a8ec5d4ac15d945d43ca061eb4d77'}

    '''
