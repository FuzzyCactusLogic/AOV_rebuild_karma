 # --------------------------------------------------------------
#  menu.py
#  Version: 1.0.1
#  Last Updated: Feb 14th, 2026
# --------------------------------------------------------------


#### IMPORT MODULES ####

import nuke
import AOV_rebuild_karma

#### ASSIGNING NUKE PATH ####

nukeCommonPath = '/path/to/your/.nuke'

#### ASSIGNING NUKE PATH END ####



#### PYTHON MENU ####

python_menu = nuke.menu('Nodes').addMenu("Python", icon="python_icon.png")

python_menu.addCommand('AOV_rebuild_karma', 'AOV_rebuild_karma.custom_breakout_lightgroups_and_materials(nuke.selectedNode())','')

#### PYTHON MENU END ####



#### CHANNELS MENU ADDITIONS ####

channel_menu = nuke.menu("Nodes").menu("Channel")

channel_menu.addCommand("AOV_rebuild_karma_albedo_raw", 'nuke.nodePaste(nukeCommonPath + "/tools/Channel/AOV_rebuild_karma_albedo_raw.nk")', icon="ShuffleSplitRGB.png")

#### CHANNELS MENU ADDITIONS END ####