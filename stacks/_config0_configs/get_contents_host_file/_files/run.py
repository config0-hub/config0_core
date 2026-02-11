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

def _get_ipaddress(stack):
    return stack.get_resource(
        name=stack.hostname,
        must_be_one=True,
        use_labels="project",
        resource_type=stack.resource_type_hostname,
    )[0][stack.ip_key]

def _get_private_key(stack):
    return stack.get_resource(
        name=stack.ssh_key_name,
        must_be_one=True,
        use_labels="project",
        resource_type=stack.resource_type_ssh_key_name,
    )[0]["private_key"]

def run(stackargs):

    stack = newStack(stackargs)

    stack.parse.add_required(key="remote_file")
    stack.parse.add_required(key="host_username",
                             default="ubuntu")
    stack.parse.add_required(key="key")

    stack.parse.add_optional(key="ssh_key_name",
                             default="null")
    stack.parse.add_optional(key="hostname",
                             default="null")

    stack.parse.add_optional(key="ipaddress",
                             default="null")
    stack.parse.add_optional(key="private_key_hash",
                             default="null")

    # this is used for resource lookup with resource_type assumptions
    stack.parse.add_optional(key="resource_type_hostname",
                             default="server")

    stack.parse.add_optional(key="resource_type_ssh_key_name",
                             default="ssh_key_pair")

    stack.parse.add_optional(key="ip_key",
                             default="public_ip")


    # Initialize Variables in stack
    stack.init_variables()

    # we make certain assumptions with this:
    if stack.hostname and stack.ssh_key_name:
        stack.set_variable("ipaddress", _get_ipaddress(stack))
        stack.set_variable("private_key", _get_private_key(stack))
    elif stack.private_key_hash:
        stack.set_variable("private_key", stack.b64_decode(stack.private_key_hash))

    if not stack.ipaddress or not stack.private_key:
        stack.logger.error("we need to have/determine ipaddress and private_key to fetch host contents")
        return stack.get_results()

    contents = stack.host_fetch_contents(remote=stack.remote_file,
                                         user=stack.host_username,
                                         ipaddress=stack.ipaddress,
                                         private_key=stack.private_key)

    pipeline_env_var = {f"{stack.key}": str(contents)}
    stack.output_to_ui(pipeline_env_var)

    return stack.get_results()