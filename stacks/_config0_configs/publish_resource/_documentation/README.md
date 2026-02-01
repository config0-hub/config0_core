# Resource Publisher Stack

## Description

This stack retrieves a specified resource from the Config0 database and publishes selected properties to the Config0 UI. It allows for customization of how the properties are displayed through key mapping and prefixing.

## Variables

### Required

| Name | Description | Default |
|------|-------------|---------|
| resource_type | Resource type used to categorized main IaC code/automation | &nbsp; |

### Optional

| Name | Description | Default |
|------|-------------|---------|
| name | Configuration for name | null |
| ref_schedule_id | Referenced schedule ID | null |
| labels_hash | Resource label in base64 | null |
| publish_keys_hash | Configuration for publish keys hash | null |
| map_keys_hash | Configuration for map keys hash | null |
| prefix_key | Configuration for prefix key | null |

## Dependencies

The stack has no dependencies as it doesn't use any substacks, execgroups, or shelloutconfigs.

### Substacks
None

### Execgroups
None

### Shelloutconfigs
None

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>