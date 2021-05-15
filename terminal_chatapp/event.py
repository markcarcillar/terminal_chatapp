import json


def create_event(type, **kwargs):
    '''
    Creates an event type and returns it as JSON decoded.
    '''
    return json.dumps({'type': type, **kwargs})


def message_event(_from, message):
    event = {'from': _from, 'message': message}
    return create_event('message', **event)


def users_event(users_length):
    return create_event('users', users=users_length)