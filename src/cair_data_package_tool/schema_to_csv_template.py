import os
import cair_data_package_tool.dsc_pkg_utils as dsc_pkg_utils


def schema_to_csv_template(trackerDictList,saveFolderPath):
    metadataTypeList = []
    schemaList = []
    outputCsvList = []
    for t_trkDict in trackerDictList:
        metadataType = t_trkDict["trackerName"]
        metadataTypeList.append(metadataType)
        if metadataType == "data-dictionary":
            schemaList.append(None)
        else:
            schemaList.append(t_trkDict["schema"])
        outputCsvName = metadataType + ".csv"
        outputCsvList.append(os.path.join(saveFolderPath,outputCsvName))

    for (metadata_type, schema, output_csv) in zip(metadataTypeList, schemaList, outputCsvList):

        input_schema_props = dsc_pkg_utils.heal_metadata_json_schema_properties(metadataType=metadata_type,schema=schema)
        input_schema_props_df = dsc_pkg_utils.empty_df_from_json_schema_properties(jsonSchemaProperties=input_schema_props)
        input_schema_props_df.to_csv(output_csv, index=False)
    
    return True

    