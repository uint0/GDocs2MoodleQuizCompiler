class ListGroup:
    def __init__(self, el):
        self._el = el
        self._items = []
        self._depth = 0

    def add_item(self, item):
        self._items.append(item)

    @property
    def children(self):
        return self._items[:]

    @property
    def depth(self):
        return self._depth

    @depth.setter
    def depth(self, v):
        self._depth = v

    def __str__(self, indent=0):
        padding = " " * indent
        return padding + "ListGroup {\n" +\
                   "\n".join(i.__str__(indent=indent+2) for i in self._items) +\
               "\n" + padding + "}"

class ListItem:
    def __init__(self, el):
        self._el = el
        self._title = None
        self._groups = []
        self._depth = 0

    def set_title(self, title):
        self._title = title

    def add_group(self, group):
        self._groups.append(group)

    @property
    def depth(self):
        return self._depth

    @depth.setter
    def depth(self, v):
        self._depth = v

    @property
    def title(self):
        return self._title

    @property
    def groups(self):
        return self._groups

    def __str__(self, indent=0):
        padding = " " * indent
        return padding + "ListItem [title="+str(self._title)+", depth="+str(self._depth)+"] {\n" +\
                    "\n".join(g.__str__(indent=indent+2) for g in self._groups) +\
                "\n" + padding + "}"

class Title:
    def __init__(self, el):
        self._el = el
        self._text = None

    def set_text(self, text, preserve_spacing=False):
        self._text = text if preserve_spacing else text.strip()

    def __str__(self):
        return self._text
