"""File and other stream i/o methods.

Writing to

- **text files**
- **stderr**

or reading from

- **text files** as lines
- **yaml** or **json** files as dictionaries
- **csv** files as array

or parsing data (dictionary, json/yaml) to and from a ``Parsable`` class object made easy!
"""


import os
import sys
import csv
import json
import yaml
import logging
log = logging.getLogger()


from . import console
from . import dt


### file input


def read_txt(path, *args, **kwargs):
    """Read text as string from a file.
    
    Args:
        path (str): A path to a file.
        args, kwargs: Any other argument passed to `open`,
            such as mode, encoding, etc.

    Returns:
        str: The text (or bytestring, depending on the mode selected)
            from the selected file.
    """
    fs = open(path, *args, **kwargs)
    text = fs.read()
    fs.close()
    return text


def read_lines(path, strip = os.linesep, *args, **kwargs):
    """Read text as lines from a file.

    A file is read line by line and parsed as a list of strings.

    Args:
        path (str): File path.
        strip (str): Characters to strip from the end
            of each line. `None` to skip stripping.
        args, kwargs: Any other argument passed to `open`,
            such as mode, encoding, etc.

    Returns:
        list: Lines read from the file as a list of strings.
    """
    fs = open(path, *args, **kwargs)
    lines = fs.readlines()
    fs.close()
    if strip is not None:
        lines = [line.rstrip(strip) for line in lines]
    return lines


def read_json(path):
    """Read a JSON file.

    Read a JSON formatted file into a dictionary object.

    Args:
        path (str): File path to JSON formatted file.

    Returns:
        dict: Content of a JSON file parsed as dictionary.
    """
    fs = open(path, "r")
    d = json.load(fs)
    fs.close()
    return d


def read_yaml(path):
    """Read a YAML file.

    Read a YAML formatted file into a dictionary object.
    Supports usage of `!include`d files.
    Supports logging (see :py:mod:`cs`).

    Args:
        path (str): File path.

    Returns:
        dict: Content of a YAML file parsed as dictionary.

    .. exec_code::
        :caption: Example code:
        :caption_output: Result:

        import cs
        print(cs.io.read_yaml("tests/example.yml"))
    """
    # safe yaml loader extended with '!include' function
    class SafeIncluder(yaml.SafeLoader):
        def include(self, node):
            filename = os.path.join(os.path.dirname(self.stream.name), node.value)
            with open(filename, 'r') as f:
                return yaml.load(f, SafeIncluder)
    SafeIncluder.add_constructor('!include', SafeIncluder.include)
    # default to empty content
    d = {}
    # check file location
    if not os.path.isfile(path):
        logging.error("missing YAML file at {}".format(path))
        return d
    # parse file
    with open(path, "r") as fs:
        try:
            logging.info("parsing YAML from file {}".format(path))
            d = yaml.load(fs, Loader=SafeIncluder)
        except yaml.YAMLError as e:
            logging.error("failed importing {} YAML {}".format(path, e))
    # return
    logging.debug("parsed YAML content as {}".format(d))
    return d


### file output


def write_txt(text, path):
    """Write text to a file.

    A file at a path is opened writable,
    and the text from a string variable is inserted.

    Args:
        text (str): Text to write to a file at `path`.
        path (str): File path.
    """
    fs = open(path, "w")
    fs.write(text)
    fs.close()
    return


def write_stdout(text, newline = True):
    """Write text to the standard output file stream.
    
    A text string is written to the system standard output file stream,
    and optionally a newline is added.

    Args:
        text (str): Output text.
        newline (bool): Add a os specific line separator to
            the end of the text.

    .. exec_code::
        :caption: Example code:
        :caption_output: Result:

        import miscset
        miscset.io.write_stdout("Hello, world!")
    """
    sys.stdout.write(text)
    if newline:
        sys.stdout.write(os.linesep)
    sys.stdout.flush()
    return


def write_stderr(text, newline = True):
    """Write text to the standard error file stream.
    
    A text string is written to the system standard error file stream,
    and optionally a newline is added.

    Args:
        text (str): Output text.
        newline (bool): Add a os specific line separator to
            the end of the text.
    """
    sys.stderr.write(text)
    if newline:
        sys.stderr.write(os.linesep)
    sys.stderr.flush()
    return


def write_json(path, obj, default = repr):
    """Write an object representation to a json file.
    
    See https://docs.python.org/3/library/json.html#json.dump
    """
    fs = open(path, "w")
    fs.write(json.dumps(obj, default = default))
    fs.close()


### console output


def print_header(msg):
    console.flush(f"[{console.Color.blue}!default_tool_name!{console.Color.none}] {msg} - {dt.now()}")


def print_warning(msg):
    console.flush(f"{console.Color.yellow}warning{console.Color.none}: {msg}")


def print_error(msg):
    console.flush(f"{console.Color.red}error{console.Color.none}: {msg}")


def print_table(rows, delimiter='\t', output=sys.stdout, output_align=True, output_columns=None, na="", lsep=", ", cellwidth=44):
    if not rows:
        return  # Handle empty input gracefully
    def short(txt, nmax=30):
        if txt is None:
            return None
        stxt = str(txt)
        if len(stxt) > nmax:
            return f"{stxt[:(nmax-3)]}..."
        return txt
    for i in range(len(rows)):
        for key, value in rows[i].items():
            if na is not None and value is None:
                rows[i][key] = na
            if lsep is not None and isinstance(value, list):
                rows[i][key] = lsep.join(rows[i][key])
            if cellwidth is not None:
                rows[i][key] = short(rows[i][key], cellwidth)
    fieldnames = output_columns if output_columns else {key for row in rows for key in row.keys()}
    if output_align:
        log.debug("using manual alignment to render output")
        col_widths = {col: max(len(col), *(len(str(row.get(col, ''))) for row in rows)) for col in fieldnames}
        header = "  ".join(col.ljust(col_widths[col]) for col in fieldnames)
        print(header, file=output)
        for row in rows:
            row_str = "  ".join(str(row.get(col, '')).ljust(col_widths[col]) for col in fieldnames)
            print(row_str, file=output)
    else:
        log.debug("using csv to render output")
        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=delimiter, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def print_obj(obj):
    console.flush(json.dumps(obj, indent=4))