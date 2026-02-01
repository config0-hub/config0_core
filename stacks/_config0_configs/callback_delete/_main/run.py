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

    # Required stack args
    stack.parse.add_required(key="parallel_ids",
                             default="null")

    stack.parse.add_required(key="sequential_ids",
                             default="null")

    stack.parse.add_required(key="keep_resources",
                             default='[ {"provider":"aws","resource_type":"ecr_repo"} ]')

    # This is parallel override to delete resources and schedules in parallel
    stack.parse.add_optional(key="parallel",
                             default="true")

    # Add substacks
    stack.add_substack('config0-publish:::delete_schedules')
    stack.add_substack('config0-publish:::delete_resources_by_time')

    # Initialize
    stack.init_variables()
    stack.init_substacks()

    # Get all the schedule_ids
    ref_schedule_ids = stack.parallel_ids[:]
    ref_schedule_ids.extend(stack.sequential_ids[:])

    # Delete resources
    input_values = {
        "ref_schedule_ids": ref_schedule_ids
    }

    if stack.get_attr("keep_resources"):
        input_values["keep_resources"] = stack.keep_resources

    if stack.get_attr("parallel") not in ["None", "null", None, False, "false"]:
        input_values["parallel_overide"] = True

    inputargs = {
        "input_values": input_values
    }

    stack.delete_resources_by_time.insert(display=None,
                                          **inputargs)

    stack.wait_all()

    # Destroy the schedules
    input_values = {}

    if stack.get_attr("parallel_ids"):
        input_values["parallel_ids"] = stack.parallel_ids

    if stack.get_attr("sequential_ids"):
        input_values["sequential_ids"] = stack.sequential_ids

    if stack.get_attr("parallel") not in ["None", "null", None, False, "false"]:
        input_values["parallel_overide"] = True

    inputargs = {
        "input_values": input_values,
        "automation_phase": "destroying_schedules",
        "human_description": 'Delete schedules stack'
    }

    stack.delete_schedules.insert(display=None,
                                  **inputargs)

    return stack.get_results(None)