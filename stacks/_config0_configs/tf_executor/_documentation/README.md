# Terraform Resource Execution and Management

## Description
This module manages Terraform/OpenTofu resource execution and interacts with the Config0 resource database. It provides a framework for deploying infrastructure as code using different runtime environments including AWS CodeBuild, Lambda functions, and Docker containers.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| provider | Cloud provider to use (aws, do, etc.) | &nbsp; |
| execgroup_ref | Reference to the execution group | &nbsp; |
| resource_name | Name of the resource to be created | &nbsp; |
| resource_type | Resource type used to categorize main IaC code/automation | &nbsp; |
| resource_configs_hash | Base64 encoded resource configuration | &nbsp; |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| terraform_type | Type of terraform configuration | null |
| tf_vars_hash | Base64 encoded terraform variables | null |
| resource_id | Configuration for resource id | null |
| runtime_env_vars | Runtime environment variables | null |
| timeout | Configuration for timeout | 1650 |
| cloud_tags_hash | Resource tags for cloud provider | null |
| stateful_id | Stateful ID for storing the resource code/state | _random |
| remote_stateful_bucket | S3 bucket for Terraform state | null |
| publish_to_saas | Boolean to publish values to config0 SaaS UI | true |
| tf_runtime | Terraform runtime version | tofu:1.9.1 |
| iac_ci_pr_strategy | Configuration for iac ci pr strategy (choices: branch, folder) | branch |
| drift_protection | Boolean to enable drift detection | true |
| ssm_name | SSM parameter name | &nbsp; |

## Dependencies

### Substacks
- [config0-publish:::output_resource_to_ui](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/output_resource_to_ui)
- [config0-publish:::setup_iac_ci_on_github](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/setup_iac_ci_on_github)

### Execgroups
- The execgroup identified by `stack.execgroup_ref` with type "cloud_resource"

### Shelloutconfigs
- No shelloutconfigs are explicitly added in the provided code

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>