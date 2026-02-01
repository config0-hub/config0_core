# IAC CI Setup

## Description
This stack sets up Infrastructure as Code Continuous Integration (IAC CI) for stateful resources. It configures the necessary environment variables and repository settings to enable CI/CD workflows for infrastructure code.

## Variables

### Required

| Name | Description | Default |
|------|-------------|---------|
| stateful_id | Stateful ID for storing the resource code/state | &nbsp; |
| resource_type | Resource type used to categorized main IaC code/automation | &nbsp; |

### Optional

| Name | Description | Default |
|------|-------------|---------|
| iac_ci_repo | Repository for storing infrastructure code | &nbsp; |
| iac_ci_pr_strategy | Configuration for iac ci pr strategy | branch (choices: branch, folder) |

## Dependencies

### Shelloutconfigs
- [config0-publish:::config0_core::iac_ci_s3_to_repo](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/shelloutconfigs/config0-publish/config0_core/iac_ci_s3_to_repo/default)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>