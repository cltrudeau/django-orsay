import os

# ===========================================================================

def thumbpath(filename, thumbdir):
    """Takes a fully qualified image filename and converts it to its thumbnail 
    equivalent"""

    dirname, relname  = os.path.split(filename)
    base, _ = os.path.splitext(relname)

    thumbname = os.path.join(dirname, thumbdir, base + '.gif')
    return thumbname

