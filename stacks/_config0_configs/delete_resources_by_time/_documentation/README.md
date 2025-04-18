# Resource Cleanup Stack

## Description
This stack handles the cleanup of resources by systematically identifying and removing resources based on specified criteria. It supports both parallel and sequential deletion operations, with the ability to preserve specified resources.

## Variables

### Required

| Name | Description | Default |
|------|-------------|---------|
| ref_schedule_ids | Referenced schedule ID | &nbsp; |
| keep_resources | Configuration for keep resources | null |

### Optional

| Name | Description | Default |
|------|-------------|---------|
| parallel_overide | Configuration for parallel overide | null |

## Dependencies

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