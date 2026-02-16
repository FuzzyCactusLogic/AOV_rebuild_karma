import nuke
import re

## global Variables
LIGHTGROUP_REGEX = re.compile(r'^(?:[a-z0-9]+_)?(li?g?h?t?s?)(?:_[a-z0-9]+)*$', re.IGNORECASE)

ADDITIONAL_LIGHTING_AOVS = []

X_SPACE = 300

Y_SPACE = 100

MERGE_FROM_COLOUR = 2569876223

MERGE_PLUS_COLOUR = 2197786623

MATERIAL_AOVS = [
    'albedo', 'albedodiffuse', 'combineddiffuse', 'directdiffuse', 'indirectdiffuse', 'sss',
    'combinedglossyreflection', 'directglossyreflection', 'indirectglossyreflection', 'coat',
    'glossytransmission', 'caustics', 'refract',
    'combinedemission', 'directemission', 'indirectemission',
    'combinedvolume', 'directvolume', 'indirectvolume',
    #'shadow', 'combineddiffuseshadow', 'directdiffuseshadow', 'indirectdiffuseshadow',
    #'beautyunshadowed', 'combineddiffuseunshadowed', 'directdiffuseunshadowed', 'indirectdiffuseunshadowed',
    'ao',]

UTILITY_AOVS = ['alpha', 'depth_extra', 'P', 'P_camera', 'pRef', 'N', 'Ng', 'motionvectors', 'velocity', 'uv_extra', 'Facingratio_N', 'Facingratio_Ng', 'indirectraycount', 'primarysamples', 'cputime', 'oraclevariance',]

DEFAULT_SETTINGS = {'breakout_materials' : True,
                    'breakout_lightgroups' : True,
                    'breakout_utilities' : True,
                    'lg_regex' : LIGHTGROUP_REGEX,
                    'expected_materials' : MATERIAL_AOVS,
                    'expected_utilities' : UTILITY_AOVS,
                    'additional_lighting' : ADDITIONAL_LIGHTING_AOVS,
                    'x_space' : X_SPACE,
                    'y_space' : Y_SPACE}

## helper functions
def comma_seperated_to_list(comma_seperated_string):
    '''Converts a string to a list based on commas and removing whitespace'''
    comma_seperated_string = re.sub(' ','',comma_seperated_string)
    return comma_seperated_string.split(',')

def flatten_out_nested(nested_data):
    '''Takes a tuple of tuples or list of lists, and returns a single flattened list '''
    list_of_items = []
    for i in nested_data:
        if isinstance (i, str):
           list_of_items.append(i)
        elif isinstance (i, tuple) or isinstance (i, list):
            inner_items = flatten_out_nested(i)
            for y in inner_items:
                list_of_items.append(y)
    print (list_of_items)
    return (list_of_items)

## nodegraph helper functions
def get_centre_xypos(node):
    '''Returns a tuple with the xpos and ypos of `node` factoring the node width to obtain the node's center point.'''
    xpos = int ( node.xpos() + node.screenWidth()/2 )
    ypos = int (node.ypos()  + node.screenHeight()/2 )
    return xpos, ypos

def set_centred_xypos(node, xpos, ypos):
    '''Positions `node` at the `xpos and `ypos` position in the nodegraph,
    factoring the node width to obtain the node's center point.'''
    x_centred = int (xpos - node.screenWidth()/2)
    y_centred = int (ypos - node.screenHeight()/2)
    node.setXYpos(x_centred, y_centred)

## layer utility functions
def get_all_layers(node):
    '''returns a list of all the layers in a node '''
    channels = node.channels()
    layers = list(set([c.split('.')[0] for c in channels ]))
    layers.sort()
    #print (layers) ## for debugging
    return layers

# def shuffle_out_all_layers(node):
#     for layer in get_layers(node):
#         shuffle = nuke.nodes.Shuffle1(inputs = [node])
#         shuffle['in'].setValue(layer)
#         shuffle['label'].setValue('[value in]')
#         shuffle["note_font_color"].setValue(int(0xFFFFFFFF))
#         shuffle["note_font"].setValue("bold")

def get_lightgroup_layers(node, lightgroup_regex = LIGHTGROUP_REGEX, additional_lighting = ADDITIONAL_LIGHTING_AOVS):
    '''Return a list of all aovs in node which are lightgroups_or_materials.'''
    lightgroups_or_materials = []
    for layer in get_all_layers(node):
        result = lightgroup_regex.search(layer)
        if result:
            lightgroups_or_materials.append(layer)
        elif layer in additional_lighting:
            lightgroups_or_materials.append(layer)
    return lightgroups_or_materials

def get_materials(node, expected_materials = MATERIAL_AOVS):
    '''Returns a list of all aovs which are in the expected_materials list'''
    materials = []
    for material in expected_materials:
        for layer in get_all_layers(node):
            if layer.lower() == material.lower(): ## using this setting according to the default karma naming convention (eg. 'C_emission')
            #if layer == material:
                materials.append(layer)
    return materials

