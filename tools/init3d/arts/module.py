"""
*TL;DR
Module class; Store information about modules
"""

import json
import uuid

from arts.artsrequests import Action, ARTSRequestMsg, FileType, Type

class Module(dict):
    """Create a module object

    The minimal arguments to create a module are name and filename (env is optional).
    These are all the arguments that can be passed and their defaults:
    mod_name, mod_filename, mod_uuid=uuid.uuid4(), parent_rt=None, mod_ft=FileType.PY, mod_args='', mod_env=''.
    Note: filetype will be inferred from filename extension (.py or .wasm).
    Note: we can create a module object to a running module (for example, to send a delete request), if we know its uuid.
    """
    type = 'module'

    def __init__(self, mod_name, mod_filename, mod_uuid=uuid.uuid4(), parent_rt=None, mod_ft=FileType.PY, mod_args='', mod_env=''):
        # determine filetype from extension
        if mod_filename.endswith('.py'):
            mod_ft = FileType.PY
        if mod_filename.endswith('.wasm'):
            mod_ft = FileType.WA

        dict.__init__(self, uuid=str(mod_uuid), name=mod_name, parent=parent_rt,
                      filename=mod_filename, filetype=mod_ft, args=mod_args, env=mod_env)

    @property
    def uuid(self):
        return self['uuid']

    @uuid.setter
    def uuid(self, mod_uuid):
        self['uuid'] = mod_uuid

    @property
    def name(self):
        return self['name']

    @name.setter
    def name(self, mod_name):
        self['name'] = mod_name

    @property
    def parent(self):
        return self['parent']

    @parent.setter
    def parent(self, parent_rt):
        self['parent'] = parent_rt

    @property
    def filename(self):
        return self['filename']

    @filename.setter
    def filename(self, fn):
        self['filename'] = fn

    @property
    def filetype(self):
        return self['filetype']

    @filetype.setter
    def filetype(self, ft):
        self['filetype'] = ft

    @property
    def args(self):
        return self['args']

    @args.setter
    def args(self, m_args):
        self['args'] = m_args

    @property
    def env(self):
        return self['env']

    @env.setter
    def env(self, m_args):
        self['env'] = m_args

    def artsReqJson(self, action):
        req_uuid = str(uuid.uuid4())
        return req_uuid, json.dumps(ARTSRequestMsg(req_uuid, action, self.type, self))
