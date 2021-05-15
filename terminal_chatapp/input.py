# Idea from:
# https://stackoverflow.com/questions/2408560/non-blocking-console-input


import threading


class NonBlockingInput(threading.Thread):
    '''A non-blocking `input()`.'''

    def __init__(
        self, 
        callback,
        input_prefix,
        daemon=True,
        thread_name='non-blocking-input-thread'
        ):
        
        self.callback = callback
        self.prefix = input_prefix
        super(NonBlockingInput, self).__init__(name=thread_name)
        
        # If true, this dies when the main thread is dead.
        self.daemon = daemon
        
        self.start()
        

    def run(self):
        while True:
            self.callback(input(self.prefix))