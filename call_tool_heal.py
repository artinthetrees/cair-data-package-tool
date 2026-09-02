import cair_data_package_tool.schemas.schema_experiment_tracker as schema_experiment_tracker
import cair_data_package_tool.schemas.schema_resource_tracker as schema_resource_tracker
import cair_data_package_tool.schemas.schema_result_tracker as schema_result_tracker

import cair_data_package_tool.back_door_edit as back_door_edit
import dsc_pkg_tool

trackersToAddToTool = [
    schema_experiment_tracker.trackerDict,
    schema_result_tracker.trackerDict,
    schema_resource_tracker.trackerDict
]

trackersToAddToTool = [back_door_edit.getTrackerVars(initialTrackerDict=d) for d in trackersToAddToTool]
packagedForAddToToolTitle = "Packaged for HDP Framework"

dsc_pkg_tool.main(trackersToAddToTool=trackersToAddToTool,packagedForAddToToolTitle=packagedForAddToToolTitle)
