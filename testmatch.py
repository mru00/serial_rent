import difflib


test = ['american', 'american dad!', 'boardwalk empire', 'american']

print difflib.get_close_matches('office', test)

