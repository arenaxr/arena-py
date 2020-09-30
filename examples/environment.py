import arena
arena.init("arena.andrew.cmu.edu", "realm", "example")
arena.Object(objName="env", scale=(0.25, 0.25, 0.25),
             data='{"environment":{"ground":"flat"}}')
arena.handle_events()
