# cs.object


"""Python object modulator."""


import logging
log = logging.getLogger()


class Parsable(object):
    """A class where slots are parsable.

    Provides methods to import and export values for data slots from dictionaries.

    Use case:
        - Get a dictionary from any object structure.
        - Get a JSON or YAML string from any object structure.
        - Parse a dictionary to add/overwrite object slots with values.

    .. exec_code::
        :caption: Example code:
        :caption_output: Result:

        import miscset
        class Container(miscset.io.Parsable):
            def __init__(self, value):
                self.value = value
        c = Container([1,2,3])
        c.import_dict({"foo": "bar"}, add = True)
        print(c.get_json())

    """

    def __init__(self):
        """Initialize a Parsable object.

        Initializes the object and calls the `reset` function.
        """
        self.reset()

    def reset(self):
        """Reset slots to default values.

        This method implemented here does not affect anything.

        It is a placeholder for subclasses implementing this method.
        When calling the class constructor, this method will be called.
        """
        return

    def __str__(self):
        """Create a string representation of the object data slots."""
        return self.description()

    def get_text(self, name = None, sep = os.linesep + "  ", private = True):
        """Return a description.

        Args:
            name (str): Provide a custom name of the class shown as prefix.
            sep (str): A string separating the values.
            private (bool): Show privat slots (starting with an underscore "_").

        Returns:
            str: A text representation of the object data slots.
        """
        if name is None:
            name = "miscset.io.Parsable"
        txt = "<{}:".format(name)
        for var in vars(self):
            if not private and var.startswith("_"):
                continue
            value = getattr(self, var)
            if type(value) == type([]):
                value = [ str(i) for i in value ]
            if type(value) == type({}):
                value = { k: str(v) for k,v in value.items() }
            txt += "{}{}={}".format(sep, var, value)
        txt += ">"
        return txt

    def get_dict(self):
        """Return values of the data slots as dictionary.

        Same as accessing the `__dict__` slot from a class instance.

        Returns:
            dict: A dictionary with keys named as the class instance slots
                containing the respective values.
        """
        return self.__dict__

    def get_json(self):
        """"Return values of the data slots as a json string.

        Returns:
            str: A JSON formatted string.
        """
        return json.dumps(self.get_dict())

    def get_yaml(self):
        """"Return values of the data slots as a yaml string.

        Returns:
            str: A YAML formatted string.
        """
        return yaml.dump(self.get_dict())

    def import_dict(self, obj, add = False):
        """Import a dictionary into data slots.

        Args:
            obj (dict): A dictionary from which keys become
               slots and assigned the values.
            add (bool): Whether to add a key as slot if it
               did not yet exist.
        """
        self.reset()
        if not type(obj) == type({}):
            return
        if obj is None:
            return
        if not callable(getattr(obj, "keys", None)):
            return
        varnames = [key for key, value in vars(self).items()]
        #obj = { key: obj.get(key) for key in obj.keys() if key in varnames }
        for key, value in obj.items():
            if key not in varnames and not add:
                continue
            setattr(self, key, value)
