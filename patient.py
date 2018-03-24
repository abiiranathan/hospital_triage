config={"host":"localhost","user":"root","password":"cmaster2018","database":"patients"}

class AttributeInitType(type):
    def __call__(self, *args, **kwargs):
        """Create a new instance"""

        # First create an object in the normal way
        obj = type.__call__(self, *args)
        # Set attribute on the new object

        for name, value in kwargs.items():
            setattr(obj, name, value)

        return obj

class Patient(metaclass=AttributeInitType):
    ''' Metaclass sets arguments, kwargs'''

    @classmethod
    def from_row(cls, row):
        return Patient(*row)

    @property
    def description(self):
        return " ".join(str(value) for value in self.__dict__.values())

    def __str__(self):
        return"{}".format(type(self))

    def __iter__(self, patient):
        return iter(self.from_row(patient))


