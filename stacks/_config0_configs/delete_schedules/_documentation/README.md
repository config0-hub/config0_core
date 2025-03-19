# Schedule Delete Stack

## Description

This stack allows for the deletion of schedules in Config0, with support for both parallel and sequential deletion operations.

## Variables

### Required

| Name | Description | Default |
|------|-------------|---------|
| parallel_ids | IDs of schedules to be deleted in parallel | "null" |
| sequential_ids | IDs of schedules to be deleted sequentially | "null" |
| destroy_instance | Flag to determine if the instance should be destroyed | "null" |

### Optional

| Name | Description | Default |
|------|-------------|---------|
| parallel_overide | Configuration for parallel overide | "null" |

## Features

- Supports both parallel and sequential schedule deletion
- Can process single IDs or lists of IDs
- Flexible execution control with parallel override option
- Handles dependencies between deletion operations

## Dependencies

### Substacks

- [schedule delete](https://api-app.config0.com/web_api/v1.0/stacks/config0/schedule_delete)

## License

Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
