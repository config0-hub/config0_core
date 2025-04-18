# Run Metadata Stack

## Description
This stack is designed to add run metadata to the Config0 platform. It takes provided run ID, data, and metadata key (mkey) parameters and adds them to the run metadata.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| run_id | Config0 builtin - id of a run for the instance of a stack/workflow | &nbsp; |
| data | Data to be added to run metadata | &nbsp; |

### Optional
| Name | Description | Default |
|------|-------------|---------|
| mkey | Metadata key for storing/referencing data | "default" |

## Dependencies

### ShelloutConfigs
- [config0-publish:::terraform::resource_wrapper](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/shelloutconfigs/config0-publish/terraform/resource_wrapper/default)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>