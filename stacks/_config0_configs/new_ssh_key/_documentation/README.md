# SSH Key Management

## Description
This stack creates SSH keys for secure resource access in cloud environments. It allows for creating new SSH keys or deleting and recreating existing ones with the clobber option.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| key_name or name | SSH key identifier for resource access |  |

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

## Features
- Creates SSH keys with unique identifiers
- Option to clobber (delete and recreate) existing keys
- Tracks job and schedule metadata for config0 integration
- Associates keys with appropriate run context (job, schedule, etc.)

## Dependencies

### Substacks
- [cloud/ssh_keys:::ssh_key](https://api-app.config0.com/web_api/v1.0/stacks/cloud/ssh_keys)

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
