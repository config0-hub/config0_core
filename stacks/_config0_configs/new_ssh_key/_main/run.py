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

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_optional(key="name", default='null')
    stack.parse.add_optional(key="key_name", default='null')
    stack.parse.add_optional(key="schedule_id", default="null")
    stack.parse.add_optional(key="run_id", default="null")
    stack.parse.add_optional(key="job_instance_id", default="null")
    stack.parse.add_optional(key="job_id", default="null")
    stack.parse.add_optional(key="clobber", default="null")

    # Initialize Variables in stack
    stack.init_variables()

    if not stack.get_attr("key_name") and stack.get_attr("name"):
        stack.set_variable("key_name", stack.name)

    if not stack.get_attr("key_name"):
        msg = "key_name or name variable has to be set"
        raise Exception(msg)

    # Delete key if clobber
    if stack.get_attr("clobber"):
        stack.delete_ssh_key(stack.key_name)

    # Create key
    stack.create_ssh_key(stack.key_name)

    return stack.get_results()