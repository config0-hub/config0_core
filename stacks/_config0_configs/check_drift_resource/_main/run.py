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

    stack.parse.add_required(key="resource_id")
    stack.parse.add_optional(key="resource_type", default="null")
    stack.parse.add_optional(key="ref_schedule_id", default="null")

    # Initialize Variables in stack
    stack.init_variables()

    match = {"id": stack.resource_id}

    if stack.get_attr("ref_schedule_id"):
        match["schedule_id"] = stack.ref_schedule_id

    if stack.get_attr("resource_type"):
        match["resource_type"] = stack.resource_type

    resource = stack.get_resource(match=match)

    if resource and len(resource) == 1:
        stack.validate_resource(resource[0]["id"], **resource[0])
    elif resource and len(resource) > 1:
        error_msg = f"More than resource found for {match}"
        stack.logger.error(error_msg)
        raise Exception(error_msg)

    return stack.get_results()