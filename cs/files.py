# cs.files

"""methods to work on file systems"""


import os
import re
import logging
log = logging.getLogger()


def find(path = ".", recurse = True, type = None, regex = None, extensions = None,
    absolute = False, case = True):
    """Get list of paths to files in a folder.
    
    Args:
        path (str): Path to a folder on a filesystem.
        extensions
    
    .. exec_code::
        :caption: Example code:
        :caption_output: Result:

        import os
        import miscset
        paths = miscset.files.find(recurse = False)
        paths = os.linesep.join(paths)
        print(paths)
    """
    # defaults
    path = os.path.expanduser(path)
    if type is None:
        type = "df"
    names = []
    if case:
        case = re.IGNORECASE
    else:
        case = 0
    if regex is not None:
        regex = re.compile(regex, case)
    # cleanup extensions
    if extensions is not None:
        tmp = []
        for e in extensions:
            e = str(e).lower()
            if not e.startswith("."):
                e = f".{e}"
            tmp.append(e)
        extensions = tmp

    # helper
    def match_extensions(name, extensions):
        if extensions is None:
            return True
        ext = os.path.splitext(name)[1]
        return ext in extensions
    def match_regex(name, regex):
        if regex is None:
            return True
        return regex.search(name)
    def abs(name):
        return os.path.abspath(name)

    # collect
    level = 0
    for root, dnames, fnames in os.walk(path):
        # check recurse level
        if not recurse and level > 0:
            break
        level += 1
        # collect directories
        if "d" in type:
            for name in dnames:
                if not match_regex(name, regex):
                    continue
                name = os.path.join(root, name)
                if absolute:
                    name = abs(name)
                names.append(name)
        # collect files
        if "f" in type:
            for name in fnames:
                if not match_extensions(name, extensions):
                    continue
                if not match_regex(name, regex):
                    continue
                name = os.path.join(root, name)
                if absolute:
                    name = abs(name)
                names.append(name)
    return names