def get_utilities(node, expected_utilities = UTILITY_AOVS):
    '''Returns a list of all aovs which are in the expected_utilities list'''
    utilities = []
    for utility in expected_utilities:
        for layer in get_all_layers(node):
            if layer == utility:
                utilities.append(layer)
    return utilities

## user config functions
def setup_breakout_panel(node=None):
    '''Allows the user to customize the breakout config in the gui, and returns a dictionary, settings{} with the user defined settings'''
    p = nuke.Panel('Breakout Lightgroups_or_Materials and Materials')
    p.addSingleLineInput('Lightgroup Regex', LIGHTGROUP_REGEX.pattern)
    p.addBooleanCheckBox('Ignore case for regex?', True)
    p.addEnumerationPulldown('Breakout:', 'Materials_&_Lightgroups Materials Lightgroups Utilities')
    p.addSingleLineInput('Additional Lighting AOVS', ', '.join(ADDITIONAL_LIGHTING_AOVS))
    p.addSingleLineInput('Material AOVs', ', '.join(MATERIAL_AOVS))
    p.addSingleLineInput('Utility AOVs', ', '.join(UTILITY_AOVS))
    p.addBooleanCheckBox('breakout_utilities', True)
    # if node is not None:
    #     layers = get_all_layers(node)
    #     text = "<h3>Layers in selected node</h3>\n"
    #     text += "\n".join(layers) if layers else "No layers found."
    #     p.addNotepad("Layers", text)
    p.addSingleLineInput('x space between nodes', X_SPACE)
    p.addSingleLineInput('y space between nodes', Y_SPACE)
    p.setWidth(960)
    config_panel = p.show()

    if not config_panel:
        return None

    ## load in information from panel
    settings = DEFAULT_SETTINGS
    if p.value('Ignore case for regex?') == True:
        settings['lg_regex'] = re.compile(p.value('Lightgroup Regex'), re.IGNORECASE)
    else:
        settings['lg_regex'] = re.compile(p.value('Lightgroup Regex'))
    settings['additional_lighting'] = comma_seperated_to_list(p.value('Additional Lighting AOVS'))
    settings['expected_materials'] = comma_seperated_to_list(p.value('Material AOVs'))
    settings['expected_utilities'] = comma_seperated_to_list(p.value('Utility AOVs'))

    if p.value('Breakout:') == 'Materials_&_Lightgroups':
        settings['breakout_materials'] = True
        settings['breakout_lightgroups'] = True
        settings['breakout_utilities'] = True
    elif p.value('Breakout:') == 'Materials':
        settings['breakout_materials'] = True
        settings['breakout_lightgroups'] = False
        settings['breakout_utilities'] = True
    elif p.value('Breakout:') == 'Lightgroups':
        settings['breakout_materials'] = False
        settings['breakout_lightgroups'] = True
        settings['breakout_utilities'] = True
    elif p.value('Breakout:') == 'Utilities':
        settings['breakout_materials'] = False
        settings['breakout_lightgroups'] = False
        settings['breakout_utilities'] = True
    settings['breakout_utilities'] = p.value('breakout_utilities')
    settings['x_space'] = int(p.value('x space between nodes'))
    settings['y_space'] = int(p.value('y space between nodes'))
    return settings

def custom_shuffle_out_lightgroups(node):
    '''Obtain custom user settings from a panel and the run the breakout script'''
    settings = setup_breakout_panel()
    breakout_lightgroups(node, settings['lg_regex'],  settings['additional_lighting'], settings['x_space'], settings['y_space'])

def custom_breakout_lightgroups_and_materials(node):
    '''Obtain custom user settings from a panel and the run the breakout script'''
    ## hard stop if Unpremult or Premult
    if node.Class() in ('Unpremult', 'Premult'):
        nuke.message(
            "Selected node is a %s.\n\n"
            "Because AOV_rebuild_karma begins by unpremultiplying the RGBA channel, "
            "by appending to a %s node you may break the rebuild.\n\n"
            "Please make sure Premult / Unpremult nodes are not being used upstream."
            % (node.Class(), node.Class())
        )
        return

    ## Run the script
    settings = setup_breakout_panel()
    breakout_lightgroups_and_materials(node, settings)

    ## warning node list - Each entry is a function that returns True if the node should warn
    warning_node_rules = {
        'Dot': lambda n: True,
        'Merge2': lambda n: n.knob('operation') is not None and n['operation'].value() in ('multiply', 'divide'),
    }

    warn_class = None

    rule = warning_node_rules.get(node.Class())
    if rule and rule(node):
        warn_class = node.Class()

    if warn_class:
        nuke.message(
            "Warning: Selected node is a %s.\n\n"
            "Please be careful of upstream operations such as Unpremult\n\n"
            "so not to break your AOV rebuld."
            % warn_class
        )

    # IMPORTANT: run the post pass after building
    post_layout_adjustments()

