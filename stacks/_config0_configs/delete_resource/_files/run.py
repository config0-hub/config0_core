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

    stack.parse.add_optional(key="db_id", default="null")
    stack.parse.add_optional(key="resource_type", default="null")
    stack.parse.add_optional(key="name", default="null")
    stack.parse.add_optional(key="hostname", default="null")
    stack.parse.add_optional(key="ref_schedule_id", default="null")
    stack.parse.add_optional(key="must_exists", default="null")

    # Initialize Variables in stack
    stack.init_variables()

    _destroy_match = {}

    if stack.get_attr("db_id"):
        _destroy_match["_id"] = stack.db_id

    if stack.get_attr("hostname"):
        _destroy_match["hostname"] = stack.hostname

    if stack.get_attr("name"):
        _destroy_match["name"] = stack.name

    if stack.get_attr("ref_schedule_id"):
        _destroy_match["schedule_id"] = stack.ref_schedule_id

    if stack.get_attr("resource_type"):
        _destroy_match["resource_type"] = stack.resource_type

    if stack.get_attr("must_exists"):
        _destroy_match["must_exists"] = True

    if not _destroy_match:
        error_msg = "match for destroy resource cannot be wide open"
        stack.logger.error(error_msg)
        raise Exception(error_msg)

    _dinputargs = stack.get_resource(**_destroy_match)

    if _dinputargs and len(_dinputargs) == 1:
        stack.remove_resource(**_dinputargs[0])
    elif _dinputargs and len(_dinputargs) > 1:
        error_msg = f"More than resource found for {_destroy_match}"
        raise Exception(error_msg)

    return stack.get_results()
