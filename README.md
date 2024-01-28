# 23-043-Tab-Slot

Add-in for Fusion 360 CAD to automate the modelling of tab and slot features. Intended for laser cut or similar assemblies where all pieces are of the same thicknesses.

## Installing and Getting Started
1. Start by downloading the 23-043-Tab-Slot repository as a zip 
<img width="1255" alt="TAS_tutorial_zip" src="https://github.com/CC-IS/23-043-Tab-Slot/assets/122337539/fe0509d3-7896-475d-9e57-bc1120a511f3">

2. Unzip the dowloadeded file and rename the folder to "Tab and Slot" 

3. Follow the autodesk [instructions](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-install-an-ADD-IN-and-Script-in-Fusion-360.html) to manually install an add-in and run it

4. When using using the add-in in a design, create a user parameter named "mt" specifying the thickness of the solids that the tab and slot features will be added to. If you try to use the add-in without this present you will get an error message. 
<img width="1200" alt="TAS_tutorial_user_param" src="https://github.com/CC-IS/23-043-Tab-Slot/assets/122337539/afd0ba7e-d86a-4351-964c-c79bf1ee921b">

## Creating Tab and Slot Features
A use case of this add-in is creating a laser cut box. Let's say we have already modelled a box like the image below:
<img width="1440" alt="TAS_tutorial_box" src="https://github.com/CC-IS/23-043-Tab-Slot/assets/122337539/5b3b2b77-7cc7-49d5-8c85-8170db879abb">

The Tab and Slot command is located in the solid create panel
<img width="1440" alt="TAS_tutorial_select" src="https://github.com/CC-IS/23-043-Tab-Slot/assets/122337539/0b5f7075-3d27-442a-b5d7-9ebc98a30d58">

Selecting the command opens up a dialog. The "Tab Edge" field allow you to select edges that you would like to add tabs to. The edges must be in the same plane and belong to the same body. Leaving "Auto Tab" checked lets the add-in decide how wide the tabs should be and how many should be added.
<img width="1440" alt="TAS_tutorial_first" src="https://github.com/CC-IS/23-043-Tab-Slot/assets/122337539/d529611f-8996-4607-bfa3-c0318a50dfab">

The box after running the tab and slot command a few times with auto tab enabled
<img width="1440" alt="TAS_tutorial_second" src="https://github.com/CC-IS/23-043-Tab-Slot/assets/122337539/0af09754-c063-4592-ac48-5b660e721f12">

Unchecking autotab allows for the tab width and minimum tab spacing to be adjusted
<img width="1440" alt="TAS_tutorial_third" src="https://github.com/CC-IS/23-043-Tab-Slot/assets/122337539/33a12843-3157-4661-a23e-298517830b42">

<img width="1440" alt="TAS_tutorial_explode" src="https://github.com/CC-IS/23-043-Tab-Slot/assets/122337539/b4114c7c-958a-4c28-891a-dc73c4893c62">
