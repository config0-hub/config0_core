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

    stack.parse.add_required(key="hostname")
    stack.parse.add_required(key="ssh_key_name")
    stack.parse.add_required(key="remote_file")
    stack.parse.add_required(key="key")

    # Initialize Variables in stack
    stack.init_variables()

    contents = stack.host_fetch_contents(remote=stack.remote_file,
                                         hostname=stack.hostname,
                                         ssh_key_name=stack.ssh_key_name)

    pipeline_env_var = {f"{stack.key}": str(contents)}
    stack.output_to_ui(pipeline_env_var)

    return stack.get_results(stackargs.get("destroy_instance"))
