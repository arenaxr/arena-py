from types import SimpleNamespace
from string import Template

TOPIC_TYPES = SimpleNamespace(**{
    'SCENE': 's',
    'PROC': 'proc',
    'DEVICE': 'd',
})

TOPIC_TOKENS = SimpleNamespace(**{
    'REALM': 0,
    'TYPE': 1,
    'NAMESPACE': 2,
    'SCENENAME': 3,
    'SCENE_MSGTYPE': 4,
    'UUID': 5,
    'TO_UID': 6,
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
    'DEVICE':                 Template('${realm}/d/${userName}/#'), # All client placeholder
    'PROC_REG':               Template('${realm}/proc/reg'),
    'PROC_CTL':               Template('${realm}/proc/control/${uuid}/#'),
    'PROC_DBG':               Template('${realm}/proc/debug/${uuid}'),
    'SCENE_PUBLIC':           Template('${realm}/s/${nameSpace}/${sceneName}/+/+'),
    'SCENE_PUBLIC_SELF':      Template('${realm}/s/${nameSpace}/${sceneName}/+/${idTag}'),
    'SCENE_PRIVATE':          Template('${realm}/s/${nameSpace}/${sceneName}/+/+/${idTag}/#'),
})

PUBLISH_TOPICS = SimpleNamespace(**{
    'NETWORK_LATENCY':        '$NETWORK/latency',
    'DEVICE':                 Template('${realm}/d/${nameSpace}/${sceneName}/${idTag}'),
    'PROC_REG':               Template('${realm}/proc/reg'),
    'PROC_CTL':               Template('${realm}/proc/control'),
    'PROC_DBG':               Template('${realm}/proc/debug/${uuid}'),
    'SCENE_PRESENCE':         Template('${realm}/s/${nameSpace}/${sceneName}/x/${idTag}'),
    'SCENE_PRESENCE_PRIVATE': Template('${realm}/s/${nameSpace}/${sceneName}/x/${idTag}/${toUid}'),
    'SCENE_CHAT':             Template('${realm}/s/${nameSpace}/${sceneName}/c/${idTag}'),
    'SCENE_CHAT_PRIVATE':     Template('${realm}/s/${nameSpace}/${sceneName}/c/${idTag}/${toUid}'),
    'SCENE_USER':             Template('${realm}/s/${nameSpace}/${sceneName}/u/${userObj}'),
    'SCENE_USER_PRIVATE':     Template('${realm}/s/${nameSpace}/${sceneName}/u/${userObj}/${toUid}'),  # Need to add face_ privs
    'SCENE_OBJECTS':          Template('${realm}/s/${nameSpace}/${sceneName}/o/${objectId}'),  # All client placeholder
    'SCENE_OBJECTS_PRIVATE':  Template('${realm}/s/${nameSpace}/${sceneName}/o/${objectId}/${toUid}'),
    'SCENE_RENDER':           Template('${realm}/s/${nameSpace}/${sceneName}/r/${idTag}'),
    'SCENE_RENDER_PRIVATE':   Template('${realm}/s/${nameSpace}/${sceneName}/r/${idTag}/-'),  # To avoid unpriv sub
    'SCENE_ENV':              Template('${realm}/s/${nameSpace}/${sceneName}/e/${idTag}'),
    'SCENE_ENV_PRIVATE':      Template('${realm}/s/${nameSpace}/${sceneName}/e/${idTag}/-'),  # To avoid unpriv sub
    'SCENE_PROGRAM':          Template('${realm}/s/${nameSpace}/${sceneName}/p/${idTag}'),
    'SCENE_PROGRAM_PRIVATE':  Template('${realm}/s/${nameSpace}/${sceneName}/p/${idTag}/${toUid}'),
    'SCENE_DEBUG':            Template('${realm}/s/${nameSpace}/${sceneName}/d/${idTag}/-'),  # To avoid unpriv sub
})
