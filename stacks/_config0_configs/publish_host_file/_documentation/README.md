# Remote File Fetcher

## Description
A Config0 stack that fetches the contents of a remote file from a specified host via SSH and publishes the contents as an environment variable.

## Variables

### Required

| Name | Description | Default |
|------|-------------|---------|
| hostname | Server hostname | |
| ssh_key_name | Name label for SSH key | |
| remote_file | Remote file path to fetch | |
| key | Key name to store fetched content | |

## Features
- Securely fetches file contents from remote hosts using SSH
- Publishes file contents to the pipeline environment for use in downstream tasks
- Supports integration with Config0 pipelines

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
