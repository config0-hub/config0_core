# Delete Schedules and Resources Stack

## Description
This stack manages the deletion of resources and schedules in either parallel or sequential order. It provides options to keep specific resources while deleting others.

## Variables

### Required

| Name | Description | Default |
|------|-------------|---------|
| parallel_ids | Configuration for parallel ids | null |
| sequential_ids | Configuration for sequential ids | null |
| keep_resources | Configuration for keep resources | [ {"provider":"aws","resource_type":"ecr_repo"} ] |

### Optional

| Name | Description | Default |
|------|-------------|---------|
| parallel | Configuration for parallel overide | true |

## Dependencies

### Substacks
- [config0-publish:::delete_schedules](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/delete_schedules/default)
- [config0-publish:::delete_resources_by_time](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/delete_resources_by_time/default)

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