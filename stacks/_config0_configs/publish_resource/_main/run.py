def run(stackargs):

    import copy

    stack = newStack(stackargs)

    stack.parse.add_required(key="resource_type", 
                             default="null")

    stack.parse.add_optional(key="name", 
                             default="null")

    stack.parse.add_optional(key="ref_schedule_id", 
                             default="null")

    stack.parse.add_optional(key="labels_hash", 
                             default="null")

    # keys in the resource to publish in base64
    stack.parse.add_optional(key="publish_keys_hash", 
                             default="null")

    # map keys b64 (dict) is use to change the key name that shows up on the UI
    stack.parse.add_optional(key="map_keys_hash", 
                             default="null")

    # prefix is prefix for each key
    stack.parse.add_optional(key="prefix_key", 
                             default="null")

    # Initialize Variables in stack
    stack.init_variables()

    match = {"resource_type": stack.resource_type}

    if stack.get_attr("name"):
        match["name"] = stack.name

    if stack.get_attr("ref_schedule_id"):
        match["schedule_id"] = stack.ref_schedule_id

    if stack.get_attr("labels_hash"):

        # testtest456
        stack.logger.debug("r1"*32)
        stack.logger.debug("r1"*32)

        for _key, value in stack.b64_decode(stack.labels_hash).items():
            key = "label-{}".format(_key)
            match[key] = value

    match["must_be_one"] = True
    resource_info = list(stack.get_resource(**match))

    data = None

    if isinstance(resource_info, list):
        data = resource_info[0]
    elif isinstance(resource_info, dict):
        data = resource_info

    if not data:
        raise Exception("resource not found for match {}".format(match))

    if stack.get_attr("publish_keys_hash"):

        # testtest456
        stack.logger.debug("s1"*32)
        stack.logger.debug("s1"*32)

        resource = stack.keys_to_dict(stack.b64_decode(stack.publish_keys_hash),
                                      {}, 
                                      data)
    else:

        resource = data

    # testtest456
    stack.logger.debug("a1"*32)
    stack.logger.debug("a1"*32)

    if not resource:
        stack.logger.warn("resource to publish is empty")
        return stack.get_results()

    stack.logger.debug("a2"*32)
    stack.logger.debug("a2"*32)

    copied_dict = copy.deepcopy(resource)

    if stack.get_attr("map_keys_hash"):

        # testtest456
        stack.logger.debug("t1"*32)
        stack.logger.debug("t1"*32)

        resource = stack.keys_to_dict(stack.b64_decode(stack.publish_keys_hash,
                                      {}, 
                                      data))
    else:

        resource = data

    # testtest456
    stack.logger.debug("a1"*32)
    stack.logger.debug("a1"*32)

    if not resource:
        stack.logger.warn("resource to publish is empty")
        return stack.get_results()

    stack.logger.debug("a2"*32)
    stack.logger.debug("a2"*32)

    copied_dict = copy.deepcopy(resource)

    if stack.get_attr("map_keys_hash"):
        # testtest456
        stack.logger.debug("u1"*32)
        stack.logger.debug("u1"*32)

        for _key, _map_key in stack.b64_decode(stack.map_keys_hash).items():

            stack.logger.debug("b"*32)
            stack.logger.debug(_key,_map_key)
            stack.logger.debug("b"*32)

            if _key not in resource:
                continue

            resource[_map_key] = copied_dict[_key]
            del resource[_key]

    stack.logger.debug("a3"*32)
    stack.logger.debug("a3"*32)

    if stack.get_attr("prefix_key"):

        for _key,_value in copied_dict.items():

            stack.logger.debug("b"*32)
            stack.logger.debug(_key,_map_key)
            stack.logger.debug("b"*32)

            if _key not in resource:
                continue

            resource[_map_key] = copied_dict[_key]
            del resource[_key]

    stack.logger.debug("a3"*32)
    stack.logger.debug("a3"*32)

    if stack.get_attr("prefix_key"):

        for _key,_value in copied_dict.items():

            stack.logger.debug("c"*32)
            stack.logger.debug(_key,_value)
            stack.logger.debug("c"*32)

            resource["{}/{}".format(stack.prefix_key, _key)] = _value
            del resource[_key]

    stack.logger.debug("a4"*32)
    stack.logger.debug("a4"*32)

    stack.publish(resource)

    return stack.get_results()
