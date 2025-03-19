# Resource Validation Stack

## Description
This stack provides resource validation functionality by verifying the existence and uniqueness of a resource based on its ID and optional parameters like resource type and schedule ID.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| resource_id | Configuration for resource id |  |

### Optional
| Name | Description | Default |
|------|-------------|---------|
| resource_type | Resource type used to categorized main IaC code/automation | "null" |
| ref_schedule_id | Referenced schedule ID | "null" |

## Features
- Validates resource existence 
- Ensures resource uniqueness
- Supports filtering by multiple criteria (ID, resource type, schedule ID)
- Error handling for multiple matching resources

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.