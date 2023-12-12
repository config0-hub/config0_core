# TF Constructor stack is a helper for terraform automation

**Required**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| resource_type   | the resource type       | string   |    |
| resource_name   | the resource name       | string   |    |
| dst_exec_group   | the execgroup to execute       | string   |    |


**Optional**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
cloud_tags_hash | the tags for the resources in the cloud as base64 | string  | None         |

``` in a stack
```
