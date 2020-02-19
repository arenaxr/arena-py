import arena,time
arena.init("oz.andrew.cmu.edu", "realm", "hello")
arena.start()
arena.Object("cube")
arena.Object("sphere",location=(1,1,-1),color=(255,0,0))
arena.Object(objType="gltf-model",
             location=(-1,1,1),
             rotation=(0,0,0,1),
             scale=(1,1,1),
             color=(255,0,255),
             persist=True,
             ttl=5,
             physical=True,
             clickable=True,
             url="models/Duck.glb");
time.sleep(30)
