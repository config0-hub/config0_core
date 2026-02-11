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

    # Required stack args: comma-separated resource db _ids
    stack.parse.add_required(key="db_ids",
                             default="null")

    stack.parse.add_optional(key="parallel",
                             default="true")

    # Add substacks
    stack.add_substack('config0-publish:::delete_resource')

    # Initialize
    stack.init_variables()
    stack.init_substacks()

    # Get all the resource ids (strip whitespace, skip empty)
    _ids = [x.strip() for x in stack.db_ids.split(",") if x.strip()]

    if not _ids:
        return stack.get_results(None)

    # Delete resources: one delete_resource substack call per db_id
    if stack.get_attr("parallel") not in ["None", "null", None, False, "false"]:
        stack.set_parallel()

    for _id in _ids:
        inputargs = {
            "arguments": {"db_id": _id},
            "human_description": "Delete resource {}".format(_id),
        }
        stack.delete_resource.insert(display=None, **inputargs)

    stack.wait_all()

    return stack.get_results(None)
