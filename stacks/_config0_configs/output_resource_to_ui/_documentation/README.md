# Queries the Config0 Resource Db and outputs the publish keys into the UI in the Output Tab

**Required**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| resource_type   | the resource type       | string   |    |


**Optional**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| name   | the name resource | string   |    |
| match_hash   | the json match dictionary converted to b64 hash | string   |    |
| labels_hash   | the json labels dictionary converted to b64 hash | string   |    |
| ref_schedule_id   | the reference schedule_id for the query | string   |    |
| publish_keys_hash   | the keys to publish converted to b64  | string   |    |
| map_keys_hash   | map keys b64 (dict) is use to change the key name that shows up on the UI (b64) | string   |    |
| prefix_key   | prefix for each key (b64) | string   |    |

``` in a stack

      stack.add_substack('config0-hub:::output_resource_to_ui')

      ...
      ...

    # publish the info
      keys_to_publish = [ "name",
                          "id",
                          "arn",
                          "resource_type" ]

      overide_values = { "name":stack.name }
      overide_values["publish_keys"] = stack.b64_encode(keys_to_publish)

      default_values = { "resource_type":stack.resource_type }

      inputargs = { "default_values":default_values,
                    "overide_values":overide_values }

      inputargs["automation_phase"] = "infrastructure"
      inputargs["human_description"] = 'Publish resource info for {}'.format(stack.resource_type)
      stack.output_resource_to_ui.insert(display=True,**inputargs)
```
