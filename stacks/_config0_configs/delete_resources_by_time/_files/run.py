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

# The minimal teardown-sufficient projection for a remove order: the row
# identity ``_id`` (the key the CLI confirms removal on after engine
# success), identity (resource_type/provider/name), the STATE POINTER that
# locates the .tfstate to destroy (stateful_id + remote_stateful_bucket),
# and the execution driver (execgroup — mod_execgroup is the write-back's
# recorded name for it).
_TEARDOWN_KEYS = (
    "_id",
    "resource_type",
    "provider",
    "name",
    "stateful_id",
    "remote_stateful_bucket",
    "execgroup",
    "timeout",
)


def _teardown_projection(resource):
    """Project one recorded resource to the minimal set a remove order needs.

    Passing the whole record is not teardown-sufficient by itself: the
    consumer routes on a stack FQN or an execgroup reference plus the state
    pointer, so the projection carries exactly those (the write-back records
    the execgroup as mod_execgroup; map it onto the execgroup driver key).
    """
    projected = {
        key: resource[key]
        for key in _TEARDOWN_KEYS
        if resource.get(key) is not None
    }
    if "execgroup" not in projected and resource.get("mod_execgroup"):
        projected["execgroup"] = resource["mod_execgroup"]
    return projected


def _get_keep_resources(stack):
    """Collect the _ids of resources the project explicitly retains.

    Each keep entry is a match dict (provider / resource_type / name /
    hostname) applied per target schedule id; every matching record's _id
    joins the exclusion set. keep_resources arrives as a real list — no
    deserialization step.
    """
    if not stack.get_attr("keep_resources"):
        return None

    _resource_ids = []

    for _keep_entry in stack.keep_resources:
        for ref_schedule_id in stack.to_list(stack.ref_schedule_ids):
            match = dict(_keep_entry)
            match["ref_schedule_id"] = ref_schedule_id
            stack.logger.debug(f"searching for keep resource {match}")
            resources = stack.get_resource(**match)
            if not resources:
                continue
            for resource in resources:
                stack.logger.debug(f"keep resource id {resource['_id']}")
                _resource_ids.append(resource["_id"])

    stack.logger.debug(f"keep resource ids {_resource_ids}")
    return _resource_ids


def _get_delete_resources(stack, keep_resource_ids=None):
    """Gather engine-teardown candidates per target schedule id.

    Only records carrying a real state pointer (stateful_id) are teardown
    candidates — record-only rows (schedule_vars, job_vars, selectors,
    labels) have no infrastructure behind them and are removed by the final
    cleanup sweep, never by the engine. Candidates are deduplicated by _id,
    filtered by the keep exclusion, and returned in REVERSE creation order
    (later-created first) keyed on the record's created_at — the
    dependency-safe removal order where resources depend on one another.
    """
    added_ids = []
    candidates = []

    for ref_schedule_id in stack.to_list(stack.ref_schedule_ids):
        _resources = stack.get_resource(ref_schedule_id=ref_schedule_id)

        if not _resources:
            continue

        for _resource in _resources:
            _id = _resource.get("_id")
            if _id in added_ids:
                continue
            if keep_resource_ids and _id in keep_resource_ids:
                continue
            if not _resource.get("stateful_id"):
                stack.logger.debug(
                    f"skipping record-only row {_id} (no stateful_id)"
                )
                continue
            if _resource.get("removal_confirmed_at"):
                # The resources table is a durable PROGRESS LEDGER: this
                # row's engine destroy already succeeded (the CLI persisted
                # the confirmation) — a retry must never repeat a confirmed
                # removal. The row itself stays as evidence until the final
                # one-transaction project sweep.
                stack.logger.debug(
                    f"skipping removal-confirmed row {_id} "
                    f"(confirmed at {_resource['removal_confirmed_at']})"
                )
                continue
            added_ids.append(_id)
            candidates.append(_resource)

    candidates = sorted(
        candidates,
        key=lambda r: str(r.get("created_at") or ""),
        reverse=True,
    )

    stack.logger.debug(
        f"teardown candidate ids (reverse creation order) "
        f"{[r.get('_id') for r in candidates]}"
    )

    return [_teardown_projection(resource) for resource in candidates]


def run(stackargs):
    """Main function to process stack arguments and manage resources."""
    stack = newStack(stackargs)

    # required stack args
    stack.parse.add_required(key="keep_resources",
                             default="null")

    stack.parse.add_required(key="ref_schedule_ids")

    stack.parse.add_optional(key="parallel_overide",
                             default="null")

    # Initialize Variables in stack
    stack.init_variables()

    keep_resource_ids = _get_keep_resources(stack)

    candidates = _get_delete_resources(stack,
                                       keep_resource_ids=keep_resource_ids)

    # parallel overide set True: remove everything concurrently (an explicit
    # caller opt-in for independent resources — no ordering guarantee).
    if stack.get_attr("parallel_overide") and candidates:
        stack.logger.debug("Parallel overide set True")
        stack.set_parallel()
        for resource in candidates:
            stack.logger.debug(f"removing resource {resource}")
            stack.remove_resource(**resource)
        return stack.get_results(None)

    # Default: the sequential reverse-creation chain — each remove order
    # depends on the previous one (queue_ids edge), so resources that depend
    # on one another are removed dependency-safe, later-created first.
    for resource in candidates:
        stack.logger.debug(f"removing resource {resource}")
        stack.remove_resource(**resource)

    return stack.get_results(None)
