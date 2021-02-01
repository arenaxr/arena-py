# Animations

Dispatching and running animation(s).

## Dispatching Animations
You can add animations to objects that will run when `run_animations` is called
```python
obj = Box()
obj.dispatch_animation(
        Animation(
            property="rotation",
            start=(0,0,0),
            end=(0,180,0),
            easing="linear",
            dur=1000
        )
    )
arena.run_animations(obj) # this will cause the animation to be run
```
You can also dispatch multiple animations
```python
obj = Box()
obj.dispatch_animation(
        [
            Animation(
                property="rotation",
                start=(0,0,0),
                end=(0,180,0),
                easing="linear",
                dur=1000
            ),
            Animation(
                property="position",
                start=(0,0,-5),
                end=(0,0,-10),
                easing="linear",
                dur=1000
            )
        ]
    )
arena.run_animations(obj) # this will cause all the dispatched animations to be run
```

## Animation vs AnimationMixer
AnimationMixer are special animations specific to a 3D model. These can be run the same way as regular animations. See [here](https://github.com/n5ro/aframe-extras/tree/master/src/loaders#animation).
```python
xr_logo.dispatch_animation(
    AnimationMixer(clip="*", loop="repeat")
)
arena.run_animations(xr_logo) # this will cause the 3D model to play its animations
```

## Permanent Animations
Sometimes you want animations to be associated with the object. You can do this by adding the animation as an attribute to the object.
```python
# this makes it such that xr_logo will ALWAYS play the animation when someone joins
# your ARENA scene, since the animation is now associated with that object:
xr_logo.update_attributes(
    animation_mixer=AnimationMixer(
            clip="*", loop="repeat"
        )
)
```
