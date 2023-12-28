# This stack creates a variables set to that can be query with a single selector to inserted into other stack as arguments.

**Required**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| vars_set_name   | the name of the variables set       | string   |    |
| env_vars_hash   | environment variables key/value (dict) converted to base64 hash      | string   |    |
| labels_hash   | query labels key/value (dict) converted to base64 hash      | string   |    |
| arguments_hash   | arguments key/value (dict) converted to base64 hash      | string   |    |
| env_vars_hash   | key/value (dict) that is converted to base64 hash      | string   |    |
| evaluate   | whether to evaluate to queries to immediate values      | null/True   | null    |

- if evaluate set to True means the platform will immediately render the query to value(s) to be stored.  
- if evaluate is set to null, then value(s) is not rendered until used.  good for variables that change.

networking example
```
global:
   selectors:
     aws_base:
       match_keys:
         provider: aws
       match_labels:
         environment: eval
         purpose: test
selectors:
   vpc_info:
     match_base: aws_base
     match_params:
       must_exists: True
       resource_type: vpc
   private_subnet_info:
     match_base: aws_base
     match_keys:
       name: private
     match_params:
       resource_type: subnet
   private_subnet_info:
     match_base: aws_base
     match_keys:
       name: private
     match_params:
       resource_type: subnet
   public_subnet_info:
     match_base: aws_base
     match_keys:
       name: public
     match_params:
       resource_type: subnet
   sg_database_info:
     match_base: aws_base
     match_keys:
       name: database
     match_params:
       must_be_one: True
       resource_type: security_group
   sg_bastion_info:
     match_base: aws_base
     match_keys:
       name: bastion
     match_params:
       must_be_one: True
       resource_type: security_group
   sg_web_info:
     match_base: aws_base
     match_keys:
       name: web
     match_params:
       must_be_one: True
       resource_type: security_group
   sg_api_info:
     match_base: aws_base
     match_keys:
       name: api
     match_params:
       must_be_one: True
       resource_type: security_group
custom:
   vars_set:
       stack_name: config0-hub:::vars_set
       arguments:
         vars_set_name: vpcinfo_dev
         evaluate: null
         env_vars_hash:
           AWS_DEFAULT_REGION: eu-west-1
         labels_hash:
           aws_default_region: eu-west-1
           environment: eval
           purpose: test
           product: config0
           area: networking
           cloud: aws
         arguments_hash:
           vpc_name: selector:::vpc_info::name
           vpc_id: selector:::vpc_info::vpc_id
           public_subnet_ids: selector:::public_subnet_info::subnet_id:csv
           private_subnet_ids: selector:::private_subnet_info::subnet_id:csv
           db_sg_id: selector:::sg_database_info::sg_id
           bastion_sg_id: selector:::sg_bastion_info::sg_id
           web_sg_id: selector:::sg_web_info::sg_id
           api_sg_id: selector:::sg_api_info::sg_id
           ami_filter: Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*
           ami_owner: 099720109477
       to_base64:
         - env_vars_hash
         - labels_hash
         - arguments_hash
       selectors:
         - vpc_info
         - public_subnet_info
         - private_subnet_info
         - sg_bastion_info
         - sg_database_info
         - sg_web_info
         - sg_api_info
       credentials:
           - reference: eval-config0-iam
             orchestration: true
```
