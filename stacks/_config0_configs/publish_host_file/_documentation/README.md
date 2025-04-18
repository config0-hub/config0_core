# Remote File Fetcher

## Description
A Config0 stack that fetches the contents of a remote file from a specified host via SSH and publishes the contents as an environment variable.

## Variables

### Required

| Name | Description | Default |
|------|-------------|---------|
| hostname | Server hostname | &nbsp; |
| ssh_key_name | Name label for SSH key | &nbsp; |
| remote_file | Remote file path to fetch | &nbsp; |
| key | Key name to store fetched content | &nbsp; |

## Dependencies

### ShelloutConfigs
- [config0-publish:::terraform::resource_wrapper](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/shelloutconfigs/config0-publish/terraform/resource_wrapper/default)

### ExecGroups
- [config0-publish:::github::lambda_trigger_stepf](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/github/lambda_trigger_stepf/default)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>