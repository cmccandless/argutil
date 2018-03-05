primitives = {
    'bool': bool,
    'int': int,
    'float': float,
    'complex': complex,
    'str': str,
    'list': list,
    'tuple': tuple,
    'bytes': bytes,
    'memoryview': memoryview,
    'bytearray': bytearray,
    'range': range,
    'set': set,
    'frozenset': frozenset,
    'dict': dict,
}

# Python 2 compatibility
try:
    primitives['long'] = long
except NameError:
    pass

try:
    primitives['unicode'] = unicode
except NameError:
    pass

try:
    primitives['buffer'] = buffer
except NameError:
    pass

try:
    primitives['xrange'] = xrange
except NameError:
    primitives['xrange'] = range
