# SaaS Report Schedule

## Description
This stack provides callback reporting functionality to the Config0 SaaS platform. It reports status updates and handles payload transfers during workflow execution.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| callback_api_endpoint | API endpoint URL for callback reporting | &nbsp; |
| callback_token | Authentication token for callbacks | &nbsp; |
| sched_token | Schedule token for authentication | &nbsp; |
| status | Current execution status | &nbsp; |
| bucket_key | S3 bucket key for payload storage | "null" |
| cluster_id | Cluster identifier | "null" |
| project_id | Project identifier in Config0 | "null" |
| sched_destroy | Schedule destruction flag | "null" |

### Optional
| Name | Description | Default |
|------|-------------|---------|
| payload | Raw payload data | "null" |
| payload_hash | Base64 encoded payload data | "null" |

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
the Free Software Foundation, version 3 of the License.
</pre>