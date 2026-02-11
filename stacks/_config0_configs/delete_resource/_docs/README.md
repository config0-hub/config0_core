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

Based on the code analysis, this stack doesn't explicitly declare any dependencies using `add_execgroup`, `add_shelloutconfig`, or `add_substack` methods. It appears to be a standalone utility that relies only on the core functionality of the Config0 framework.

### Substacks

None

### ExecGroups

None

### ShelloutConfigs

None

## License

<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>