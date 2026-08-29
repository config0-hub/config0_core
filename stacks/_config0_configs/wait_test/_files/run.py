"""Wait-row integration test stack (plan wait-all-wt-scoped-ordering, P9).

One stack, one required argument ``scenario``; each config0.yaml under
config0_yamls_repos/wait-tests/<scenario>/ targets one wait condition
(decision 16). Orders are cheap shell orders (echo / sleep / exit 1); no
cloud resource is created. Scenarios (e) and (h) reference the substack
config0-hub:::config0_core::wait_test_child (mode=slow / mode=fast).

Legend: ok = "echo ok", bad = "exit 1", slow = "sleep 20". E = this stack's
exec order. A = the displayed checkpoint/parallel anchor row. ** = the wait
row (check-wait::api, role check/wait/instance, dependencies.prior_all=true,
retries=-1, base_wt=E, scoped to E.*). Every order inside a parallel window
depends on A alone. A depends on the order active before set_parallel(),
falling back to E for a first emission.

(a) plain wait:               set_parallel(); ok; ok; ok; wait_all(); ok
  E.005 A  E.010 ok  E.015 ok  E.020 ok  E.025 ** WAIT  E.030 ok deps=[WAIT]

(b) sibling fails, must_succeed default:
                              set_parallel(); ok; bad; ok; wait_all(); ok
  E.005 A  E.010 ok  E.015 bad  E.020 ok  E.025 ** WAIT  E.030 ok deps=[WAIT]

(c) sibling fails, must_succeed=False:
                              set_parallel(); ok; bad(must_succeed=False); ok; wait_all(); ok
  E.005 A  E.010 ok  E.015 bad(must_succeed=false)  E.020 ok
  E.025 ** WAIT  E.030 ok deps=[WAIT]

(d1) wait_all(must_complete=True), two bad, must_succeed default:
                              set_parallel(); bad; bad; slow; wait_all(must_complete=True); ok
  E.005 A  E.010 bad  E.015 bad  E.020 slow
  E.025 ** WAIT must_complete  E.030 ok deps=[WAIT]

(d2) as d1, must_succeed=False on both bad orders.

(e) grandchild holds the wait: set_parallel(); wait_test_child(slow); wait_all(); ok
  E.005      A
  E.010      instruction/add wait_test_child
  E.010.005  A-child
  E.010.010  slow           (grandchild, in no list)
  E.010.015  ** WAIT-child  base_wt=E.010
  E.010.020  ok
  E.015      ** WAIT        base_wt=E, held by E.010.*
  E.020      ok deps=[WAIT]

(g) sequential order before the batch: slow; set_parallel(); ok; ok; wait_all(); ok
  E.005 slow  E.010 A deps=[slow]  E.015 ok deps=[A]  E.020 ok deps=[A]
  E.025 ** WAIT  E.030 ok deps=[WAIT]

(h) parallel substacks B (fast) and C (slow), C must not hold B's wait:
                              set_parallel(); wait_test_child(fast) as B;
                              wait_test_child(slow) as C; wait_all(); ok
  E.005      A
  E.010      instruction/add B (fast)              base_wt=E
  E.010.005  A-B
  E.010.010  ok  E.010.015 ok  E.010.020 ok         base_wt=E.010
  E.010.025  ** WAIT-B                              base_wt=E.010
  E.010.030  ok deps=[WAIT-B]
  E.015      instruction/add C (slow)  deps=[A]     base_wt=E
  E.015.005  A-C
  E.015.010  slow                                   base_wt=E.015
  E.015.015  ** WAIT-C                              base_wt=E.015
  E.015.020  ok deps=[WAIT-C]
  E.020      ** WAIT-A  deps=[A]                    base_wt=E, held by E.010.* and E.015.*
  E.025      ok deps=[WAIT-A]
"""

OK = "echo ok"
BAD = "exit 1"
SLOW = "sleep 20"


def _ok(stack):
    return stack.add_external_cmd(cmd=OK, role="external/cli/execute")


def _bad(stack, must_succeed=True):
    order = stack.add_external_cmd(cmd=BAD, role="external/cli/execute")
    if not must_succeed:
        order["must_succeed"] = False
    return order


def _slow(stack):
    return stack.add_external_cmd(cmd=SLOW, role="external/cli/execute")


def _child(stack, mode):
    return stack.wait_child.insert(
        display=True,
        arguments={"mode": mode},
        human_description=f"wait_test_child mode={mode}",
    )


def run(stackargs):
    stack = newStack(stackargs)

    stack.parse.add_required(key="scenario", types="str", choices=["a", "b", "c", "d1", "d2", "e", "g", "h"])
    stack.add_substack("config0-hub:::config0_core::wait_test_child", "wait_child")

    stack.init_variables()
    stack.init_substacks()

    scenario = stack.scenario

    if scenario == "g":
        _slow(stack)

    stack.set_parallel()

    if scenario in ("a", "g"):
        _ok(stack)
        _ok(stack)
        if scenario == "a":
            _ok(stack)
    elif scenario == "b":
        _ok(stack)
        _bad(stack)
        _ok(stack)
    elif scenario == "c":
        _ok(stack)
        _bad(stack, must_succeed=False)
        _ok(stack)
    elif scenario == "d1":
        _bad(stack)
        _bad(stack)
        _slow(stack)
    elif scenario == "d2":
        _bad(stack, must_succeed=False)
        _bad(stack, must_succeed=False)
        _slow(stack)
    elif scenario == "e":
        _child(stack, "slow")
    elif scenario == "h":
        _child(stack, "fast")
        _child(stack, "slow")
    else:
        raise ValueError(f"unsupported wait_test scenario: {scenario!r}")

    stack.wait_all(must_complete=scenario in ("d1", "d2"))
    _ok(stack)

    return stack.get_results()
