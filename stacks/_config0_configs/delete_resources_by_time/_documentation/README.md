# Resource Cleanup Stack

## Description
This stack handles the cleanup of resources by systematically identifying and removing resources based on specified criteria. It supports both parallel and sequential deletion operations, with the ability to preserve specified resources.

## Variables

### Required

| Name | Description | Default |
|------|-------------|---------|
| ref_schedule_ids | Referenced schedule ID |  |
| keep_resources | Configuration for keep resources | null |

### Optional

| Name | Description | Default |
|------|-------------|---------|
| parallel_overide | Configuration for parallel overide | null |

## Features
- Supports both parallel and sequential resource deletion
- Allows selective resource preservation through keep_resources parameter
- Handles resources with parent/child relationships
- Prioritizes deletion order using checkin values

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
