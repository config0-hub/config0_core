# Publish the info of the resource

    stack.parse.add_required(key="resource_type",default="null")

    stack.parse.add_optional(key="name",default="null")
    stack.parse.add_optional(key="match_hash",default="null")  # match hash in base64
    stack.parse.add_optional(key="ref_schedule_id",default="null")

    stack.parse.add_optional(key="publish_keys_hash",default="null")  # keys in the resource to publish in base64
    stack.parse.add_optional(key="map_keys_hash",default="null")  # map keys b64 (dict) is use to change the key name that shows up on the UI
    stack.parse.add_optional(key="prefix_key",default="null")  # prefix is prefix for each key


**Required**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| resource_type   | the resource type       | string   |    |


**Optional**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| name   | the name resource | string   |    |
| match_hash   | the json match dictionary converted to b64 hash | string   |    |
| ref_schedule_id   | the reference schedule_id for the query | string   |    |
| publish_keys_hash   | the keys to publish converted to b64  | string   |    |
| map_keys_hash   | map keys b64 (dict) is use to change the key name that shows up on the UI (b64) | string   |    |
| prefix_key   | prefix for each key (b64) | string   |    |
