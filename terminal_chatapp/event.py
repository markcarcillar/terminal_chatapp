import json

from .security import Security


def encrypted_event(type, digest_count=3, **kwargs):
    '''
    Creates an encrypted event using `create_event()` function
    for creating event and `Security` class from our own module
    for encrypting the event.
    '''
    return json.dumps({'type': type, **kwargs})


def message_event(_from, message):
    event = {'from': _from, 'message': message}
    return create_event('message', **event)


def users_event(users_length):
    return create_event('users', users=users_length)