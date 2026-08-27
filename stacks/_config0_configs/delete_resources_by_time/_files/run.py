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

# A recorded infrastructure teardown transports ONLY the row id. The CLI reads
# the immutable execution asset, merged mod_params/destroy_params, and tfstate
# pointer from that QHost row. Passing an asset here would let caller state drift
# away from the exact version that created the resource.
_TEARDOWN_KEYS = ("_id",)


def _teardown_projection(resource):
    """Project one recorded resource to its id-only immutable destroy request."""
    projected = {
        key: resource[key]
        for key in _TEARDOWN_KEYS
        if resource.get(key) is not None
    }
    if not projected.get("_id"):
        raise ValueError("state-backed resource teardown requires the recorded _id")
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


_STATE_POINTER_KEYS = ("stateful_id",
                       "remote_stateful_location",
                       "remote_stateful_bucket")


def _has_state_pointer(resource):
    """A row carrying any state pointer is real infrastructure."""
    return any(resource.get(key) not in (None, "", "null", "None")
               for key in _STATE_POINTER_KEYS)


def _checkin_sort_key(resource):
    """The original's checkin sort semantics (``_main/run.py:64-68``): the
    string form of the integer checkin, with a missing/unparseable checkin
    coerced to 1000000000 so it sorts LAST under the descending sort."""
    try:
        checkin = int(resource["checkin"])
    except (KeyError, TypeError, ValueError):
        checkin = 1000000000
    return str(checkin)


def _get_delete_resources(stack, keep_resource_ids=None):
    """Gather EVERY matched row per target schedule id - no row left behind.

    Mirrors ``.original``'s uniform remove_resource: every matched row of
    every resource_type is torn down by the stack's own run, per schedule
    id. The split is only HOW each row dies:

    - a row carrying a state pointer is real infrastructure → an
      execution-backed ``remove_resource`` teardown order;
    - a record-only row (schedule_vars, job_vars, selectors, labels,
      reference, vars_set) has nothing to run → the inline
      ``unrecord_resource`` QHost row delete.

    Teardown candidates are deduplicated by _id and filtered by the keep
    exclusion, then split into the original's two tiers
    (``_main/run.py:37-89``):

    - the PARALLEL tier: rows flagged ``query_only`` or ``parent`` —
      independent resources torn down concurrently;
    - the SEQUENTIAL tier: everything else, in reverse ``checkin`` order
      (latest checkin first, missing checkin last) — the dependency-safe
      removal order where resources depend on one another.

    Returns ``(parallel_requests, sequential_requests, record_only_ids)``.
    """
    added_ids = []
    parallel_candidates = []
    sequential_candidates = []
    record_only_ids = []
    matched_row_count = 0

    for ref_schedule_id in stack.to_list(stack.ref_schedule_ids):
        _resources = stack.get_resource(ref_schedule_id=ref_schedule_id)

        if not _resources:
            continue

        matched_row_count += len(_resources)
        for _resource in _resources:
            _id = _resource.get("_id")
            if _id in added_ids:
                continue
            if keep_resource_ids and _id in keep_resource_ids:
                continue
            if not _has_state_pointer(_resource):
                stack.logger.debug(
                    f"record-only row {_id} "
                    f"(resource_type={_resource.get('resource_type')}) - "
                    "inline unrecord"
                )
                added_ids.append(_id)
                record_only_ids.append(_id)
                continue
            if _resource.get("removal_confirmed_at"):
                # The resources table is a durable PROGRESS LEDGER: this
                # row's engine destroy already succeeded (the CLI persisted
                # the confirmation) — a retry must never repeat a confirmed
                # removal.
                stack.logger.debug(
                    f"skipping removal-confirmed row {_id} "
                    f"(confirmed at {_resource['removal_confirmed_at']})"
                )
                continue
            added_ids.append(_id)
            if _resource.get("query_only") or _resource.get("parent"):
                parallel_candidates.append(_resource)
            else:
                sequential_candidates.append(_resource)

    # A repeated project destroy legitimately finds no rows after the first
    # sweep. Keep that retry idempotent, but make a broken project link visible.
    if matched_row_count == 0:
        warning = (
            "WARNING: zero resources matched the project's schedule ids "
            f"{stack.to_list(stack.ref_schedule_ids)!r}; nothing to destroy. "
            "If this project should still have resources, the resource-to-project "
            "link is broken."
        )
        stack.logger.warning(warning)
        stack.output_to_ui({"warning": warning})

    sequential_candidates = sorted(
        sequential_candidates,
        key=_checkin_sort_key,
        reverse=True,
    )

    stack.logger.debug(
        f"parallel teardown candidate ids "
        f"{[r.get('_id') for r in parallel_candidates]}"
    )
    stack.logger.debug(
        f"sequential teardown candidate ids (reverse checkin order) "
        f"{[r.get('_id') for r in sequential_candidates]}"
    )

    parallel_requests = [_teardown_projection(r) for r in parallel_candidates]
    sequential_requests = [_teardown_projection(r) for r in sequential_candidates]
    return parallel_requests, sequential_requests, record_only_ids


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

    parallel_requests, sequential_requests, record_only_ids = _get_delete_resources(
        stack,
        keep_resource_ids=keep_resource_ids)

    # Record-only rows (labels / selectors / schedule_vars / job_vars /
    # reference / vars_set) have no infrastructure behind them: nothing runs,
    # so their teardown is the inline QHost row delete - done here by the
    # stack itself, per schedule id, exactly like .original's uniform
    # remove_resource covered every matched row. NO row is left for a later
    # SaaS-side sweep.
    for record_only_id in record_only_ids:
        stack.logger.debug(f"unrecording record-only row {record_only_id}")
        stack.unrecord_resource(_id=record_only_id)

    # parallel overide set True: remove everything concurrently (an explicit
    # caller opt-in for independent resources — no ordering guarantee).
    # Mirrors the original (_main/run.py:143-151): the combined tier list,
    # all removed inside one parallel window.
    if stack.get_attr("parallel_overide") and (parallel_requests or sequential_requests):
        stack.logger.debug("Parallel overide set True")
        stack.set_parallel()
        for resource in parallel_requests + sequential_requests:
            stack.logger.debug(f"removing resource {resource}")
            stack.remove_resource(**resource)
        return stack.get_results(None)

    # Two tiers, as the original (_main/run.py:153-167): the independent
    # (query_only/parent) tier torn down concurrently under set_parallel(),
    # then unset_parallel() emits the check-wait::api wait row so the
    # sequential tier waits on the whole batch.
    if parallel_requests:
        stack.set_parallel()
        for resource in parallel_requests:
            stack.logger.debug(f"removing resource {resource}")
            stack.remove_resource(**resource)
        stack.unset_parallel()

    # The sequential reverse-checkin chain — each remove order depends on
    # the previous one (queue_ids edge), so resources that depend on one
    # another are removed dependency-safe, latest checkin first.
    for resource in sequential_requests:
        stack.logger.debug(f"removing resource {resource}")
        stack.remove_resource(**resource)

    return stack.get_results(None)
