from arena import *
from object_import import ARENAObjectImport
import argparse
import os
import yaml
import re
import json
import collections  # From Python standard library.
import bson

DFT_CONFIG_FILENAME='./config.yaml'
DFT_HOST='arenaxr.org'
DFT_PORT=8883
DFT_REALM='realm'

def obj_check_attr(obj, attr, dict):
    """
    Return True/False if attr (namespace/scene) is to be included in import/export
    obj: Namespace or Scene object
    attr: Which attribute to check ('namespace' or 'scene')
    dict: Dictionary of namespace or scene from config
    """
    if obj[attr] in dict:
        return True
    if not 'regex' in dict: return False
    if not obj[attr]: return False
    regex = dict['regex'].get('value', '')
    skip = dict['regex'].get('skip', False)
    match = bool(re.search(regex, obj[attr]))
    return match and not skip

if __name__ == '__main__':
    global config

    parser = argparse.ArgumentParser()
    parser.add_argument('action', action='store', type=str,
            help="The action to perform: import/export.")
    parser.add_argument('-c', '--conf', dest='configfile', default=DFT_CONFIG_FILENAME, action='store', type=str,
            nargs='+', help=f'The configuration file. Default is {DFT_CONFIG_FILENAME}')
    parser.add_argument('-d','--dry-run', dest='dryrun', action='store_true')
    parser.add_argument('-n','--no-dry-run', dest='dryrun', action='store_false')
    parser.set_defaults(dryrun=None)
    parser.add_argument('-o', '--host', dest='host', action='store', type=str,
            help=f'The arena host.')
    parser.add_argument('-p', '--mqtt-port', dest='mqtt_port', action='store', type=str,
            help=f'The arena mqtt host port.')
    parser.add_argument('-r', '--realm', dest='realm', action='store', type=str,
            help=f'The arena realm.')
    args = parser.parse_args()

    fn = args.configfile
    if isinstance(args.configfile, list):
        fn = args.configfile[0]

    # load config
    with open(fn) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    # copy args to config (commandline will override config file)
    for arg in dir(args):
        if not arg.startswith('__') and not arg.startswith('_'):
            val = getattr(args, arg)
            if not val == None:
                config[arg] = val

    # export not implemented yet
    if config['action'] == 'export':
        print('Export is not implemented yet')
        exit(1)

    obj_importer = ARENAObjectImport(realm=config.get('realm', DFT_REALM), mqtt_host=config.get('host', DFT_HOST), mqtt_port=config.get('mqtt_port', DFT_PORT));

    # load objects from .json or .bson
    import_file = config.get('import_objects_filename', '')
    if import_file.endswith('.json'):
        with open(f'./{import_file}') as f:
            arena_objects = json.load(f)
    elif import_file.endswith('.bson'):
        bs = open(f'./{import_file}', 'rb').read()
        arena_objects = []
        for obj in bson.decode_all( bs ):
            arena_objects.append(obj)
    else:
        print('Import objects filename (import_objects_filename) must be .json or .bson')
        exit(1)

    ns_config_dict = config.get('namespaces', { 'regex' : { 'value': '.*' } }) # dict of namespaces to import

    namespaces = {}
    scenes = {}

    dryrun = config.get('dryrun', True)
    persist = config.get('persist', True)
    for obj in arena_objects:
        if obj_check_attr(obj, 'namespace', ns_config_dict):
            scenes_config_dict = config['namespaces'].get(obj['namespace'], { 'regex' : { 'value': '.*' } })

            if 'to' in scenes_config_dict:
                ns = scenes_config_dict['to'].get('namespace', obj['namespace'])
                obj['namespace'] = ns

            if obj_check_attr(obj, 'sceneId', scenes_config_dict):
                scene_config = scenes_config_dict.get(obj['sceneId'], { obj['sceneId']: {} })
                if not scene_config:
                    scene_config = {}
                toscene = obj['sceneId']

                # check if we want to change scene name/namepace
                if 'to' in scene_config:
                    scene = scene_config['to'].get('scene', obj['sceneId'])
                    obj['sceneId'] = scene
                    ns = scene_config['to'].get('namespace', obj['namespace'])
                    obj['namespace'] = ns
                    if 'parent' in scene_config:
                        obj['attributes']['parent'] = scene_config['parent']

                # do some custom changes
                if 'url' in obj['attributes']:
                    if obj['attributes']['url'] == 'store/models/factory_robot_arm/scene.gltf':
                        obj['attributes']['url'] = '/store/users/wiselab/models/factory_robot_arm/scene.gltf'
                    if obj['attributes']['url'].startswith('store/'):
                        obj['attributes']['url'] = f'/{obj["attributes"]["url"]}' # add '/' at the start of gltf models in store/
                    if obj['attributes']['url'].startswith('https://arena-cdn.conix.io/store'):
                        obj['attributes']['url'] = f'{obj["attributes"]["url"].replace("https://arena-cdn.conix.io/store", "/store")}'

                    #if obj['attributes']['url'].startswith('https://arena.andrew.cmu.edu/store'):
                    #    obj['attributes']['url'] = f'{obj["attributes"]["url"].replace("https://arena.andrew.cmu.edu/store", "/store")}'

                    #   if obj['attributes']['url'].startswith('/store'):
                    #    obj['attributes']['url'] = f'https://arena-cdn.conix.io{obj["attributes"]["url"]}'

                #print('obj:', json.dumps(obj, indent=4, sort_keys=True))

                if (obj.get('type') == 'scene-options'):
                    if 'scene-options' in obj['attributes']:
                        obj['attributes']['scene-options'].pop('jitsiServer', None) # remove jitsiServer config
                try:
                    # import object
                    if not dryrun:
                        obj_importer.add(obj, persist=persist, debug=False)
                    print('.', end='')
                except Exception as error:
                    print('Error adding object:' f'{obj["namespace"]}/{obj["sceneId"]}', error)
                else:
                    # save scene info for listing
                    if obj['namespace'] in namespaces:
                        namespaces[obj['namespace']][obj['sceneId']] = namespaces[obj['namespace']].get(obj['sceneId'], 0) + 1
                    else:
                        namespaces[obj['namespace']] = { obj['sceneId']: 1 }

    print('\nDone publishing\n')
    # list namespaces/scenes
    for ns in namespaces:
        print(f'{ns}: {len(namespaces[ns])} scenes')
        scenes=namespaces[ns]
        for scene in scenes:
            host=config.get('host', DFT_HOST)
            pre = f'https://{host}/'
            print(f'\t{pre}{ns}/{scene}: {scenes[scene]} objects')
