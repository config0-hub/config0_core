"""
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

def run(stackargs):

    stack = newStack(stackargs)

    stack.parse.add_required(key="drift_protection",
                             default="True")

    stack.parse.add_optional(key="ref_schedule_id",
                             default="null")

    stack.parse.add_optional(key="resource_type",
                             default="null")

    stack.add_substack('config0-publish:::config0_core::check_drift_resource')

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_substacks()

    if stack.drift_protection:
        match = {"drift_protection": True}
    else:
        match = {}

    if stack.ref_schedule_id:
        match["schedule_id"] = stack.ref_schedule_id

    if stack.resource_type:
        match["resource_type"] = stack.resource_type

    resources_to_chk = stack.get_resource(match=match)

    if not resources_to_chk:
        stack.logger.warn("There are no other resources to validate for drift")
        return stack.get_results()

    stack.set_parallel()

    for resource in resources_to_chk:
        inputargs = {
            "overide_values": {
                "resource_id": resource["id"],
            },
            "automation_phase": "infrastructure",
            "human_description": f'check drift {resource.get("name")}',
            "display": True
        }
        stack.check_drift_resource.insert(**inputargs)

    stack.wait_to_complete()

    return stack.get_results()