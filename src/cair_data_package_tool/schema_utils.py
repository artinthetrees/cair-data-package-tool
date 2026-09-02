import jsonschema

def replaceStringsInList(myList,stringMapDictionary,removeNone=True):
    if myList: # if value is not none and not empty list, try to replace values, otherwise just return original value
        myList = [stringMapDictionary.get(i,i) for i in myList]
        if removeNone:
            myList = [x for x in myList if x is not None] # check for None values and remove them 
        
    return myList

def renameDictKeys(myDictionary,keyRenameDictionary):
    if myDictionary: # if value is not none and not empty dictionary, try to rename keys, otherwise just return original value
        for k, v in list(myDictionary.items()):
            myDictionary[keyRenameDictionary.get(k, k)] = myDictionary.pop(k)

    return myDictionary

def renameDictKeysListofDicts(myListOfDicts,keyRenameDictionary):
    if myListOfDicts: # if value is not none and not empty list, try to rename keys in each dictionary item of the list, otherwise just return original value
        myListOfDicts = [renameDictKeys(d) for d in myListOfDicts]
    
    return myListOfDicts

def update_record_df_schema_version(tracker_df,tracker_schema,tracker_schema_version_map):

    # before running this fx, use the utility fxs above to: 
    # get the schema and schema version map, and 
    # check that the schema version map is up to date and can be used to map a record created under an earlier schema version to the latest schema version

    collectAllFormerNames = []
    collectAllCurrentNamesOrdered = [] # collect a list of current (non-deprecated) property names so that you can re-order based on the 'correct' order at the end of the update
    
    # step 1: for each schema property, delete deprecated fields, copy/rename undeprecated fields with former names, add new fields  
    
    print("working on step 1: updating field names")
    
    for key in tracker_schema_version_map["properties"]:

        # if the property has former names, add them to a list that will collect all former field names 
        # across all properties for deletion all at once after looping through each property
        if tracker_schema_version_map["properties"][key]["formerNames"]:
            collectAllFormerNames.extend(tracker_schema_version_map["properties"][key]["formerNames"])

        # if deprecated is true
        #   delete any field with current or former field name(s) 
        if tracker_schema_version_map["properties"][key]["deprecated"]:
            deleteFieldNames = [key]
            if tracker_schema_version_map["properties"][key]["formerNames"]:
                deleteFieldNames.extend(tracker_schema_version_map["properties"][key]["formerNames"])
            tracker_df.drop(columns=deleteFieldNames, inplace=True, errors="ignore")

        # if deprecated is false
        else:
            # collect a list of current (non-deprecated) property names so that you can re-order based on the 'correct' order at the end of the update
            collectAllCurrentNamesOrdered.append(key) 
            
            # if field with current field name exists
            if key in tracker_df.columns: 
                
                # leave field with current field name alone
                # delete any field with a former field name
                if tracker_schema_version_map["properties"][key]["formerNames"]:
                    deleteFieldNames = tracker_schema_version_map["properties"][key]["formerNames"]
                    tracker_df.drop(columns=deleteFieldNames, inplace=True, errors="ignore")    
            
            # if field with current field name does not exist
            else:
                
                i=0 

                # if former field name(s) and find a key with former field name, then copy the value from the key with former field name to key with current/new field name
                if tracker_schema_version_map["properties"][key]["formerNames"]:

                    # if field with former field name exists
                        # copy field with former field name and rename to current field name
                        # (if more than one field with a former field name exists, error out with informative message)
                    formerFieldNames = tracker_schema_version_map["properties"][key]["formerNames"]
                    
                    for f in formerFieldNames:
                        
                        if f in tracker_df.columns:
                        
                            i+=1
                            if i>1:
                                print("there is more than one field with a former name for the field currently named: ",key)
                                return False
                            tracker_df[key] = tracker_df[f]
                    
                # if field with former field name does not exist OR no former field names to check
                    # create new field with current field name; fill with appropriate empty value
                if i==0:
                    tracker_df[key] = None

    # while looping through properties, if there were undeprecated fields still using a former field name,
    # that field was copied into a new field with the updated field name (instead of straight re-naming);
    # this is done in case an old field is parsed out into two new fields for which you might still want to 
    # copy the old values and map to new values for each new field (for example, this happened with the split from 
    # category sub results to category single result and category multi result)
    # HOWEVER, this approach means that following the loop through of properties, you have to go ahead and 
    # delete all fields with a former field name that remain in the df
    if collectAllFormerNames:
        tracker_df.drop(columns=collectAllFormerNames, inplace=True, errors="ignore") 

    # step 2: update enums
    
    print("working on step 2: updating enums")
    
    # for each (non-deprecated) schema property:
    for key in tracker_schema_version_map["properties"]:

        if not tracker_schema_version_map["properties"][key]["deprecated"]:

            
            # if either deleteEnums or mapEnums is not empty
            if ((bool(tracker_schema_version_map["properties"][key]["mapEnum"])) or (bool(tracker_schema_version_map["properties"][key]["deleteEnum"]))):
                
                # get type of schema property
                # all non-deprecated properties should have an entry in the schema and therefore should have a type defined
                propertyType = tracker_schema["properties"][key]["type"]
                
                # if deleteEnums is not empty
                if tracker_schema_version_map["properties"][key]["deleteEnum"]:
                    
                    deleteDict = dict.fromkeys(tracker_schema_version_map["properties"][key]["deleteEnum"],None)
                    print("key: ", key, "deleteDict: ", deleteDict)

                    if propertyType == "string": # each value in this column of the df is a string
                        # if string value is equal to any of the values from delete list, replace string with empty string
                        tracker_df[key] = tracker_df[key].replace(deleteDict)
                        
                    elif propertyType == "array": # each value in this column of the df is an array of strings
                  
                        tracker_df[key] = [replaceStringsInList(x,deleteDict) for x in tracker_df[key]]
                        
                    else:
                        print(key, " is not a string or array of strings - I don't know how to delete enums for any other property types yet!")
                        return False
                else:
                    print(key, " has no enum deletions to review")

                if tracker_schema_version_map["properties"][key]["mapEnum"]: 

                    mapDict = {}
                    for mapKey in tracker_schema_version_map["properties"][key]["mapEnum"]:
                        mapDict.update(dict.fromkeys(tracker_schema_version_map["properties"][key]["mapEnum"][mapKey],mapKey))
                    
                    print("key: ",key,"; mapDict: ", mapDict)

                    if propertyType == "string": # each value in this column of the df is a string
                        # check if string is equal to any of the former values that have a mapping, if so, replace with mapping
                        tracker_df[key] = tracker_df[key].replace(mapDict)
                        
                    elif propertyType == "array": # each value in this column of the df is an array of strings
                        
                        # check list/array for any former values that have a mapping, if so, replace with mapping
                        tracker_df[key] = [replaceStringsInList(x,mapDict) for x in tracker_df[key]]

                    else:
                        print(key, " is not a string or array of strings - I don't know how to map enums for any other property types yet!")
                        return False
                else:
                    print(key, " has no enum mappings to review")

            else:
                print(key, "has no enum deletions or mappings") 

        else:
            print(key, " is deprecated, no deletions or mapping of enums necessary")    
                
            
    # step 3: update subfield names
    
    print("working on step 3: updating subfield names")
    
    # for each (non-deprecated) schema property:
    for key in tracker_schema_version_map["properties"]:

        if not tracker_schema_version_map["properties"][key]["deprecated"]:

            # if formerSubNames is not empty
            if tracker_schema_version_map["properties"][key]["formerSubNames"]:

                # in original dict of formerSubNames key is the current value and value is a list of all past value(s)
                # this inverts it, making each of the former values a key and the current value the value for each past value key
                subNameDict = {}
                for subNameKey in tracker_schema_version_map["properties"][key]["formerSubNames"]:
                    subNameDict.update(dict.fromkeys(tracker_schema_version_map["properties"][key]["formerSubNames"][subNameKey],subNameKey))
                
                print("key: ",key,"; subNameDict: ", subNameDict)

                # if value is a dictionary
                if propertyType == "object": # each value in this column of the df is a dictionary
                    
                    tracker_df[key] = [renameDictKeys(x,subNameDict) for x in tracker_df[key]]

                # if value is a list of dictionaries                     
                elif propertyType == "array": # each value in this column of the df is an array of dictionaries
                    tracker_df[key] = [renameDictKeysListofDicts(x,subNameDict) for x in tracker_df[key]]
                else:
                    print(key, " is not a dictionary object or an arrary of dictionary objects - I don't know how to map former sub field names for any other property types yet!")
                    return False

    print("adding updated schema version")
    if "schemaVersion" in tracker_df.columns: # it should be at this point, since it should have been added if not already present
        tracker_df["schemaVersion"] = tracker_schema_version_map["latestVersion"]
    else:
        print("has the name of the schema version property changed from schemaVersion? if so update the script to the new name to add the updated schema version")
        return False

    print("reordering to correct order")
    print("current tracker df column order: ",tracker_df.columns)
    print("desired tracker df column order: ",collectAllCurrentNamesOrdered)
    tracker_df = tracker_df[collectAllCurrentNamesOrdered]
    print("done updating")  
    return tracker_df

def validate_against_jsonschema(json_object,schema):
    Validator = jsonschema.validators.validator_for(schema)
    validator = Validator(schema)
    report = []
    is_valid = True
    for error in validator.iter_errors(json_object):
        is_valid = False
        error_report = {
            "json_path":error.json_path,
            "message":error.message,
            "absolute_path":list(error.path),
            "relative_path":list(error.relative_path),
            "validator":error.validator,
            "validator_value":error.validator_value
        }
        report.append(error_report)
    return {"valid":is_valid,"errors":report}