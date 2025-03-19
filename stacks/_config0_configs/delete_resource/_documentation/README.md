# Resource Destroy Stack

## Description

This stack enables the destruction of resources in Config0 by matching specified criteria. It provides a safe way to remove resources by requiring at least one matching parameter to prevent unintended wide-scope deletions.

## Variables

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| resource_type | Resource type used to categorized main IaC code/automation | "null" |
| name | Configuration for name | "null" |
| hostname | Server hostname | "null" |
| ref_schedule_id | Referenced schedule ID | "null" |
| must_exists | Flag to ensure the resource exists | "null" |

## Features

- Prevents wide-open resource destruction by requiring at least one matching parameter
- Supports multiple ways to identify resources (name, hostname, resource type, or schedule ID)
- Validates that only one resource matches the specified criteria before deletion
- Throws clear error messages when no matching resource is found or when multiple resources match

## License

Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
