# Debug Machine

## Description
This stack creates a debug machine that sleeps for a configurable amount of time, providing a platform for debugging processes or configurations.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| ttl | Time to live in seconds for the debug machine | 7200 |

## Features
- Creates a debug worker in the panel
- Sleeps for a configurable amount of time
- Provides a platform for debugging

## Dependencies

### Substacks
- [config0-publish:::config0_core::publish_worker](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/config0_core/publish_worker)

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.