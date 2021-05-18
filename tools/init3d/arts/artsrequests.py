import json
import uuid
import requests


class Type():
    rt = 'runtime'
    mod = 'module'


class Result():
    ok = 'ok'
    err = 'error'


class Action():
    create = 'create'
    delete = 'delete'
    update = 'update'


class FileType():
    WA = 'WA'
    PY = 'PY'


class ARTSResponseMsg(dict):
    def __init__(self, r_uuid, result, details):
        dict.__init__(self, object_id=str(r_uuid), type='arts_resp',
                      data={'result': result, 'details': details})


class ARTSRequestMsg(dict):
    def __init__(self, req_uuid, action, type, robj={}):
        rdata = {'type': type}
        rdata.update(robj)
        dict.__init__(self, object_id=req_uuid, action=action,
                      type='arts_req', data=rdata)


class ARTSRESTRequest():
    def __init__(self, arts_addr):
        if (not arts_addr.endswith("/")):
            arts_addr += "/"
        if (not arts_addr.startswith("https://")):
            arts_addr = f"https://{arts_addr}"
        self.arts_addr = arts_addr

    def getRuntimes(self):
        # e.g. https://arena.andrew.cmu.edu/arts-api/v1/runtimes/
        # returns:
        # [
        #     {
        #         "type": "runtime",
        #         "uuid": "a69e075c-51e5-4555-999c-c49eb283dc1d",
        #         "name": "py-runtime",
        #         "apis": "python:python3",
        #         "max_nmodules": 100,
        #         "nmodules": 2,
        #         "ka_ts": "2020-09-14T21:13:18.896131Z",
        #         "children": [
        #             {
        #                 "type": "module",
        #                 "parent": {
        #                     "uuid": "a69e075c-51e5-4555-999c-c49eb283dc1d"
        #                 },
        #                 "name": "wiselab/arb",
        #                 "uuid": "6aafedf3-e313-4785-a456-939de8677f07",
        #                 "filename": "arb.py"
        #             },
        #             {
        #                 "type": "module",
        #                 "parent": {
        #                     "uuid": "a69e075c-51e5-4555-999c-c49eb283dc1d"
        #                 },
        #                 "name": "wiselab/robot-arm",
        #                 "uuid": "96c530d8-f6a6-4e34-a464-943ca6f90f22",
        #                 "filename": "robot-arm.py"
        #             }
        #         ]
        #     }
        # ]
        r = requests.get(self.arts_addr+'runtimes/')
        return r.json()

    def getModules(self, rt_uuid=''):
        # e.g. https://arena.andrew.cmu.edu/arts-api/v1/modules/
        # returns:
        # [
        #     {
        #         "type": "module",
        #         "uuid": "6aafedf3-e313-4785-a456-939de8677f07",
        #         "name": "wiselab/arb",
        #         "parent": {
        #             "uuid": "a69e075c-51e5-4555-999c-c49eb283dc1d"
        #         },
        #         "filename": "arb.py",
        #         "fileid": "na",
        #         "filetype": "PY",
        #         "apis": "python:python3",
        #         "args": "arb-arts -b  arena.andrew.cmu.edu",
        #         "env": "",
        #         "channels": "[]"
        #     },
        #     {
        #         "type": "module",
        #         "uuid": "96c530d8-f6a6-4e34-a464-943ca6f90f22",
        #         "name": "wiselab/robot-arm",
        #         "parent": {
        #             "uuid": "a69e075c-51e5-4555-999c-c49eb283dc1d"
        #         },
        #         "filename": "robot-arm.py",
        #         "fileid": "na",
        #         "filetype": "PY",
        #         "apis": "python:python3",
        #         "args": "",
        #         "env": "SCENE=theme6 MQTTH=arena.andrew.cmu.edu REALM=realm",
        #         "channels": "[{'path': '/ch/theme6', 'type': 'pubsub', 'mode': 'rw', 'params': {'topic': 'realm/s/theme6'}}]"
        #     }
        # ]
        if len(rt_uuid) > 0:
            r = requests.get(self.arts_addr+'modules/'+rt_uuid+'/')
        else:
            r = requests.get(self.arts_addr+'modules/')
        return r.json()
