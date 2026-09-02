import jsonschema2md
import sys
import os

import cair_data_package_tool.dsc_pkg_utils as dsc_pkg_utils


def schema_to_md(trackerDictList,saveFolderPath):
    metadataTypeList = []
    schemaList = []
    outputMdList = []
    for t_trkDict in trackerDictList:
        metadataType = t_trkDict["trackerName"]
        metadataTypeList.append(metadataType)
        if metadataType == "data-dictionary":
            schemaList.append(None)
        else:
            schemaList.append(t_trkDict["schema"])
        outputMdName = metadataType + ".md"
        outputMdList.append(os.path.join(saveFolderPath,outputMdName))

    for (metadata_type, schema, output_md) in zip(metadataTypeList, schemaList, outputMdList):

        input_schema = dsc_pkg_utils.heal_metadata_json_schema(metadataType=metadata_type,schema=schema)

        parser = jsonschema2md.Parser(
            examples_as_yaml=False,
            show_examples="all",
        )

        md_lines = parser.parse_schema(input_schema)
        md_lines[0] = md_lines[0].strip() + ": v" + input_schema["version"] + "\n\n"

        original_stdout = sys.stdout # save ref to original stdout of print

        with open(output_md,"w") as f:
            sys.stdout = f # change stdout to output md file we created
            sys.stdout = original_stdout # reset stdout to original value

    return True
