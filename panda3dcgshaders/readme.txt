
[Basics]

Before you start reading this tutorials do the following:

You should know Python.

http://www.python.org/doc/

If should be able to write a simple math program in C/C++ or C#. Do not
underestimate this. If you start writing your own shaders without any prior
knowledge about a C like language, it is as hard as if you start writing a
Panda3D application without knowing anything about Python. If you do not know
anything about C it has at least three advantages to learn it first. Python
extensions are often written in C. You learn a programming language where you
have to explicitly declare the types of variables. With C you get a tool to
rewrite your time critical Python snippets.

http://en.wikibooks.org/wiki/C_Programming
http://en.wikibooks.org/wiki/C_Sharp_Programming

Read the Panda3D Hello World sample.

http://www.panda3d.net/wiki/index.php/A_Panda_%22Hello_World%22_using_Python

Try to fully understand "Solar-System" example from the Panda3D distribution.

...\samples\Solar-System\

Try to understand how the "Scene Graph" of Panda3D works.

http://www.panda3d.net/wiki/index.php/The_Scene_Graph

It helps you understand the concept of the Depth Buffer, and why you need it at
all. If you at anytime like to do shadow mapping, you need to understand very
well, how the depth buffer works.

http://www.panda3d.net/wiki/index.php/Depth_Test_and_Depth_Write

Read the first chapter from NVIDIAs Cg Tutorial. You do not have to understand
it fully, but at least you know who invented Cg, and what it is for.

http://http.developer.nvidia.com/CgTutorial/cg_tutorial_chapter01.html

Remember the NVIDIA and ATI sites forever, they have tons of usefull stuff about
shaders in general.

http://developer.amd.com
http://developer.nvidia.com

Always have the following page handy:

http://www.panda3d.org/wiki/index.php/List_of_Possible_Shader_Inputs

[Tutorials]

All samples have no fancy input handling mechanisms they are only here to play
with. There is a DIRTY tag on every section you should get dirty with and modify
the source yourself.

0.py

A sample without any shader. Just a point to start with. Each example extends
and/or modifies it predecessors.

1.py

The simplest possible shader. It is so simple that it is useless.

2.py

The simplest possible usefull shader.

3.py

Apply the colors to your models that are defined in the models egg file.

4.py

Apply colors to your objects only with the help of the vertex shader and the
fragment shader. Pass your own information from the vertex shader to the
fragment shader.

5.py

Feed your shader with input from Panda3D. Modify the colors according to this
input.

6.py

Apply one texture to your models. Do not care anymore about the colors.

7.py

Apply two textures to your models.

8.py

Per vertex diffuse lighting with one Point light, without shaders. Explain
details about diffuse lighting.

9.py

Per vertex diffuse lighting with one point light, with shaders. The concept of
spaces is introduced here.

10.py

Per pixel lighting with one point light. Normalization problems that may arise
are explained here.

11.py

Per pixel lighting with multiple point lights and attenuation.
