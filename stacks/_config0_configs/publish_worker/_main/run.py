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
    """Process worker information and return results."""
    stack = newStack(stackargs)

    # If you want to look up a worker with a different run_id
    # Very uncommon
    stack.parse.add_required(key="overide_run_id", default="null")

    # Initialize Variables in stack
    stack.init_variables()

    worker_info = stack.get_worker_info(run_id=stack.overide_run_id)

    stack.output_to_ui(worker_info)

    return stack.get_results()
