import pandas as pd
import os

import cair_data_package_tool.dsc_pkg_utils as dsc_pkg_utils
import cair_data_package_tool.schema_utils as schema_utils

def version_update_tracker(getTrk,trkDict):

    # step 0: import tracker
    
    if os.path.isfile(getTrk):
        
        tracker_df = pd.read_csv(getTrk)
        tracker_df.fillna("", inplace = True)

        # if the tracker is empty, just create a new empty tracker based on the current schema
        if tracker_df.empty:
            props = dsc_pkg_utils.heal_metadata_json_schema_properties(metadataType=trkDict["trackerName"],schema=trkDict["schema"])
            updated_tracker_df = dsc_pkg_utils.empty_df_from_json_schema_properties(jsonSchemaProperties=props)
        else:
            schema = trkDict["schema"]
            schema_version_map = trkDict["schemaVersionMap"]
            updated_tracker_df = schema_utils.update_record_df_schema_version(tracker_df=tracker_df,tracker_schema=schema,tracker_schema_version_map=schema_version_map)
        
        updated_tracker_df.to_csv(getTrk, index = False)
        return True
        
    return False
        