import yaml
import copy
import pandas as pd
import os
import importlib
from importlib.resources import files

def createReadme(shareableDirString,shareablePkgDirStemString,flavor,byDate,sharedColString):

    readmePath = os.path.join(shareableDirString,"readme.yaml")
    
    bundleDir = os.path.abspath(os.path.dirname(__file__))
    readmeTemplatePath = os.path.join(bundleDir, "readme.yaml")

    # if there's already a readme, add to it
    # if not, start with the template readme
    
    # if os.path.isfile(readmePath):
    #     startTemplateReadmePath = readmePath
    # else:
    #     startTemplateReadmePath = readmeTemplatePath
    
    # with open(startTemplateReadmePath,"r") as file:
    #     contents = yaml.safe_load(file)

    # update to load readme.yaml from the package
    # https://python.plainenglish.io/a-pythonic-guide-to-packaging-and-accessing-data-files-at-runtime-da93e2059e28
    if os.path.isfile(readmePath):
        startTemplateReadmePath = readmePath
        with open(startTemplateReadmePath,"r") as file:
            contents = yaml.safe_load(file)
    else:
        contents_text = files("cair_data_package_tool").joinpath("readme.yaml").read_text()
        contents = yaml.safe_load(contents_text)

    pkgName = shareablePkgDirStemString

    pkgList = contents["Get-started"]["Contents"]["shareable-data-packages"]
    pkgListCopy = copy.deepcopy(pkgList)
    addPkg = copy.deepcopy(pkgListCopy[0])

    if "example-shareable-data-package-name-1" in addPkg:
        example = True
    else:
        example = False

    oldPkgName = list(addPkg.keys())
    oldPkgName = oldPkgName[0]
    addPkg[pkgName] = addPkg.pop(oldPkgName)
    addPkg[pkgName]["file-name"] = pkgName + ".zip"
    addPkg[pkgName]["access-regime"] = flavor
    if "by-date" in flavor:
        addPkg[pkgName]["by-date"] = byDate
    else: 
        addPkg[pkgName]["by-date"] = None
    addPkg[pkgName]["created"] = str(pd.Timestamp("now").normalize())
    addPkg[pkgName]["resource-tracker-flag-name"] = sharedColString

    if example:
        pkgList[0] = addPkg
    else: 
        pkgList.append(addPkg)
    
    with open(readmePath,"w") as file:
        yaml.safe_dump(contents,file,sort_keys=False)
    return












