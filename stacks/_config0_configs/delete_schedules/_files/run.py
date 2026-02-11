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

    # Add required arguments
    stack.parse.add_required(key="parallel_ids", default="null")
    stack.parse.add_required(key="sequential_ids", default="null")
    stack.parse.add_required(key="destroy_instance", default="null")
    stack.parse.add_optional(key="parallel_overide", default="null")

    # Initialize Variables in stack
    stack.init_variables()

    # Do parallel schedule deletes
    if stack.get_attr("parallel_ids") and not isinstance(stack.parallel_ids, list):
        stack.parallel_ids = [stack.parallel_ids]

    if stack.get_attr("sequential_ids") and not isinstance(stack.sequential_ids, list): 
        stack.sequential_ids = [stack.sequential_ids]

    all_schedule_ids = []

    if stack.get_attr("parallel_ids"): 
        all_schedule_ids.extend(stack.parallel_ids)

    if stack.get_attr("sequential_ids"): 
        all_schedule_ids.extend(stack.sequential_ids)

    stack.set_parallel()

    # parallel overide set True
    if stack.get_attr("parallel_overide") and all_schedule_ids:
        stack.logger.debug("Executing delete schedule_ids in parallel")
        for num, parallel_id in enumerate(all_schedule_ids):
            stack.delete_schedule(parallel_id)
        return stack.get_results(None)

    # Delete parallel schedules
    if stack.get_attr("parallel_ids"):
        for num, parallel_id in enumerate(stack.parallel_ids):
            stack.delete_schedule(parallel_id)

    # Delete sequential ids
    if not stack.get_attr("sequential_ids"):
        return stack.get_results(stack.destroy_instance)

    # Set unset_parallel
    stack.unset_parallel()

    # Wait until all actions complete
    stack.wait_all()

    for sequential_id in stack.sequential_ids:
        stack.delete_schedule(sequential_id)
    return stack.get_results(None)