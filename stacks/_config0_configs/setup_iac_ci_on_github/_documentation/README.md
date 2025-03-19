# IAC CI Setup

## Description
This stack sets up Infrastructure as Code Continuous Integration (IAC CI) for stateful resources. It configures the necessary environment variables and repository settings to enable CI/CD workflows for infrastructure code.

## Variables

### Required

| Name | Description | Default |
|------|-------------|---------|
| stateful_id | Stateful ID for storing the resource code/state | |
| resource_type | Resource type used to categorized main IaC code/automation | |

### Optional

| Name | Description | Default |
|------|-------------|---------|
| iac_ci_repo | Repository for storing infrastructure code | |
| iac_ci_pr_strategy | Configuration for iac ci pr strategy | branch (choices: branch, folder) |

## Features
- Sets up IAC CI environment with appropriate folder structure and branch naming
- Automatically transfers infrastructure code from S3 to Git repository
- Updates resource records with CI information
- Supports different PR strategies (branch per environment or folder per environment)

## Dependencies

### Shelloutconfigs
- [config0-publish:::config0_core::iac_ci_s3_to_repo](https://api-app.config0.com/web_api/v1.0/assets/shelloutconfigs/config0-publish/config0_core/iac_ci_s3_to_repo)

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
