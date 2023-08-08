import adsk.core
import adsk.fusion
import os
import traceback
from ...lib import fusion360utils as futil
from ... import config
from ...lib.fusion360utils import tas_utils as tas
app = adsk.core.Application.get()
ui = app.userInterface


# TODO *** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_tst'
CMD_NAME = 'T&S Test'
CMD_Description = 'Tests tab and slot on all edges on bodies in design '

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

# TODO *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the 
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []


# Executed when add-in is run.
def start():
    try:
        # Create a command Definition.
        cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

        # Define an event handler for the command created event. It will be called when the button is clicked.
        futil.add_handler(cmd_def.commandCreated, command_created)

        # ******** Add a button into the UI so the user can run the command. ********
        # Get the target workspace the button will be created in.
        workspace = ui.workspaces.itemById(WORKSPACE_ID)

        # Get the panel the button will be created in.
        panel = workspace.toolbarPanels.itemById(PANEL_ID)

        # Create the button command control in the UI after the specified existing command.
        control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)

        # Specify if the command is promoted to the main toolbar. 
        control.isPromoted = IS_PROMOTED
    except Exception as error:
        # ui.messageBox("command_execute Failed : " + str(error)) 
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Executed when add-in is stopped.
def stop():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()


# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')

    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs

    # TODO Define the dialog for your command by adding different inputs to the command.

    #default values for length and edge inputs
    # defaultLengthUnits = app.activeProduct.unitsManager.defaultLengthUnits
    # default_edge_dist = adsk.core.ValueInput.createByString('1/4')
    # default_tab_width = adsk.core.ValueInput.createByString('1.5')
    #value input for distance from edge of tab
    # edge_dist = inputs.addValueInput('dist_edge', 'distance from edge', defaultLengthUnits,default_edge_dist)
    #value input for width of tab
    # tab_width = inputs.addValueInput('tab_width', 'width of tab', defaultLengthUnits, default_tab_width)
     #int spinner input for number of tabs
    # tab_qty = inputs.addIntegerSpinnerCommandInput('tab_qty','number of tabs',1,20,1,1)
    
    # TODO Connect to the events that are needed by this command.
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')

    # TODO ******************************** Your code here ********************************
    try:
        # Get a reference to your command's inputs.
        # inputs = args.command.commandInputs
        # edge_dist_input: adsk.core.ValueCommandInput = inputs.itemById('dist_edge')
        # tab_width_input: adsk.core.ValueCommandInput = inputs.itemById('tab_width')
        # tab_qty_input: adsk.core.IntegerSpinnerCommandInput = inputs.itemById('tab_qty')
        
        # # Do something interesting
        # edgeDist = edge_dist_input
        # twid = tab_width_input
        
        # tas.alltest(edgeDist,twid,tab_qty_input)
        tas.testAuto()



    except Exception as error:
        # ui.messageBox("command_execute Failed : " + str(error)) 
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
    

# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Preview Event')
    #TODO change preview appearance to make it easier to see where tab and slot will go
    

    #TODO if preview is exactly the same as execute add following lines to code so that drawTab() is done only once
    # eventArgs = adsk.core.CommandEventArgs.cast(args)
    # eventArgs.isValidResult = True


# This event handler is called when the user changes anything in the command dialog
# allowing you to modify values of other inputs based on that change.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs
    futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')

    #TODO tell or stop user from going over max tab count (based on edge length, tab width, edge distance, min tab separation)
    


# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows you to verify that all of the inputs are valid and enables the OK button.
def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Validate Input Event')

    inputs = args.inputs
    
    #add validation to stop user from doing bad things    
    
    
    
        

# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []
