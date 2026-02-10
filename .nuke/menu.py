 # --------------------------------------------------------------
#  menu.py
#  Version: 1.0.0
#  Last Updated: Feb 10th, 2026
# --------------------------------------------------------------


#### IMPORT MODULES ####

import nuke
import AOV_rebuild_karma_basic

#### ASSIGNING NUKE PATH ####

nukeCommonPath = '/path/to/your/.nuke'

#### ASSIGNING NUKE PATH END ####



#### PYTHON MENU ####

python_menu = nuke.menu('Nodes').addMenu("Python", icon="python_icon.png")

python_menu.addCommand('AOV_rebuild_karma_basic', 'AOV_rebuild_karma_basic.custom_breakout_lightgroups_and_materials(nuke.selectedNode())','')

#### PYTHON MENU END ####
