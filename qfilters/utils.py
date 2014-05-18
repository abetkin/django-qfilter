# -*- coding: utf-8 -*-

class CallablesList(list):
    
    def __init__(self, *args, **kw):
        self.operation = kw.pop('operation', lambda x,y: None)
        super(CallablesList, self).__init__(*args, **kw)
    
    @classmethod
    def from_callables(cls, callables, operation=None):
        '''
        Assuming some of callables may be instances of `CallablesList`
        construct a new instance with a list of plain functions.
        '''
        def flat_list():
            for callabl in callables:
                try:
                    for f in callabl:
                        yield f
                except TypeError:
                    yield callabl
        operation = operation or (lambda x,y: None)
        return cls(flat_list(), operation=operation)
    
    
    def __call__(self, *args, **kw):
        results = [f(*args, **kw) for f in self]
        results = reversed(results) # make it queue not stack
        return reduce(self.operation, results)

