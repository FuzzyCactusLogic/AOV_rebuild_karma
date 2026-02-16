### README ###

1. Copy .nuke folder to your desired location

Linux = '/home/<your username>/.nuke'
Windows = 'C:\\Users\\<your username>\\.nuke'
Mac = '/Users/<your username>/.nuke'

Inside .nuke directory, edit menu.py 'nukeCommonPath' to match your .nuke directory. That's it!



2. AOV_rebuild_karma_albedo_raw.nk 

is a template to demonstrate AOV rebuilding with albedo in nuke. It won't work for every use case so you will need to rebuild depending on the albedo AOVs you have in your render. To work as a complete rebuild you will first need to use 

AOV_rebuild_karma 

to breakout all your AOVs, then delete out materials that you intend rebuild with albedo from this template and stitch both templates together.



3. AOV_rebuild_karma_examples_v001.nk 

has been included as a dictionary / sandbox for users to test renders and rebuild AOVs. It includes EXRs rendered using Peter Arcara's Refining_Karma_Renders.hip from the tutorial series of the same name. These files are too large to upload to GitHub, so I've left a link below for those that want to use them..

https://drive.google.com/drive/folders/17qIadU5TkyDVur3TtMvS-RFBrwJs_1Z0?usp=sharing

So far AOV_rebuild_karma_examples_v001.nk includes a key of all default and extra render vars available in Karma H21, and some (but not all) of the custom render vars shown in Refining_Karma_Renders (I'll update this through new Houdini releases). An albedo rebuild demonstrating the AOV_rebuild_karma & AOV_rebuild_karma_albedo_raw.nk stitch, and one rebuid test I made (not quite working!) although I'll build this out (with working examples) as I test through future projects. AOV_rebuild_karma_examples_v001.nk uses Stamps for instancing and layout purposes so if you're not familiar with Stamps the link is at the bottom of the list of references so you can install it for Nuke.



For any questions, issues or feedback hit me up on GitHub!



Special thanks to Daniel Miller and Tony Lyons for their work apon which this project is based.



References

https://www.fxphd.com/details/698/

https://github.com/areelillmind/BreakOutLightGroups

https://compositingmentor.com/category/cg-compositing-series/

https://www.sidefx.com/tutorials/refining-karma-renders/

https://www.sidefx.com/docs/houdini/solaris/support/lpe.html

https://www.sidefx.com/docs/houdini/news/21/karma.html#rendering-aovs

https://github.com/adrianpueyo/Stamps