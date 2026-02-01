# Delete Resources by IDs Stack

## Description
This stack deletes Config0 resources by their document IDs. It accepts a comma-separated list of resource `db_ids` and calls `config0-publish:::delete_resource` once per ID. Deletions can run in parallel or sequentially.

## Variables

### Required

| Name | Description | Default |
|------|-------------|---------|
| db_ids | Comma-separated list of resource document IDs (_id) to delete | null |

### Optional

| Name | Description | Default |
|------|-------------|---------|
| parallel | When true, run delete_resource calls in parallel | true |

## Dependencies

### Substacks
- [config0-publish:::delete_resource](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/delete_resource)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>