def breakout_utilities(node, settings = DEFAULT_SETTINGS):
    '''Cycles through all the aovs classed as utilities and creates an aov shuffle of them'''
    expected_utilities = settings['expected_utilities']
    x_space = settings['x_space']
    y_space = settings['y_space']

    utilities = get_utilities(node, expected_utilities)
    if not utilities:
        return None

    bpipe_nodes = []
    x_pos, y_pos = get_centre_xypos(node)
    x_pos += x_space

    utility_dot = nuke.nodes.Dot(inputs = [node])
    #utility_dot.setName('Utility_Pipe')
    utility_dot['label'].setValue('UTILITY >')  ## for debugging layout
    utility_dot["note_font_color"].setValue(int(0xFFFFFFFF))
    utility_dot["note_font"].setValue("bold")
    utility_dot["note_font_size"].setValue(40)
    set_centred_xypos(utility_dot, x_pos, y_pos)
    bpipe_nodes.append(utility_dot)

    x_utl_dot_pos, y_utl_dot_pos = get_centre_xypos(utility_dot)

    src_channels = set(node.channels())

    available_layers = get_all_layers(node)
    available_layers_lower = {l.lower() for l in available_layers}

    # If user expects "alpha" but there's no alpha layer, synthesize from rgba.alpha
    if "alpha" in {u.lower() for u in expected_utilities} and "alpha" not in available_layers_lower:
        if "rgba.alpha" in src_channels:
            # put alpha at the front so it appears first in the utility row
            utilities = ["alpha"] + utilities

    for i, utl in enumerate(utilities):
        x_pos = x_utl_dot_pos + (x_space * (i + 1))
        utility_pipe = [bpipe_nodes[-1]]

        utl_dot = nuke.nodes.Dot(inputs=[utility_pipe[-1]])
        set_centred_xypos(utl_dot, x_pos, y_pos)

        utility_pipe.append(utl_dot)
        bpipe_nodes.append(utl_dot)

        shuffle_utl = nuke.nodes.Shuffle2(inputs=[utility_pipe[-1]], in1=utl, in2='alpha', label=utl)

        # --- alpha special-case (do NOT let generic mapping overwrite it)
        if utl.lower() == "alpha" and "alpha" not in available_layers_lower:
            shuffle_utl["in1"].setValue("rgba")
            shuffle_utl["in2"].setValue("alpha")
            shuffle_utl["label"].setValue("alpha")
            shuffle_utl["mappings"].setValue([
                ("rgba.alpha", "rgba.red"),
                ("rgba.alpha", "rgba.green"),
                ("rgba.alpha", "rgba.blue"),
                ("rgba.alpha", "rgba.alpha"),
            ])
        else:
            ## gather channels that belong to this layer
            layer_chans = [c for c in src_channels if c.startswith(utl + ".")]

            has_xyz = all(f"{utl}.{c}" in src_channels for c in ("x", "y", "z"))
            has_rgb = all(f"{utl}.{c}" in src_channels for c in ("red", "green", "blue"))
            has_alpha = f"{utl}.alpha" in src_channels

            alpha_src = f"{utl}.alpha" if has_alpha else "rgba.alpha"

            if has_xyz:
                shuffle_utl['mappings'].setValue([
                    (f"{utl}.x", "rgba.red"),
                    (f"{utl}.y", "rgba.green"),
                    (f"{utl}.z", "rgba.blue"),
                    (alpha_src, "rgba.alpha"),
                ])

            elif has_rgb:
                shuffle_utl['mappings'].setValue([
                    (f"{utl}.red", "rgba.red"),
                    (f"{utl}.green", "rgba.green"),
                    (f"{utl}.blue", "rgba.blue"),
                    (alpha_src, "rgba.alpha"),
                ])

            else:
                non_alpha = [c for c in layer_chans if not c.endswith(".alpha")]
                single_src = (non_alpha[0] if non_alpha else (layer_chans[0] if layer_chans else None))

                if single_src:
                    shuffle_utl['mappings'].setValue([
                        (single_src, "rgba.red"),
                        (single_src, "rgba.green"),
                        (single_src, "rgba.blue"),
                        (alpha_src, "rgba.alpha"),
                    ])
                else:
                    shuffle_utl['mappings'].setValue([
                        (alpha_src, "rgba.alpha"),
                    ])

        shuffle_utl["note_font_color"].setValue(int(0xFFFFFFFF))
        shuffle_utl["note_font"].setValue("bold")
        set_centred_xypos(shuffle_utl, x_pos, y_pos + 28)
        utility_pipe.append(shuffle_utl)

    return utility_dot

