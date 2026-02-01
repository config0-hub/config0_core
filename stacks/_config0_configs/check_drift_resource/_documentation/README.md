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
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
</pre>