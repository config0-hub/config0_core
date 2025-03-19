# Resource Publisher

## Description
This stack retrieves a specific resource and allows you to publish selected data fields with optional key mapping and prefixing. This utility stack enables controlled exposure of resource data to the Config0 UI.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| resource_type | Resource type used to categorized main IaC code/automation | |

### Optional
| Name | Description | Default |
| ------ | ----------- | ------- |
| name | Configuration for name | "null" |
| match_hash | Match hash in base64 | "null" |
| ref_schedule_id | Referenced schedule ID | "null" |
| labels_hash | Resource label in base64 | "null" |
| publish_keys_hash | Configuration for publish keys hash | "null" |
| map_keys_hash | Configuration for map keys hash | "null" |
| prefix_key | Configuration for prefix key | "null" |

## Features
- Resource lookup based on type, name, schedule ID, or custom match criteria
- Filtering of resource data by selecting specific keys to publish
- Renaming of keys for better readability in the UI
- Key prefixing to organize published data
- Support for label-based resource matching
- JSON serialization of complex data types (lists, dictionaries)

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
