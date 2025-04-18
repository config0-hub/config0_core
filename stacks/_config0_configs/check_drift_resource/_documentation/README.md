# Resource Validation Stack

## Description
This stack provides resource validation functionality by verifying the existence and uniqueness of a resource based on its ID and optional parameters like resource type and schedule ID.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| resource_id | Configuration for resource id | &nbsp; |

### Optional
| Name | Description | Default |
|------|-------------|---------|
| resource_type | Resource type used to categorize main IaC code/automation | "null" |
| ref_schedule_id | Referenced schedule ID | "null" |

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