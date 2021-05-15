import json


def create_event(type, **kwargs):
    '''
    Creates an event type and returns it decoded as JSON.
    '''
    return json.dumps({'type': type, **kwargs})


def is_valid_event(event):
    '''
    Returns True if event is a valid event
    otherwise False.
    '''
    if not isinstance(event, dict):
        return False
    if not 'type' in event:
        return False
    if not event['type']:
        return False
    return True


def message_event(_from, message):
    event = {'from': _from, 'message': message}
    return create_event('message', **event)


def users_event(users_length):
    return create_event('users', users=users_length)