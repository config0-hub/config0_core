# Config0 Variable Set Manager

## Description
This stack allows you to create and manage variable sets in Config0. It handles the creation of environment variables, labels, and arguments that can be used in other stacks and workflows.

## Variables

### Required
| Name | Description | Default |
|------|-------------|---------|
| vars_set_name | Name of the variable set to be created |  |

### Optional
| Name | Description | Default |
| ---- | ----------- | ------- |
| env_vars_hash | Environment variables in base64 encoded format | 'null' |
| labels_hash | Resource label in base64 | 'null' |
| arguments_hash | Arguments in base64 encoded format | 'null' |
| evaluate | Determines whether to evaluate arguments | 'null' |

## Features
- Creates variable sets to be used across Config0 stacks
- Supports base64 encoded input for environment variables, labels, and arguments
- Provides optional evaluation of arguments
- Automatically inserts variable sets with appropriate labels

## Dependencies

### Shelloutconfigs
- [external/cli/execute](https://api-app.config0.com/web_api/v1.0/assets/shelloutconfigs/external/cli/execute)

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
