import json


def create_event(type, **kwargs):
    '''
    Returns an event with type of given `type`. The event is JSON
    encoded.
    '''
    return json.dumps({'type': type, **kwargs})


def create_message_event(_from, message):
    '''
    Event for message of websocket clients.
    '''
    event = {'from': _from, 'message': message}
    return create_event('message', **event)


def create_users_event(users):
    '''
    Event for clients that is connected to the server.
    '''
    return create_event('users', users=users)