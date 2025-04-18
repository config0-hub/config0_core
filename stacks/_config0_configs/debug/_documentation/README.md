# Debug Machine

## Description
This stack creates a debug machine that sleeps for a configurable amount of time, providing a platform for debugging processes or configurations.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| ttl | Time to live in seconds for the debug machine | 7200 |

## Dependencies

### Substacks
- [config0-publish:::config0_core::publish_worker](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/stacks/config0-publish/config0_core/publish_worker/default)

### Execgroups
- [config0-publish:::github::lambda_trigger_stepf](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/github/lambda_trigger_stepf/default)

### Shelloutconfigs
- [config0-publish:::terraform::resource_wrapper](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/shelloutconfigs/config0-publish/terraform/resource_wrapper/default)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>