**Description**

  - A stack around builtins that deletes and create ssh keys to be 
    uploaded to aws, digitalocean, gcp, etc ...

**Required**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| name   | name of the ssh key                 | string   | None         |

**Sample entry**

```
infrastructure:
   ssh_upload:
       stack_name: config0-hub:::new_ssh_key
       arguments:
          name: config0-test-do-key
```
