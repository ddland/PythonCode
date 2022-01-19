class Circular:
    """Circular generator for lists.

    Creates an iterator object which will always return a value.
    Ones the last element of the list is generated, it starts over.
    """

    def __init__(self, ll, i=0, reversed=False):
        """Initialise the generator object

        arguments:
            ll: list for which the circulair generator is created
            i: starting point, default 0
            reversed: boolean, if True list object is reversed, default False
        """

        self.i = i
        self.nlist = len(ll)
        if self.i >= self.nlist:
            self.i = 0

        if reversed:
            self.list = ll[::-1]
        else:
            self.list = ll

    def __iter__(self):
        """Iterator object which yields elements from the list.

        If the end of the list is reached, the iterator will start from the
        first element again.
        """
        while True:
            yield(self.list[self.i])
            self.i += 1
            if self.i >= self.nlist:
                self.i = 0
