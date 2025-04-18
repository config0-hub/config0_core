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

### Substacks
- [config0:::schedule_delete](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0/schedule_delete/default)

### Execgroups
- [config0-publish:::github::lambda_trigger_stepf](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/github/lambda_trigger_stepf/default)

### Shelloutconfigs
- [config0-publish:::terraform::resource_wrapper](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/shelloutconfigs/config0-publish/terraform/resource_wrapper/default)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>