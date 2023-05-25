from arena import *
import os
from google_drive_downloader import GoogleDriveDownloader as gdd

# setup library
scene = Scene(host="arenaxr.org", scene="test")

@scene.run_async
async def func():
    global btn_data

    def mouse_handler(scene, evt, msg):
        if evt.type == "mousedown":
            target_bd = btn_data.get(evt.object_id)
            if target_bd:
                img_obj = scene.get_persisted_obj(target_bd['img_object_id'])
                print(f'Switching to: {target_bd["img_url"]}')
                scene.update_object(img_obj, url=target_bd['img_url'])

    # add click listeners
    for btn in btn_data:
        btn_obj = scene.get_persisted_obj(btn)
        if btn_obj:
            scene.update_object(btn_obj, click_listener=True, evt_handler=mouse_handler)

# get google drive file_id; file with json config data
file_id = os.environ.get('GD_FILE_ID', '1WD7-a7onzoegXxQFtiRZPTd-ZC2Mgzyo')

fpath = f'./{file_id}.json'
if os.path.exists(fpath):
  os.remove(fpath)

# download button data file in the form:
#{
#    "<object_id_of_button>": {
#        "img_object_id": "<object_id_of_img_object_to_change>",
#        "img_url": "<url_of_the_image_to_change_on_click>"
#    },
#    "<another_object_id_of_button>": {
#        ...
gdd.download_file_from_google_drive(file_id=file_id, dest_path=fpath, unzip=False)

with open(fpath) as f:
    btn_data = json.load(f)

# start tasks
scene.run_tasks()
