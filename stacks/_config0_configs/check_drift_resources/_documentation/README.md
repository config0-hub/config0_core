# Drift Protection Resource Check

## Description
This stack checks for configuration drift across resources with drift protection enabled. It can optionally filter resources by type or schedule ID to validate that infrastructure matches the expected state.

## Variables

### Required Variables
| Name | Description | Default |
|------|-------------|---------|
| drift_protection | Boolean to enable drift detection | "True" |

### Optional Variables
| Name | Description | Default |
|------|-------------|---------|
| ref_schedule_id | Referenced schedule ID | "null" |
| resource_type | Resource type used to categorize main IaC code/automation | "null" |

## Dependencies

### Substacks
- [config0-publish:::config0_core::check_drift_resource](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/config0_core/check_drift_resource/default)

### Shelloutconfigs
- [config0-publish:::terraform::resource_wrapper](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/shelloutconfigs/config0-publish/terraform/resource_wrapper/default)

### Execgroups
- [config0-publish:::github::lambda_trigger_stepf](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/github/lambda_trigger_stepf/default)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>