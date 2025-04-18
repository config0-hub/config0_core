# Resource Destroy Stack

## Description

This stack enables the destruction of resources in Config0 by matching specified criteria. It provides a safe way to remove resources by requiring at least one matching parameter to prevent unintended wide-scope deletions.

## Variables

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| resource_type | Resource type used to categorize main IaC code/automation | "null" |
| name | Configuration for name | "null" |
| hostname | Server hostname | "null" |
| ref_schedule_id | Referenced schedule ID | "null" |
| must_exists | Flag to ensure the resource exists | "null" |

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