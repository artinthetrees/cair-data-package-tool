# CAIR Data Package Tool
Desktop software tool that provides a user-friendly interface to operationalize data packaging compliant with [CAIR Data Package Framework Specifications](https://norc-heal.github.io/heal-data-pkg-guide/).

The CAIR Data Package Framework and Tool has its roots in the HEAL Data Package Framework and Tool. The HEAL Data Package Framework and Tool were developed between 2022-2024 by the [HEAL Data Sharing Consultancy team at NORC at the University of Chicago](https://www.norc.org/research/projects/helping-to-end-addiction-long-term-heal-data-support.html) as part of a larger body of data sharing strategy work to support data sharing requirements for the [National Institutes of Health Helping to End Addiction Long-term (HEAL)](https://www.nih.gov/heal) Initiative. This foundational work was funded by the NIH HEAL Initiative.  

# Helpful Documentation
>[!WARNING]
>The CAIR Data Package Framework and Tool are currently in a transition as we fork form the foundational HEAL Data Package Framework and Tool to make the CAIR Data Package Framework and Tool more fully generalizable, and further develop its functionality and integrations with state of the art data sharing and data re-use standards and tools. During this transition, we will continue to point to documentation for the HEAL Data Package Framework and Tool, which should still largely apply. We will work to develop documentation specific to CAIR Data Package Framework and Tool as soon as possible. 

- **CAIR Data Package Tool** [Documentation](https://norc-heal.github.io/heal-data-pkg-tool-docs/)
- **CAIR Data Package Framework** [Specifications and Guide](https://norc-heal.github.io/heal-data-pkg-guide/)
         
# Download and Open Tool (Windows executable)
- Go to the download [link](https://github.com/artinthetrees/cair-data-package-tool/releases/latest/) for the latest release of the tool
- Expand "Assets"
- Download the asset: cair-data-pkg-tool-windows.zip
- Unzip archive
- The result will be a directory called cair-pkg-tool-windows with a single file called call_tool_cair.exe inside. Double click this executable file to open tool.  
- **NOTE**:
    - **Delete previous version(s) of the tool**: If you have downloaded a previous version of the tool, delete the previous version of the tool (cair-pkg-tool-windows\call_tool_cair.exe – delete the whole cair-pkg-tool-windows folder) prior to downloading and unzipping the current version of the tool, as having more than one version of the tool in the same file location may lead to problems with duplicate file names.
    - **DO NOT delete your dsc-pkg folder or contents**: If you have already used the tool to create/initialize your data package (i.e. created your dsc-pkg folder within your study folder), **DO NOT** delete your dsc-pkg folder or any of its contents (i.e. standard data package metadata files such as experiment, resource, and results trackers and data dictionaries)

# Download and Open Tool (Mac executable)
- Go to the download [link](https://github.com/artinthetrees/cair-data-package-tool/releases/latest/) for the latest release of the tool  
- Expand "Assets"
- Download the asset: cair-data-pkg-tool-mac.zip
- Unzip archive
- The result will be a directory called cair-data-pkg-tool-mac with a single file called call_tool_cair inside. Right click on the call_tool_cair file and select “Open.” <i><b>Note:</b> You will receive a pop-up window with a notification that macOS cannot verify the developer. You will need to select “Open” within this pop-up window up to override and open the app.</i>  
- **NOTE**:
    - **DO NOT delete your dsc-pkg folder or contents**: If you have already used the tool to create/initialize your data package (i.e. created your dsc-pkg folder within your study folder), **DO NOT** delete your dsc-pkg folder or any of its contents (i.e. standard data package metadata files such as experiment, resource, and results trackers and data dictionaries) 

# (Developers only) Python virtual environment for development
- clone repository
- cd into repository
- create and activate virtual environment
- install editable version of tool and its dependencies into virtual environment
    ``` pip install -e . ```







