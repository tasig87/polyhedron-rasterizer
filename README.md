## Description

This project is a WORK IN PROGRESS showcase of a Python-based real-time 3D Rasterizer for Polyhedra. It began as an attempt at recreating an eyecatcher from the video game "The 25th Ward: The Silver Case", and pivoted into an experimental solid face rasterizer from scratch. PyGame is used solely as a display-out "drawing tool" for the time being, though the endgoal is for me to learn enough JavaScript to move the "drawing" process over to a portable HTML file.

Shown below is what the library + demo file is currently capable of.


![tscpoly_finalB](https://github.com/user-attachments/assets/e5adced0-2071-4495-855a-6aa98599ef3a)
![tscpoly_4d](https://github.com/user-attachments/assets/975f0c9e-03fe-492e-8ed8-3c0ae77b5a60)




## Documentation

In-progress documentation can be found in link below until project is finalized. It is **very informal** as it was solely intended to be a personal reference for when I write up a formal documentation, so expect gramatical errors, confusing sentences, and cringy writing. It is otherwise a very detailed report on how the project was created, explanations behind algorithms and development choices, as well as a list of issues to be addressed and future updates.

https://docs.google.com/document/d/e/2PACX-1vSz1IgYfsS2MOSI1Tw3kpf4W8gL1FDwTzphNkF9g5in9Hxdyg0w6-D8Qak9tNYzXMgjChloI5RebL94/pub



## How To Run
1. Import *main.py* (demo program) and *polyhedron.py* (library file) into a Python workspace, ideally a virtual environment.
2. If necessary, install the following relevant libraries into your workspace:
- numpy
- networkx
- pygame
3. Run the "main.py" file in Python within your workspace.



## Modifications
The files as is will show a spinning wireframe of the default "25W:TSC" Polyhedron mentioned in the documentation. Further edits will require editing the code in main.py yourself.
- To edit the polyhedron being displayed or create a new one, read documentation in polyhedron.py for assistance and edit p_original in line 131 of main.py. polyA() can be used to create the default polyhedron object, while polyB() can be used create a basic cube.
- To switch from wireframe to solid face, navigate to the bottom of main.py where the PyGame runtime loop is and comment out the "Wireframe" section, and uncomment the "Solid Face" section.
- The *green_gradient.png* is simply a cosmetic background picture that can be used for the program, if you wish to use it, uncomment the relevant line in the runtime loop. It is broken on Linux and presumably MacOS, so I no longer support it.
