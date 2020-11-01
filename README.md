# Panoptes3D
Demo of browser tool for viewing PANOPTES unit telemetry

### Documentation

Both the app and this document are WIP

(Goal is to make a solid outline of the code and assets so anyone can understand how to make changes/contribute to both)

(also stuff is gonna change so this is just a first pass on certain sections)

#### About

This app was written entirely in JavaScript (with some custom GLSL shaders, for the sky and stars)

It uses the open source three.js WebGL library, revision 116

All the code currently in main.js -- modularization and better organization in progress

(describe main structure of app)

##### Scene configuration

- Camera has 45 degree FOV

##### About the stars

See jupyter notebook in data folder for more info on how stars data were prepared.

Observation: star particle size seems largely tied to resolution/pixel density (dpi) of the monitor, which makes stars look blocky on low-res displays. Either need to find different way of defining star size or just makes stars look less-blocky (rounded), which may be easier for now.

##### About the unit model

##### About the sky

##### Scene design decisions

Notes about why particular decisions were made (mainly related to art direction or optimizing app performance)

###### Lights

- Trying to largely rely on dynamic ambient lighting + fog, as well as image-based lighting from an HDR image, while minimizing reliance on directional lights (sun and moon) which can be slow.
- Light from the sun should always be warm; light from the moon should be cool; ambient light is from the sky and should therefore match its average hue.
- Discard/hide lights that are below the ground plane

#### Asset creation: 3D models

3D models were created using the open source Blender 2.8

Image textures were created with Photoshop CC, Procreate 5, and Krita. Note that any image editing program is fine for creating textures.

##### Notes about 3D model creation:

- Everything should be modelled in a low-poly style; use minimal numbers of vertices, especially when rounding corners of things with bevels.
  - If you are interested in learning about the low-poly art style, which is popular in video games, you can look on Sketchfab and other 3d art sites for inspiration. Use the Model Inspector in the Sketchfab viewer to see a given model's geometry.
- It is OK for different mesh components of an object to intersect; geometry of things that don't deform doesn't need to be perfect beyond what you're able to see. (for example, see how the camera box and control box were modelled -- with 
- Exported as .gtlf with modifiers applied, +Y up, selected only
- Try to model each separate component (ie. control box, pier, keychain, flowers, trees) in their own .blend file and import asset into main mockup scene, or at least have these parts grouped appropriately in the organizer for easy selection

- Set materials to use backface culling when possible
- Avoid using multiple materials on any individual mesh; instead, separate if necessary

##### Notes about image texture creation:

- .png or .jpg export format preferred (need to do more research on whether .png significantly larger)
- Make image dimensions square, and sized to some power of 2 (ie. 512x512, 2048x2048)
- Use the smallest image size possible to help reduce file sizes
- Use your discretion to determine how high-resolution a texture needs to be (ie. flower petals and small things that won't be viewed up close will be fine with 128x128 or 256x256, but parts of the unit's mount or control box, like stickers, might require something slightly higher. Large textures like the ground plane can be high resolution.)
- Remember you can draw/create the image texture at a comfortable, high resolution and downscale it later!

#### Asset creation: environments

Design to fit within a small sphere; unit at center

Can resemble actual locations (ie. a mountaintop, the beach, a rooftop, a forest), or just be for fun (ie. the surface of the moon, or a distant exoplanet!)

##### Design considerations:

- Environment scenes are comprised of a horizon (image textures on a large cylindrical object/sphere), 3D objects to decorate the scene (ie. plants and flowers), and custom sky color scheme
  - part of the horizon should be adjustable (by sliding UV textures up and down) to allow for optional syncing with unit config file horizon limits
- Should not make the scene too crowded (too many objects may cause lag on certain devices)
  - after more experimentation/research, determine max poly count?
- May be a good idea to create minimal, 'low graphics quality'/'minified' versions of environment scenes which users can opt to view instead (for slower devices)
  - or just aim to make all scenes this lightweight
  - for the future, enabling/disabling post-processing should definitely be an option though
- The environment scene should look good even when the camera goes below the ground plane, making ground objects transparent. This happens so that the stars are unobscured and entire sky is visible.
- Still need to look into making custom HDRIs of horizon (in Photoshop?); current one is just a placeholder from HDRI Haven.

