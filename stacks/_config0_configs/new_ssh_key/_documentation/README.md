# SSH Key Management

## Description
This stack creates SSH keys for secure resource access in cloud environments. It allows for creating new SSH keys or deleting and recreating existing ones with the clobber option.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| key_name or name | SSH key identifier for resource access | &nbsp; |

### Optional
| Name | Description | Default |
|------|-------------|---------|
| name | Configuration for name | null |
| key_name | SSH key identifier for resource access | null |
| schedule_id | config0 builtin - id of schedule associated with a stack/workflow | null |
| run_id | config0 builtin - id of a run for the instance of a stack/workflow | null |
| job_instance_id | config0 builtin - id of a job instance of a job in a schedule | null |
| job_id | config0 builtin - id of job in a schedule | null |
| clobber | Clobber/delete key if it exists | null |

## Dependencies

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