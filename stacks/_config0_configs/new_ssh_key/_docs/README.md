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

### Substacks
None

### Shelloutconfigs
None

### Execgroups
None

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
</pre>