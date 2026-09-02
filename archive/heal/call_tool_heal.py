import schema_experiment_tracker
import schema_resource_tracker
import schema_results_tracker

import back_door_edit
import dsc_pkg_tool

trackersToAddToTool = [
    schema_term_tracker.trackerDict
]

trackersToAddToTool = [back_door_edit.getTrackerVars(initialTrackerDict=d) for d in trackersToAddToTool]

dsc_pkg_tool.main(trackersToAddToTool=trackersToAddToTool)
