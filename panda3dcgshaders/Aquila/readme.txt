
While writing the shader tutorials, I was not sure how the perspective interpolation exactly works on GPUs. Because  I was unable to find and answer that was satisfying (that does not mean that somewhere in the black hole internet there is one) I started my own rasterizer. I belong to the sort of persons which prefer to read code, than reading a technical or mathematical paper that does not care about the uncountable special cases.
A second problem, I have, since I started to write my own shaders, is that I have not found any simple solution to develop a shader step by step and debug it. I like to write something to a console, write anything to a file, easily read and examine the depth buffer, everything I do normally while writing an application.

The mini project Aquila was born.

Some facts (good and bad):

- No OpenGL interface, but more than one idea is stolen from OpenGL. All default matrices and transformations are created the way like OpenGL does.
- Every buffer is a texture, every texture is a buffer. You can modify and access them whenever you like.
- The rasterizer tries to reassemble a todays GPU pipeline. Therefore there is a vertex program and a fragment program.
- All internal calculations are device independant. In a final step it is possible (but not necessary) to convert a texture into an image, and display or save this image.
- No restrictions. Use whatever texture size you like, square or not does not matter. Your vertex program and framgent can have as many uniforms, varyings and "instructions" as you like.
- You have to restrict yourself or you write a shader that never would run on a GPU.
- Speed was not a top priority.
- Linear interpolation and wrap modes for textures.
- Perspective correction (but you can disable it).
- Although it would be possible to add all swizzling possibilites like in GLSL and or Cg in C# that would add an trendemous amount of methods to all classes.
- Only floating point Textures/Buffers. HDR should be no problem.

Missing things:

- Automatic support for left handed coordinate system. OpenGL has a default right handed coordinate system. Panda3D has a left handed coordinate system.
- Add support for a geometry program.
- Add some more performance tests. I still do not know when structs are more suitable and when not (eventuall modify Vector4, Matrix4 then).
- Add Matrix3 (for normals).
- Add a possibility to discard a fragment.
- Try to remove as much short-life objects as possible (the GC should never be called ideally, at least not in a tight loop).
