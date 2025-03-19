# Worker Info Retrieval

## Description
This stack retrieves worker information based on the provided run ID or an override run ID.

## Variables

### Required
None

### Optional
| Name | Description | Default |
|------|-------------|---------|
| overide_run_id | Alternative run ID for worker lookup | "null" |

## Features
- Retrieves worker information using run_id
- Supports override run ID for flexibility
- Publishes worker information to the stack

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
