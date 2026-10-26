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

_STATE_POINTER_KEYS = ("stateful_id",
                       "remote_stateful_location",
                       "remote_stateful_bucket")


def _has_state_pointer(resource):
    """A row carrying any state pointer is real infrastructure."""
    return any(resource.get(key) not in (None, "", "null", "None")
               for key in _STATE_POINTER_KEYS)


def _is_ssm_secret(resource):
    """True for a stack.add_secret row naming its permanent SSM parameter."""
    return (resource.get("resource_type") == "secret"
            and resource.get("ssm_path") not in (None, "", "null", "None"))


def _is_connection_pointer(resource):
    """True for the schedule->aws_account connection pointer row.

    Every order of the schedule, a secret's remove included, resolves its
    target credentials through this row, so it is deleted after every other
    row of the run.
    """
    return (resource.get("resource_type") == "reference"
            and resource.get("reference_target") == "aws_account")


def _delete(stack, _id):
    """Insert one delete_resource substack call for db_id *_id*."""
    inputargs = {
        "arguments": {"db_id": _id},
        "human_description": f"Delete resource {_id}",
    }
    stack.delete_resource.insert(display=None, **inputargs)


def run(stackargs):

    stack = newStack(stackargs)

    # Required stack args: comma-separated resource db _ids
    stack.parse.add_required(key="db_ids",
                             default="null")

    stack.parse.add_optional(key="parallel",
                             default="true")

    # Add substacks
    stack.add_substack('config0-hub:::config0_core::delete_resource')

    # Initialize
    stack.init_variables()
    stack.init_substacks()

    # Get all the resource ids (strip whitespace, skip empty)
    _ids = [x.strip() for x in stack.db_ids.split(",") if x.strip()]

    if not _ids:
        return stack.get_results()

    # The order delete_resources_by_time uses: the infrastructure deletes, a
    # barrier, the SSM secret deletes, then the record-only deletes with the
    # schedule's connection pointer last. Infrastructure destroy reads its
    # permanent SSM parameters before their deletion. A secret's remove mints
    # its target credentials through the connection
    # pointer. Stored rows only, never the read-time overlay.
    rows = {_id: stack.get_resource(match={"_id": _id}, overlay_tfstate=False)
            for _id in _ids}
    secret_ids = [_id for _id in _ids
                  if any(_is_ssm_secret(row) for row in rows[_id])]
    # An id with no stored row lands here; its delete finds nothing.
    record_only_ids = [_id for _id in _ids
                       if _id not in secret_ids
                       and not any(_has_state_pointer(row) for row in rows[_id])]
    record_only_ids.sort(
        key=lambda _id: any(_is_connection_pointer(row) for row in rows[_id]))

    # Delete resources: one delete_resource substack call per db_id
    if stack.get_attr("parallel") not in ["None", "null", None, False, "false"]:
        stack.set_parallel()

    for _id in _ids:
        if _id not in secret_ids and _id not in record_only_ids:
            _delete(stack, _id)

    # The barrier covers every delete above and the orders each one emits.
    # must_complete=True drains them all; a failed one holds every delete
    # after it, so those rows stay for the retry. After the barrier the
    # deletes chain: each waits on the previous one and the orders it emits.
    if secret_ids or record_only_ids:
        stack.wait_all(must_complete=True)
        for _id in secret_ids + record_only_ids:
            _delete(stack, _id)

    stack.wait_all()

    return stack.get_results()
