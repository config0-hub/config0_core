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
    """Process stack arguments and return results."""
    #####################################
    stack = newStack(stackargs)
    #####################################

    stack.parse.add_required(key="run_id")
    stack.parse.add_required(key="data")
    stack.parse.add_required(key="mkey", default="default")

    # Initialize Variables in stack
    stack.init_variables()

    inputargs = {
        "run_id": stack.run_id,
        "data": stack.data,
        "mkey": stack.mkey
    }

    stack.run_metadata.add(**inputargs)

    return stack.get_results()