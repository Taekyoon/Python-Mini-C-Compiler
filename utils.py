import os

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.items())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

def get_filename(path):
    base = os.path.basename(path)
    return os.path.splitext(base)[0]

def file_content_to_string(content):
    string = ""
    for line in content:
        string += line
    return string
