# Resource Publisher

## Description
This stack retrieves a specific resource and allows you to publish selected data fields with optional key mapping and prefixing. This utility stack enables controlled exposure of resource data to the Config0 UI.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| resource_type | Resource type used to categorize main IaC code/automation | &nbsp; |

### Optional
| Name | Description | Default |
|------|-------------|---------|
| name | Resource name to match | "null" |
| match_hash | Match hash in base64 | "null" |
| ref_schedule_id | Referenced schedule ID | "null" |
| labels_hash | Resource label in base64 | "null" |
| publish_keys_hash | Keys in the resource to publish in base64 | "null" |
| map_keys_hash | Map keys to change the key name that shows up on the UI | "null" |
| prefix_key | Prefix for each key | "null" |

## Dependencies

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
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
</pre>