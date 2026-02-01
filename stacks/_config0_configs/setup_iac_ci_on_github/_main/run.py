"""
# Copyright (C) 2025 Gary Leong <gary@config0.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

def run(stackargs):

    import json
    import os

    stack = newStack(stackargs)

    stack.parse.add_required(key="stateful_id",
                             types="str")

    stack.parse.add_required(key="resource_type",
                             types="str")

    stack.parse.add_optional(key="iac_ci_repo",
                             types="str")

    # one folder per environment/one main branch
    # one branch per environment
    stack.parse.add_optional(key="iac_ci_pr_strategy",
                             default="branch",
                             choices=["branch", "folder"],
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
                       f'{stack.project_name}/{stack.resource_type}/{stack.stateful_id}')

    if not stack.get_attr("iac_ci_repo"):
        stack.set_variable("iac_ci_repo",
                           stack.inputvars.get("iac_ci_repo"))

    if not stack.get_attr("iac_ci_repo"):
        raise Exception("cannot set up iac ci - missing a repository")

    if stack.iac_ci_pr_strategy == "folder":
        stack.set_variable("iac_ci_branch",
                           stack.inputvars.get("iac_ci_branch", "main"))
    elif stack.iac_ci_pr_strategy == "branch":
        stack.set_variable("iac_ci_branch",
                           stack.iac_ci_folder)
    else:
        stack.set_variable("iac_ci_branch",
                           stack.iac_ci_folder)

    resource_info = stack.get_resource(
        match={
            "stateful_id": stack.stateful_id,
            "resource_type": stack.resource_type
        },
        must_be_one=True)[0]

    remote_stateful_bucket = resource_info["remote_stateful_bucket"]

    # ref 542352
    iac_src_s3_loc = f's3://{remote_stateful_bucket}/{stack.stateful_id}/state/src.{stack.stateful_id}.zip'

    env_vars = {
        "IAC_REPO_FOLDER": stack.iac_ci_folder,
        "IAC_CI_BRANCH": stack.iac_ci_branch,
        "IAC_CI_REPO": stack.iac_ci_repo,
        "IAC_SRC_S3_LOC": iac_src_s3_loc,
        "STATEFUL_ID": stack.stateful_id   # this is useful but not needed
    }

    env_vars.update({
        "IAC_CI_GITHUB_TOKEN": iac_ci_github_token,
        "GITHUB_NICKNAME": stack.nickname
    })

    human_description = f'IAC CI stateful_id/"{stack.stateful_id}", repo/"{stack.iac_ci_repo}" branch/"{stack.iac_ci_branch}"'

    inputargs = {
        "human_description": human_description,
        "env_vars": json.dumps(env_vars),
        "retries": 1,
        "timeout": 180,
        "wait_last_run": 20,
        "display": True
    }

    # Execute shellout and check for errors
    iac_ci_raise_on_failure = os.environ.get("IAC_CI_RAISE_ON_FAILURE", "true").lower() in ("true", "1", "yes")
    
    try:
        results = stack.iac_ci_s3_to_repo.run(**inputargs)
        
        # Check if results indicate failure
        if results:
            if isinstance(results, dict):
                status = results.get("status")
                exitcode = results.get("exitcode")
                failed_message = results.get("failed_message")
                
                if status is False or (exitcode is not None and exitcode != 0):
                    error_msg = f"IAC CI setup failed for stateful_id=\"{stack.stateful_id}\", repo=\"{stack.iac_ci_repo}\", branch=\"{stack.iac_ci_branch}\""
                    if exitcode is not None:
                        error_msg += f", exitcode={exitcode}"
                    if failed_message:
                        error_msg += f". Error: {failed_message}"
                    
                    stack.logger.error(error_msg)
                    
                    if iac_ci_raise_on_failure:
                        raise Exception(error_msg)
                else:
                    stack.logger.info(f"IAC CI setup succeeded for stateful_id=\"{stack.stateful_id}\", repo=\"{stack.iac_ci_repo}\", branch=\"{stack.iac_ci_branch}\"")
    except Exception as e:
        error_msg = f"IAC CI setup failed for stateful_id=\"{stack.stateful_id}\", repo=\"{stack.iac_ci_repo}\", branch=\"{stack.iac_ci_branch}\". Error: {str(e)}"
        stack.logger.error(error_msg)
        
        if iac_ci_raise_on_failure:
            raise Exception(error_msg)
        else:
            stack.logger.warn(f"IAC_CI_RAISE_ON_FAILURE is false, continuing despite error")

    # update resource
    update_values = {
        "iac_ci_info": {
            "env_vars": {
                "IAC_REPO_FOLDER": stack.iac_ci_folder,
                "IAC_CI_BRANCH": stack.iac_ci_branch,
                "IAC_CI_REPO": stack.iac_ci_repo,
                "IAC_SRC_S3_LOC": iac_src_s3_loc,
                "STATEFUL_ID": stack.stateful_id,
                "SSM_NAME": resource_info.get("ssm_name"),
            }
        }
    }

    # REF: register the iac-ci to ci system if exists
    stack.update_resource(update_values=update_values,
                          **resource_info)

    return stack.get_results()
