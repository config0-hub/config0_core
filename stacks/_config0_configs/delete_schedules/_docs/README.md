# Schedule Delete Stack

## Description

This stack allows for the deletion of schedules in Config0, with support for both parallel and sequential deletion operations.

## Variables

### Required

| Name | Description | Default |
|------|-------------|---------|
| parallel_ids | IDs of schedules to be deleted in parallel | "null" |
| sequential_ids | IDs of schedules to be deleted sequentially | "null" |
| destroy_instance | Flag to determine if the instance should be destroyed | "null" |

### Optional

| Name | Description | Default |
|------|-------------|---------|
| parallel_overide | Configuration for parallel override | "null" |

## Dependencies

The code analysis shows this stack does not have any dependencies.

### Substacks
None

### Execgroups
None

### Shelloutconfigs
None

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>