def plus_lightgroups_or_materials(node, mode = 0, settings = DEFAULT_SETTINGS, start_input=None):
    '''Cycles through all the aovs classed as either materials (mode 0) or lightgroups (mode 1) and creates and aov minibuild of them'''
    ## breakout settings
    expected_materials = settings['expected_materials']
    lightgroup_regex = settings['lg_regex']
    additional_lighting = settings['additional_lighting']
    x_space = settings['x_space']
    y_space = settings['y_space']

    if start_input is None:
        start_input = node

    bpipe_nodes = []
    x_pos, y_pos = get_centre_xypos(node)
    y_pos += y_space * 1.5

    no_op = nuke.nodes.NoOp(inputs = [start_input])
    no_op.setName('spacer_no_op', True)
    set_centred_xypos(no_op, x_pos, y_pos)
    bpipe_nodes.append(no_op)

    y_pos+=y_space
    start_dot = nuke.nodes.Dot(inputs = [bpipe_nodes[-1]])
    #start_dot['label'].setValue('start_dot')  ## For debugging layout
    start_dot.setName('start_dot', True)
    set_centred_xypos(start_dot, x_pos, y_pos)
    bpipe_nodes.append(start_dot)
    top_nodes =[bpipe_nodes[-1]]
    ## ensure bpipe_xpos/ypos always exist even if no AOVs are found
    bpipe_xpos, bpipe_ypos = get_centre_xypos(bpipe_nodes[-1])

    ## main breakout
    if mode == 0:
        lightgroups_or_materials =  get_materials(node, expected_materials)
        missing_materials = list(set([mat.lower() for mat in expected_materials]) - set([mat.lower() for mat in lightgroups_or_materials]))
        print([mat.lower() for mat in expected_materials])
        print([mat.lower() for mat in lightgroups_or_materials])
    elif mode == 1:
        lightgroups_or_materials = get_lightgroup_layers(node, lightgroup_regex, additional_lighting)

    ## guard + feedback to artist on missing material AOVs
    if not lightgroups_or_materials:
        sticky_label = '<h3>Missing Materials</h3>There are no materials in this stream.'
        sticky_note = nuke.nodes.StickyNote(
            label=sticky_label,
            tile_color=0x272727ff,
            note_font_color=0xa8a8a8ff,
            note_font_size=40
        )
        sticky_note.setXYpos(int(x_pos + x_space), int(y_pos))
        return bpipe_nodes

    count = 0 ## track Lightgroup numbers

    for lg in lightgroups_or_materials:
        x_pos, y_pos = get_centre_xypos(top_nodes[-1])
        x_pos += x_space

        ## aov_pipe
        aov_pipe = []
        aov_dot = nuke.nodes.Dot(inputs = [top_nodes[-1]])
        #aov_dot['label'].setValue('aov_dot')  ## for debugging layout
        aov_dot.setName('aov_dot', True)
        set_centred_xypos(aov_dot, x_pos, y_pos)
        top_nodes.append(aov_dot)
        aov_pipe.append(aov_dot)

        y_pos+=y_space
        shuffle_lg = nuke.nodes.Shuffle2(inputs = [aov_pipe[-1]], in1 = lg, in2 = 'alpha', label = lg)
        shuffle_lg['mappings'].setValue([('rgba.alpha','rgba.alpha')])
        shuffle_lg["note_font_color"].setValue(int(0xFFFFFFFF))
        shuffle_lg["note_font"].setValue("bold")
        set_centred_xypos(shuffle_lg, x_pos, y_pos)
        aov_pipe.append(shuffle_lg)

        y_pos+=y_space
        unpremult_lg = nuke.nodes.Unpremult(inputs = [aov_pipe[-1]])
        set_centred_xypos(unpremult_lg, x_pos, y_pos)
        aov_pipe.append(unpremult_lg)

        y_pos+=y_space
        bottom_aov_dot = nuke.nodes.Dot(inputs = [aov_pipe[-1]])
        #bottom_aov_dot['label'].setValue('bottom_aov_dot')  ## for debugging layout
        bottom_aov_dot.setName('bottom_aov_dot', True)
        set_centred_xypos(bottom_aov_dot, x_pos, y_pos)
        aov_pipe.append(bottom_aov_dot)

        ## bpipe
        if mode == 0:

            lg_lower = lg.lower()
            ## build a lowercase lookup once per iteration (cheap + simple)
            all_mats_lower = [m.lower() for m in lightgroups_or_materials]

            if lg_lower.startswith('combined'):

                suffix = lg_lower[len('combined'):]  ## eg. 'diffuse', 'volume', etc

                direct_name   = 'direct'   + suffix
                indirect_name = 'indirect' + suffix

                if direct_name in all_mats_lower and indirect_name in all_mats_lower:

                    sticky_label = (
                        "combined %s not added to B pipe,\n\n"
                        "direct %s and indirect %s used."
                        % (suffix, suffix, suffix)
                    )

                    sticky_note = nuke.nodes.StickyNote(
                        label=sticky_label,
                        tile_color=0x272727ff,
                        note_font_color=0xa8a8a8ff,
                        note_font_size=11
                    )

                    ## place under the combined shuffle
                    sx, sy = get_centre_xypos(shuffle_lg)
                    sticky_note.setXYpos(int(sx), int(sy + y_space * 1))
                    ## skip adding this combined AOV to the B pipe
                    continue

            # skip ao AOV in B pipe (materials rebuild only) - NO continue
            if lg_lower == "ao":
                sticky_label = (
                    "ao AOV not added to B pipe,\n\n"
                    "Please use as needed"
                )

                sticky_note = nuke.nodes.StickyNote(
                    label=sticky_label,
                    tile_color=0x272727ff,
                    note_font_color=0xa8a8a8ff,
                    note_font_size=11
                )

                sx, sy = get_centre_xypos(shuffle_lg)
                sticky_note.setXYpos(int(sx), int(sy + y_space * 1))

                # mark this iteration as "skip merge"
                skip_bpipe = True
            else:
                skip_bpipe = False

        ## skip albedo AOVs in B pipe (materials rebuild only)
        if mode == 0 and 'albedo' in lg.lower():

            ## ensure the RGB remove happens once at the start of the bpipe (same as normal flow)
            bpipe_xpos, bpipe_ypos = get_centre_xypos(bpipe_nodes[-1])

            if count == 0:
                remove_rgb = nuke.nodes.Remove(
                    operation='remove',
                    channels='rgb',
                    inputs=[bpipe_nodes[-1]],
                    label='RGB',
                    note_font_color=0xFFFFFFFF,
                    note_font='bold'
                )
                set_centred_xypos(remove_rgb, bpipe_xpos, bpipe_ypos + y_space)
                bpipe_nodes.append(remove_rgb)

                ## mark "first" as handled so we don't create remove_rgb again next iteration
                count = 1

                ## update bpipe position now that we've appended remove_rgb
                bpipe_xpos, bpipe_ypos = get_centre_xypos(bpipe_nodes[-1])

            ## reserve the same vertical space a merge_plus would take (keeps layout unchanged)
            merge_ypos = bpipe_ypos + (y_space * 3)

            albedo_spacer_dot = nuke.nodes.Dot(inputs=[bpipe_nodes[-1]])
            #albedo_spacer_dot['label'].setValue('albedo_skipped')  ## for debugging layout
            albedo_spacer_dot.setName('albedo_spacer_dot', True)
            set_centred_xypos(albedo_spacer_dot, bpipe_xpos, merge_ypos)
            bpipe_nodes.append(albedo_spacer_dot)

            ## keep the aov branch bottom aligned to the bpipe row (same as normal flow)
            y_pos = merge_ypos
            set_centred_xypos(aov_pipe[-1], x_pos, y_pos)

            ## sticky note under the albedo shuffle
            sticky_label = (
                "albedo AOV not added to B pipe,\n\n"
                "this AOV will break the basic rebuild.\n\n"
                "Please only use for cheats\n\n" 
                "or refer to the advanced rebuild for albedo rebuild."
            )
            sticky_note = nuke.nodes.StickyNote(
                label=sticky_label,
                tile_color=0x272727ff,
                note_font_color=0xa8a8a8ff,
                note_font_size=11
            )
            ## place underneath the albedo shuffle
            sx, sy = get_centre_xypos(shuffle_lg)
            sticky_note.setXYpos(int(sx - x_space * 0.5), int(sy + y_space * 1))
            ...
        elif mode == 0 and skip_bpipe:
            # AO (or any future skip case): do nothing further to bpipe
            # (no spacer dots, no remove node, no merge)
            pass
        else:
            bpipe_xpos, bpipe_ypos = get_centre_xypos(bpipe_nodes[-1])

            if count==0:
                remove_rgb = nuke.nodes.Remove(
                    operation='remove',
                    channels='rgb',
                    inputs=[bpipe_nodes[-1]],
                    label='RGB',
                    note_font_color=0xFFFFFFFF,
                    note_font='bold'
                )
                set_centred_xypos(remove_rgb, bpipe_xpos, bpipe_ypos+y_space)
                bpipe_nodes.append(remove_rgb)

            bpipe_ypos += y_space * 2

            bpipe_ypos += y_space
            merge_plus = nuke.nodes.Merge2(
                inputs=[bpipe_nodes[-1], aov_pipe[-1]],
                operation='plus',
                output='rgb',
                tile_color=MERGE_PLUS_COLOUR,
                label=lg
            )
            set_centred_xypos(merge_plus, bpipe_xpos, bpipe_ypos)
            bpipe_nodes.append(merge_plus)

            y_pos = bpipe_ypos
            set_centred_xypos(aov_pipe[-1], x_pos, y_pos)

            count += 1

    ## unassigned Pipe
    unassigned_pipe = []
    x_pos += x_space
    unassigned_aov_dot = nuke.nodes.Dot(inputs = [top_nodes[-1]])
    #unassigned_aov_dot['label'].setValue('unassigned_aov_dot')  ## for debugging layout
    unassigned_ypos = get_centre_xypos(top_nodes[-1], )[1]
    set_centred_xypos(unassigned_aov_dot, x_pos, unassigned_ypos)
    top_nodes.append(unassigned_aov_dot)
    unassigned_pipe.append(unassigned_aov_dot)

    ## feedback to artist on missing material aovs
    if mode == 0 and missing_materials != []:
        sticky_label = '<h3>Missing Materials</h3>'
        for material in missing_materials:
            sticky_label += '<i>' + material + r'</i>\n'
        sticky_note = nuke.nodes.StickyNote(label=sticky_label, tile_color=0x272727ff, note_font_color=0xa8a8a8ff, note_font_size=40)
        sticky_note.setXYpos(x_pos + x_space, unassigned_ypos)

    unassigned_ypos += y_space
    shuffle_original = nuke.nodes.Shuffle2(inputs = [unassigned_pipe[-1]], in1 = 'original', label = 'original rbg', note_font_color = 0xFFFFFFFF, note_font = 'bold')
    set_centred_xypos(shuffle_original, x_pos, unassigned_ypos)

    unassigned_pipe.append(shuffle_original)

    for lg in lightgroups_or_materials:
        unassigned_ypos += y_space
        unpremult_unassigned_pipe = nuke.nodes.Unpremult(inputs = [unassigned_pipe[-1] ], channels = lg)
        set_centred_xypos(unpremult_unassigned_pipe, x_pos, unassigned_ypos)
        unassigned_pipe.append(unpremult_unassigned_pipe)
        
        unassigned_ypos += y_space
        bpipe_ypos +=y_space * 0.5
        merge_from = nuke.nodes.Merge2(inputs = [unassigned_pipe[-1], unassigned_pipe[-1]], Achannels = lg, operation ='from', output = 'rgb', tile_color = MERGE_FROM_COLOUR, label = lg)
        set_centred_xypos(merge_from, x_pos, unassigned_ypos)
        unassigned_pipe.append(merge_from)

        y_pos += y_space * 0.5

    unassigned_bottom_dot = nuke.nodes.Dot(inputs = [unassigned_pipe[-1]])
    #unassigned_bottom_dot['label'].setValue('unassigned_bottom_dot')  ## for debugging layout
    unassigned_bottom_dot.setName('unassigned_bottom_dot', True)
    set_centred_xypos(unassigned_bottom_dot, x_pos, y_pos)
    unassigned_pipe.append(unassigned_bottom_dot)

    merge_plus = nuke.nodes.Merge2(inputs = [ bpipe_nodes[-1], unassigned_pipe[-1]], operation ='plus', output = 'rgb', tile_color = MERGE_PLUS_COLOUR, label = '<i> unassigned aov', disable = True)
    merge_plus.setName('merge_plus', True)
    set_centred_xypos(merge_plus, bpipe_xpos, bpipe_ypos)
    bpipe_nodes.append(merge_plus)

    bpipe_ypos += y_space
    end_result = nuke.nodes.Dot(inputs =[bpipe_nodes[-1]])
    #end_result['label'].setValue('end_result')  ## for debugging layout
    set_centred_xypos(end_result, bpipe_xpos, bpipe_ypos)
    bpipe_nodes.append(end_result)

    return bpipe_nodes

