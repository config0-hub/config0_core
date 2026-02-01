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

    stack.parse.add_required(key="description", default="null")

    # Initialize Variables in stack
    stack.init_variables()

    if not stack.get_attr("description"):
        stack.description = "This is an empty stack"
        stackargs["description"] = stack.description

    cmd = f'echo "{stack.description}"'

    stack.add_external_cmd(cmd=cmd,
                           order_type="empty_stack::shellout",
                           human_description=stack.description,
                           display=True,
                           role="external/cli/execute")

    return stack.get_results()