args = None

def get_args(content=None):
    global args
    if args is None:
        args = content
    return args
     