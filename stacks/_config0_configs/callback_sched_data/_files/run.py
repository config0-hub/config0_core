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

    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="callback_api_endpoint")
    stack.parse.add_required(key="callback_token")
    stack.parse.add_required(key="sched_token")
    stack.parse.add_required(key="status")

    stack.parse.add_required(key="bucket_key",
                             default="null")

    stack.parse.add_required(key="cluster_id",
                             default="null")

    stack.parse.add_required(key="project_id",
                             default="null")

    stack.parse.add_required(key="sched_destroy",
                             default="null")

    stack.parse.add_optional(key="payload",
                             default="null")

    stack.parse.add_optional(key="payload_hash",
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
        "callback": stack.callback_token,
        "values": f"{str(stack.to_str(values))}"
    }

    if stack.get_attr("payload_hash"):
        payload = stack.b64_decode(stack.payload_hash)
    elif stack.get_attr("payload"):
        payload = stack.payload
    else:
        payload = None

    if stack.get_attr("bucket_key") and payload:
        stack.add_dict_to_s3(payload,
                             bucket_key=stack.bucket_key)

    stack.execute_restapi(default_values)

    return stack.get_results()