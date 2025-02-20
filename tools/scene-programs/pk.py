# listens to activity on a scene and kills programs when inactive
from arena import *
from scenestate import SceneState

DFT_INACTIVE_TIME_SEC = 5
DFT_SCENE_STATE_UPDATE_SEC = 60

def scene_inactive(scene):
    
    if not scene: 
        raise ValueError("Scene not set; Did you call SceneState's set_scene()?")
        return

    programs = [v for k,v in scene.all_objects.items() if hasattr(v, "type") and v.type == "program"]
    
    for prgrm in programs: 
        try:
            if prgrm.data.parent: # delete programs setup to run in a runtime
                print(f"DELETING: {prgrm.data.name} ({prgrm.object_id})")
                scene.delete_program(prgrm)
        except ValueError:
            pass
        except AttributeError:
            pass

def main(state_update_sec, inactive_time_sec):

    # call inactive_callback after detecting the scene is inactive for 
    # inactive_time_secs; program will exit afterwards (exit_on_inactive=True)
    scene_state = SceneState(
        inactive_callback=scene_inactive, 
        inactive_time_secs=inactive_time_sec, 
        exit_on_inactive=True)

    # create scene; user join/left callbacks handled by corresponding SceneState methods
    scene = Scene(..., 
        user_join_callback=lambda s, c, m : scene_state.user_joined(c), 
        user_left_callback=lambda s, c, m : scene_state.user_left(c.object_id))

    scene_state.set_scene(scene)

    # update scene state every scene_state_update_sec 
    # or inactive_time_sec / 2, if smaller; never faster than every second
    update_interval_sec = max(min(state_update_sec, inactive_time_sec / 2), 1)
    print(f"Updating scene state every {update_interval_sec} seconds")
    scene.run_forever(scene_state.update, update_interval_sec * 1000) 
    scene.run_tasks()

if __name__ == "__main__":
    """ Parse arguments; start main """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--state_update_sec", default=os.environ.get('SCENE_STATE_UPDATE_SEC', DFT_SCENE_STATE_UPDATE_SEC),
        help="Specify the scene state update interval in seconds (can also be specified using SCENE_STATE_UPDATE_SEC environment variable)")
    parser.add_argument(
        "--inactive_time_sec", default=os.environ.get('INACTIVE_TIME_SEC', DFT_INACTIVE_TIME_SEC),
        help="Specify the scene inactivity time until a scene is said to be inactive in seconds (can also be specified using INACTIVE_TIME_SEC environment variable)")
    args=parser.parse_args()

    try:
        main(**vars(args))
    except Exception as e:
        print(str(e))

