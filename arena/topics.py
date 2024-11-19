from string import Template
from types import SimpleNamespace

TOPIC_TYPES = SimpleNamespace(**{
    'SCENE': 's',
    'PROC': 'p',
    'DEVICE': 'd',
})

DEVICE_TOPIC_TOKENS = SimpleNamespace(**{
    'REALM': 0,
    'TYPE': 1,
    'DEVICE_NAME': 2,
    'UUID': 3,
})

TOPIC_TOKENS = SimpleNamespace(**{
    'REALM': 0,
    'TYPE': 1,
    'NAMESPACE': 2,
    'SCENENAME': 3,
    'SCENE_MSGTYPE': 4,
    'USER_CLIENT': 5,
    'UUID': 6,
    'TO_UID': 7,
})

SCENE_MSGTYPES = SimpleNamespace(**{
    'PRESENCE': 'x',
    'CHAT': 'c',
    'USER': 'u',
    'OBJECTS': 'o',
    'RENDER': 'r',
    'ENV': 'e',
    'PROGRAM': 'p',
    'DEBUG': 'd',
})

SUBSCRIBE_TOPICS = SimpleNamespace(**{
    'NETWORK':                '$NETWORK',
    'DEVICE':                 Template('${realm}/d/${nameSpace}/${deviceName}/#'),  # All client placeholder
    'PROC_REG':               Template('${realm}/proc/reg'),
    'PROC_CTL':               Template('${realm}/proc/control/${uuid}/#'),
    'PROC_DBG':               Template('${realm}/proc/debug/${uuid}'),
    'SCENE_PUBLIC':           Template('${realm}/s/${nameSpace}/${sceneName}/+/+/+'),
    'SCENE_PUBLIC_SELF':      Template('${realm}/s/${nameSpace}/${sceneName}/+/${userClient}/+'),
    'SCENE_PRIVATE':          Template('${realm}/s/${nameSpace}/${sceneName}/+/+/+/${idTag}/#'),
    'SCENE_ENV_PRIVATE':      Template('${realm}/s/${nameSpace}/${sceneName}/e/+/+/${idTag}/#'),
})

PUBLISH_TOPICS = SimpleNamespace(**{
    'NETWORK_LATENCY':        '$NETWORK/latency',
    'DEVICE':                 Template('${realm}/d/${nameSpace}/${deviceName}/${idTag}'),
    'PROC_REG':               Template('${realm}/proc/reg'),
    'PROC_CTL':               Template('${realm}/proc/control'),
    'PROC_DBG':               Template('${realm}/proc/debug/${uuid}'),
    'SCENE_PRESENCE':         Template('${realm}/s/${nameSpace}/${sceneName}/x/${userClient}/${idTag}'),
    'SCENE_PRESENCE_PRIVATE': Template('${realm}/s/${nameSpace}/${sceneName}/x/${userClient}/${idTag}/${toUid}'),
    'SCENE_CHAT':             Template('${realm}/s/${nameSpace}/${sceneName}/c/${userClient}/${idTag}'),
    'SCENE_CHAT_PRIVATE':     Template('${realm}/s/${nameSpace}/${sceneName}/c/${userClient}/${idTag}/${toUid}'),
    'SCENE_USER':             Template('${realm}/s/${nameSpace}/${sceneName}/u/${userClient}/${userObj}'),
    'SCENE_USER_PRIVATE':     Template('${realm}/s/${nameSpace}/${sceneName}/u/${userClient}/${userObj}/${toUid}'),  # Need to add face_ privs
    'SCENE_OBJECTS':          Template('${realm}/s/${nameSpace}/${sceneName}/o/${userClient}/${objectId}'),  # All client placeholder
    'SCENE_OBJECTS_PRIVATE':  Template('${realm}/s/${nameSpace}/${sceneName}/o/${userClient}/${objectId}/${toUid}'),
    'SCENE_RENDER':           Template('${realm}/s/${nameSpace}/${sceneName}/r/${userClient}/${idTag}'),
    'SCENE_RENDER_PRIVATE':   Template('${realm}/s/${nameSpace}/${sceneName}/r/${userClient}/${idTag}/-'),  # To avoid unpriv sub
    'SCENE_ENV':              Template('${realm}/s/${nameSpace}/${sceneName}/e/${userClient}/${idTag}'),
    'SCENE_ENV_PRIVATE':      Template('${realm}/s/${nameSpace}/${sceneName}/e/${userClient}/${idTag}/-'),  # To avoid unpriv sub
    'SCENE_PROGRAM':          Template('${realm}/s/${nameSpace}/${sceneName}/p/${userClient}/${idTag}'),
    'SCENE_PROGRAM_PRIVATE':  Template('${realm}/s/${nameSpace}/${sceneName}/p/${userClient}/${idTag}/${toUid}'),
    'SCENE_DEBUG':            Template('${realm}/s/${nameSpace}/${sceneName}/d/${userClient}/${idTag}/-'),  # To avoid unpriv sub
})