def breakout_lightgroups_and_materials(node, settings=DEFAULT_SETTINGS):
    '''Runs a breakout of materials and lightgroups using divide/multiply to combine both operations in a mathematically correct fashion.'''
    breakout_utilities_enabled = settings.get('breakout_utilities', False)
    utility_dot = None
    if breakout_utilities_enabled == True:
        utility_dot = breakout_utilities(node, settings)
    ## breakout settings
    print(settings)
    breakout_materials = settings['breakout_materials']
    breakout_lightgroups = settings['breakout_lightgroups']
    expected_materials = settings['expected_materials']
    expected_utilities = settings['expected_utilities']
    lightgroup_regex = settings['lg_regex']
    additional_lighting = settings['additional_lighting']
    x_space = settings['x_space']
    y_space = settings['y_space']

    ## guard : Utilities only mode
    if (not settings.get('breakout_materials', False) and
        not settings.get('breakout_lightgroups', False) and
        settings.get('breakout_utilities', False)):

        breakout_utilities(node, settings)
        return

    ## if there are no materials/lightgroups, run utilities only (if any)
    materials = get_materials(node, expected_materials)
    lightgroups = get_lightgroup_layers(node, lightgroup_regex, additional_lighting)
    utilities = get_utilities(node, expected_utilities)

    if not materials and not lightgroups and utilities:
        if settings.get('breakout_utilities', False):
            breakout_utilities(node, settings)
        return

    ## begin main bpipe
    bpipe_nodes = []
    x_pos, y_pos = get_centre_xypos(node)
    y_pos += y_space

    shuffle_original = nuke.nodes.Shuffle2(inputs=[node], label = '[value in1] > [value out1]', note_font_color = 0xFFFFFFFF, note_font = 'bold')
    nuke.Layer('original', ['original.red', 'original.green', 'original.blue', 'original.alpha'])
    shuffle_original['out1'].setValue('original')
    set_centred_xypos(shuffle_original, x_pos, y_pos)
    bpipe_nodes.append(shuffle_original)
    y_pos += y_space

    unpremult_original = nuke.nodes.Unpremult(inputs=[bpipe_nodes[-1]], )
    #unpremult_original['channels'].setValue('original')
    unpremult_original['channels'].setValue('original.red original.green original.blue')
    set_centred_xypos(unpremult_original, x_pos, y_pos)
    bpipe_nodes.append(unpremult_original)
    y_pos += y_space

    ## materials breakout
    if breakout_materials == True:
        mat_branch_dot = nuke.nodes.Dot(inputs=[bpipe_nodes[-1]], )
        #mat_branch_dot['label'].setValue('mat_branch_dot')  ## for debugging layout
        set_centred_xypos(mat_branch_dot, x_pos, y_pos)
        bpipe_nodes.append(mat_branch_dot)
        x_pos += x_space
        mat_branch_dot2 = nuke.nodes.Dot(inputs=[bpipe_nodes[-1]], )
        #mat_branch_dot2['label'].setValue('mat_branch_dot2')  ## for debugging layout
        set_centred_xypos(mat_branch_dot2, x_pos, y_pos)

        mat_pipe = plus_lightgroups_or_materials(mat_branch_dot2, 0, settings)
        x_pos = get_centre_xypos(bpipe_nodes[-1])[0]
        y_pos = get_centre_xypos(mat_pipe[-1])[1]

        mat_dot_bottom = nuke.nodes.Dot(inputs=[bpipe_nodes[-1]])
        #mat_dot_bottom['label'].setValue('mat_dot_bottom') ## for debugging layout
        set_centred_xypos(mat_dot_bottom, x_pos, y_pos)
        bpipe_nodes.append(mat_dot_bottom)

        shuffle_back_original = nuke.nodes.Shuffle2(inputs=[bpipe_nodes[-1]], in1='original', label='original rbg', note_font_color = 0xFFFFFFFF, note_font = 'bold')
        midpoint = int((get_centre_xypos(bpipe_nodes[-1])[0] + get_centre_xypos(mat_pipe[-1])[0]) / 2)
        set_centred_xypos(shuffle_back_original, midpoint, y_pos)

        y_pos += y_space
        merge_divide = nuke.nodes.Merge2(inputs=[shuffle_back_original, mat_pipe[-1]], operation='divide', output='rgb')
        set_centred_xypos(merge_divide, get_centre_xypos(mat_pipe[-1])[0], y_pos)
        mat_pipe.append(merge_divide)

        y_pos += y_space

        merge_materials = nuke.nodes.Merge2(inputs=[bpipe_nodes[-1], mat_pipe[-1]], operation='multiply', output='rgb')
        set_centred_xypos(merge_materials, x_pos, y_pos)
        bpipe_nodes.append(merge_materials)

        y_pos += y_space
        spacer_dot = nuke.nodes.Dot(inputs=[bpipe_nodes[-1]], label='spacer dot!')
        set_centred_xypos(spacer_dot, x_pos, y_pos)
        bpipe_nodes.append(spacer_dot)

    ## lightgroups breakout
    if breakout_lightgroups == True and get_lightgroup_layers(node, lightgroup_regex, additional_lighting):
        lg_branch_dot = nuke.nodes.Dot(inputs=[bpipe_nodes[-1]], )
        #lg_branch_dot['label'].setValue('lg_branch_dot')  ## for debugging layout
        set_centred_xypos(lg_branch_dot, x_pos, y_pos)
        bpipe_nodes.append(lg_branch_dot)
        x_pos += x_space
        lg_branch_dot2 = nuke.nodes.Dot(inputs=[bpipe_nodes[-1]], )
        #lg_branch_dot2['label'].setValue('lg_branch_dot2')  ## for debugging layout
        set_centred_xypos(lg_branch_dot2, x_pos, y_pos)

        lg_pipe = plus_lightgroups_or_materials(lg_branch_dot2, 1, settings)
        x_pos = get_centre_xypos(bpipe_nodes[-1])[0]
        y_pos = get_centre_xypos(lg_pipe[-1])[1]

        lg_dot_bottom = nuke.nodes.Dot(inputs=[bpipe_nodes[-1]])
        #lg_dot_bottom['label'].setValue('lg_dot_bottom')  ## for debugging layout
        set_centred_xypos(lg_dot_bottom, x_pos, y_pos)
        bpipe_nodes.append(lg_dot_bottom)

        shuffle_back_original = nuke.nodes.Shuffle2(inputs=[bpipe_nodes[-1]], in1='original', label='original rbg', note_font_color = 0xFFFFFFFF, note_font = 'bold')
        midpoint = int((get_centre_xypos(bpipe_nodes[-1])[0] + get_centre_xypos(lg_pipe[-1])[0]) / 2)
        set_centred_xypos(shuffle_back_original, midpoint, y_pos)

        y_pos += y_space
        merge_divide = nuke.nodes.Merge2(inputs=[shuffle_back_original, lg_pipe[-1]], operation='divide', output='rgb')
        set_centred_xypos(merge_divide, get_centre_xypos(lg_pipe[-1])[0], y_pos)
        lg_pipe.append(merge_divide)

        y_pos += y_space

        merge_materials = nuke.nodes.Merge2(inputs=[bpipe_nodes[-1], lg_pipe[-1]], operation='multiply', output='rgb')
        set_centred_xypos(merge_materials, x_pos, y_pos)
        bpipe_nodes.append(merge_materials)

    ## guard + feedback to artist on missing lightgroup AOVs
    elif breakout_lightgroups == True:
        sticky_label = '<h3>Missing Lightgroups</h3>There are no lightgroups in this stream (as per the regex code).'
        sticky_note = nuke.nodes.StickyNote(
            label=sticky_label,
            tile_color=0x272727ff,
            note_font_color=0xa8a8a8ff,
            note_font_size=40
        )
        sticky_note.setXYpos(int(x_pos + x_space), int(y_pos))

    y_pos += y_space

    final_premult = nuke.nodes.Premult(inputs=[bpipe_nodes[-1]])
    set_centred_xypos(final_premult, x_pos, y_pos)
    bpipe_nodes.append(final_premult)

