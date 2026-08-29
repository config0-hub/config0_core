"""Wait-row integration child stack (plan wait-all-wt-scoped-ordering, P9).

Used by wait_test scenarios (e) and (h) as a substack. Emits cheap shell
orders only, no cloud resources.

mode=slow (default):   set_parallel(); slow; wait_all(); ok
mode=fast:             set_parallel(); ok; ok; ok; wait_all(); ok

Expected orders, E = this stack's exec order (the parent's substack order),
A = the displayed checkpoint/parallel anchor:

  mode=slow
  E.005  A                                      deps=[E]
  E.010  external/cli/execute  sleep 20         deps=[A]
  E.015  check/wait/instance   ** WAIT          prior_all, deps=[A]  base_wt=E
  E.020  external/cli/execute  echo ok           deps=[WAIT]

  mode=fast
  E.005  A                                      deps=[E]
  E.010  external/cli/execute  echo ok           deps=[A]
  E.015  external/cli/execute  echo ok           deps=[A]
  E.020  external/cli/execute  echo ok           deps=[A]
  E.025  check/wait/instance   ** WAIT          prior_all, deps=[A]  base_wt=E
  E.030  external/cli/execute  echo ok           deps=[WAIT]
"""

SLOW = "sleep 20"
OK = "echo ok"


def run(stackargs):
    stack = newStack(stackargs)

    stack.parse.add_optional(
        key="mode",
        types="str",
        default="slow",
        choices=["slow", "fast"],
    )

    stack.init_variables()

    stack.set_parallel()
    if stack.mode == "slow":
        stack.add_external_cmd(cmd=SLOW, role="external/cli/execute")
    else:
        for _ in range(3):
            stack.add_external_cmd(cmd=OK, role="external/cli/execute")
    stack.wait_all()
    stack.add_external_cmd(cmd=OK, role="external/cli/execute")

    return stack.get_results()
