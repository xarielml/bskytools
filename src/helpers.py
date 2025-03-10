import re
from atproto import IdResolver


_AT_URI_REGEX = r'at://'
_DID_REGEX = r'did:[a-z0-9:%-]+'
_URL_REGEX = R'^(?:https?:\/\/)?(?:www\.)?(?P<domain>bsky\.app)(?:\/)'
_BSKY_URL_REGEX = _URL_REGEX + r'(?P<collection>profile|starter-pack)(?:\/)(' \
'?P<identifier>'+_DID_REGEX+r'|[a-z0-9][a-z0-9.:-]*)(?:\/)?(?P<section>' \
'lists|post|feed|[a-z0-9-_:~]+.*)?(?:\/)?(?P<rkey>[a-z0-9-_:~]+.*)?$'

_COLLECTION_MAP = {
    "app.bsky.actor.profile": "profile",
    "app.bsky.graph.list": "lists",
    "app.bsky.graph.starterpack": "starter-pack",
    "app.bsky.feed.post": "post",
    "app.bsky.feed.generator": "feed",
}
_COLLECTION_MAP_REV = {v: k for k, v in _COLLECTION_MAP.items()}


def get_did(identifier):
    did = re.search(r'^'+_DID_REGEX, identifier.lower())
    if did is None:
        return IdResolver().handle.resolve(identifier)
    else:
        return identifier


def check_if_url(link_str):
    match = re.search(_BSKY_URL_REGEX, link_str.lower())

    if match:
        return match.groupdict()
    else:
        raise ValueError("Invalid url format")


def check_if_uri(link_str):
    match = re.search(r'^'+_AT_URI_REGEX, link_str.lower())

    if match:
        identifier, collection, rkey = link_str.split('/')[2:]
        return {'identifier': identifier, 'collection': collection, 'rkey': rkey}
    else:
        raise ValueError("Invalid at:// uri format")


def get_url_parts(link_str):
    groups = check_if_url(link_str)

    groups['identifier'] = get_did(groups['identifier'])
    if groups['section'] and groups['rkey']:
        groups['collection'] = groups['section']
        groups.pop('section', None)
    elif groups['section'] and not groups['rkey']:
        groups['rkey'] = groups['section']
        groups.pop('section', None)
    else:
        groups['rkey'] = 'self'
        groups.pop('section', None)

    return groups


def get_uri_parts(link_str):
    groups = check_if_uri(link_str)
    
    groups['identifier'] = get_did(groups['identifier'])
    if groups['rkey'] == 'self':
        groups.pop('rkey', None)

    return groups


def get_persistent_url(link_str):
    groups = get_url_parts(link_str)
    url = f"https://{groups['domain']}"
    if groups.get('rkey'):
        if groups['collection'] != 'starter-pack':
            url += f"/profile/{groups['identifier']}/{groups['collection']}/{
                groups['rkey']}"
        else:
            url += f"/{groups['collection']}/{groups['identifier']}/{
                groups['rkey']}"
    else:
        url += f"/profile/{groups['identifier']}"
    return url


def get_persistent_uri(link_str):
    groups = get_uri_parts(link_str)
    uri = f"at://{groups['identifier']}/{groups['collection']}/"
    if groups.get('rkey'):
        uri += f"{groups['rkey']}"
    else:
        uri += "/self"

    return uri


def url_to_uri(link_str):
    groups = get_url_parts(link_str)
    collection = _COLLECTION_MAP_REV[groups['collection']]

    return f"at://{groups['identifier']}/{collection}/{groups['rkey']}"


def uri_to_url(link_str):
    groups = get_uri_parts(link_str)
    collection = _COLLECTION_MAP[groups['collection']]
    
    url = "https://bsky.app/"
    if collection == 'starter-pack':
        url += f"{collection}/{groups['identifier']}/{groups['rkey']}"
    else:
        url += f"profile/{groups['identifier']}"
        if groups.get('rkey'):
            url += f"/{collection}/{groups['rkey']}"
    
    return url