def post_layout_adjustments(y_offset_shuffle=28, y_offset_unpremult=32, y_pad_bottom_dot=50):

    deleted_NoOps = 0

    ## move Shuffle2 nodes UP to the minimum Y of their upstream aov_dot + offset
    for sh in nuke.allNodes():
        if (
            sh.Class() == 'Shuffle2'
            or (sh.Class() == 'Remove' and sh['label'].value() == 'RGB')
        ):
            inp = sh.input(0)
            if not inp:
                continue

            if inp.Class() == 'Dot' and ('aov_dot' in inp.name() or 'start_dot' in inp.name()):
                sh_x, _ = get_centre_xypos(sh)
                _, dot_y = get_centre_xypos(inp)

                target_y = int(dot_y + y_offset_shuffle)
                set_centred_xypos(sh, sh_x, target_y)

    ## move Unpremult nodes up to the minimum Y of their upstream Shuffle2 + offset
    for up in nuke.allNodes('Unpremult'):
        inp = up.input(0)
        if not inp:
            continue

        ## only unpremults with channels value 'rgb'
        if up['channels'].value() == 'rgb' and inp.Class() == 'Shuffle2':
            up_x, _ = get_centre_xypos(up)
            _, sh_y = get_centre_xypos(inp)

            target_y = int(sh_y + y_offset_unpremult)
            set_centred_xypos(up, up_x, target_y)

    ## bottom_aov_dot: align to upstream node, then place below using upstream size
    for d in nuke.allNodes('Dot'):
        if "bottom_aov_dot" in d.name().lower() and not d.dependent():

            up = d.input(0)
            if not up:
                continue

            up_x, up_y = get_centre_xypos(up)

            # half upstream height + half dot height + padding
            offset = int((up.screenHeight() / 2) + (d.screenHeight() / 2) + y_pad_bottom_dot)

            set_centred_xypos(d, up_x, int(up_y + offset))

    ## delete albedo_spacer_dot
    for n in nuke.allNodes('Dot'):
        if 'albedo_spacer_dot' in n.name():
            nuke.delete(n)

    merge_pluses = [
        n for n in nuke.allNodes("Merge2")
        if n.name().startswith("merge_plus")
    ]

    unassigned_bottom_dot = nuke.toNode("unassigned_bottom_dot")

    if unassigned_bottom_dot:
        for m in merge_pluses:
            if unassigned_bottom_dot in m.dependencies():
                ux, _ = get_centre_xypos(unassigned_bottom_dot)
                _, my = get_centre_xypos(m)
                set_centred_xypos(unassigned_bottom_dot, ux, my)
                break

    ## delete NoOps
    for n in nuke.allNodes('NoOp'):
        if 'spacer_no_op' in n.name():
            nuke.delete(n)
            deleted_NoOps += 1

    print("post_layout_adjustments() ran:",
          "deleted_NoOps =", deleted_NoOps)
