# Import/Export ARENA scenes

You can import/export ARENA scenes with:

```bash
make import
make export
```

This assumes you have [Make](https://www.gnu.org/software/make/) installed. The Makefile creates a [virtual environment that deals with installing all dependencies](https://github.com/sio/Makefile.venv), including the **arena-py library** (from pyPI; it does not use the development version in this repo).

**Export is not implemented yet**

## Arguments

The script accepts an action argument:

```
  action                The action to perform: import/export.
```
**Note**: Export is not implemented yet

And the following optional arguments:
```
  -h, --help            show this help message and exit
  -c CONFIGFILE [CONFIGFILE ...], --conf CONFIGFILE [CONFIGFILE ...]
                        The configuration file. Default is ./config.yaml
  -d, --dry-run
  -n, --no-dry-run
  -o HOST [HOST ...], --host HOST [HOST ...]
                        The arena host.
  -p MQTT_PORT [MQTT_PORT ...], --mqtt-port MQTT_PORT [MQTT_PORT ...]
                        The arena mqtt host port.
  -r REALM [REALM ...], --realm REALM [REALM ...]
                        The arena realm.
```

To pass arguments to the script, add the ARGS variable when invoking Make, e.g.:

```bash
make import ARGS='-h'
make export ARGS='--dry-run'
make import ARGS='--host=mqtt.arenaxr.org --mqtt_port=8883 --conf=myconfigfile.yaml'
```

## Config file

Most of the time, you will want to invoke the script simply with the action:

```bash
make import
make export
```

And define options in the **config file** (`./config.yaml` by default). The config file looks like this:

```yaml
dryrun: False # a dry run does not perform publish, just lists objects that would be imported (default: True; import only)
persist: True # persist flag used in published messages (default: True)
host: mqtt.arenaxr.org
mqtt_port: 8883
realm: realm

# json array with objects for import (e.g. from mongodb export; must be .json or .bson file)
import_objects_filename: arenaobjects_03_29_2021.bson

# list of namespaces and scenes to import/export
namespaces:
  regex:
    value: .* # regex for the namespaces to be included ('.*' will match any scene name; will include all scenes, if skip=False)
    skip: False # if True, treat regex as indicating that matching namespaces are skipped (default=False)

  skip-scenes-from-this-namespace: # the regex below shows how to skip all scenes in a namespace
    regex:
      value: .* # regex for the scenes to be imported for this namespace (none, if skip=True)
      skip: True # this indicates that scenes matching the regex will be **skipped**

    dont-skip-this-one: # this scene will be imported; scenes listed are always processed (even if they don't match the regex)

  rename-this-namespace: # this example shows how to rename an entire namespace in the file when importing
    regex:
      value: .* # regex for the scenes to be included (all, if skip=False)
      skip: False # do not skip matching scene ids
    to:
      namespace: new-namespace # can add destination to:namespace (to rename namespace)

  public: # namespaces listed are always processed (even if they don't match the regex)
    lobby:
    	to: # add destination scene name and/or namespace to rename/change scene/namespace
    		scene: lobby # can add destination to:scene (to rename scene)
    		namespace: public_test # can add destination to:namespace (to change namespace; will override namespace-level to: setting)
      	parent: imported_lobby_root # objects will be added as children of this object (assumes parent exists )
    fireside: # another example: import scene 'fireside' in the file to 'fireside-imported'
       to:
    		  scene: fireside-imported
```

**Note**: Command line args override config file options.

## Permissions

This tool will use the permissions of the ARENA user logged in. Can only import to namespaces/scenes the user has access to. If the user is not logged in, a login prompt (in a browser) will be presented.

To force sign out:
```
make signout
```
