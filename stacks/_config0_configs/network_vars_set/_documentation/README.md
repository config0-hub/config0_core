# Config0 Variable Set Manager

## Description
This stack allows you to create and manage variable sets in Config0. It handles the creation of environment variables, labels, and arguments that can be used in other stacks and workflows.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| vars_set_name | Name of the variable set to be created | &nbsp; |

### Optional
| Name | Description | Default |
| ---- | ----------- | ------- |
| env_vars_hash | Environment variables in base64 encoded format | 'null' |
| labels_hash | Resource label in base64 | 'null' |
| arguments_hash | Arguments in base64 encoded format | 'null' |
| evaluate | Determines whether to evaluate arguments | 'null' |

## Dependencies

### Execgroups
- [config0-publish:::github::lambda_trigger_stepf](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/github/lambda_trigger_stepf/default)

### Shelloutconfigs
- [config0-publish:::terraform::resource_wrapper](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/shelloutconfigs/config0-publish/terraform/resource_wrapper/default)
- [external/cli/execute](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/shelloutconfigs/external/cli/execute/default)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>