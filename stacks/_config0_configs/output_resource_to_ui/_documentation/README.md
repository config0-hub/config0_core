# Resource Publisher

## Description
This stack retrieves a specific resource and allows you to publish selected data fields with optional key mapping and prefixing. This utility stack enables controlled exposure of resource data to the Config0 UI.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| resource_type | Resource type used to categorize main IaC code/automation | &nbsp; |

### Optional
| Name | Description | Default |
|------|-------------|---------|
| name | Resource name to match | "null" |
| match_hash | Match hash in base64 | "null" |
| ref_schedule_id | Referenced schedule ID | "null" |
| labels_hash | Resource label in base64 | "null" |
| publish_keys_hash | Keys in the resource to publish in base64 | "null" |
| map_keys_hash | Map keys to change the key name that shows up on the UI | "null" |
| prefix_key | Prefix for each key | "null" |

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