import json

# Used for formatting of the human readable version
indent = "    "
indent2 = indent + indent
indent3 = indent2 + indent
indent4 = indent3 + indent


# Creates the json output file that contains a valid
# config database entry for the provided information
def dumpConfigToFile(filename, config):
    config.services = convertServiceObjects(config.services)

    with open(filename, "w") as outfile:
        outfile.write(json.dumps(config.__dict__, sort_keys=True, indent=4))


# Creates a human readable short summary of the config that was created in a text file
def createTextDescriptionOfConfig(filename, config):
    fullMDString = textConfigBreakdown(config)

    print(fullMDString)
    with open(filename, "w") as outfile:
        outfile.write(fullMDString)


# Resolves issues with serialization by forcing the service
# objects to be primitive dicts before calling .dumps
def convertServiceObjects(objects):
    for index1, service in enumerate(objects):
        objects[index1] = service.__dict__
    return objects


# Assembles the human readable string output
def textConfigBreakdown(config):
    configBreakdownString = ""
    configBreakdownString += "\nConfiguration\n\n"

    configBreakdownString += (
        indent + str(len(config.filtered_ports)) + " filtered ports were found.\n"
    )
    configBreakdownString += (
        indent + str(len(config.services)) + " open ports were found.\n\n"
    )
    configBreakdownString += indent + "Detected Services\n\n"
    for service in config.services:
        configBreakdownString += (
            indent2
            + str(service.name)
            + ": "
            + str(service.port)
            + " ("
            + service.protocol
            + ")\n"
        )
        # for obj in service.service_data:
        #     configBreakdownString += (
        #         indent4 + str(obj)
        #     )
        configBreakdownString += "\n\n"

    return configBreakdownString
