"""
^x denotes x as being virtual - i.e. not implemented but merely used
to distinguish different allowed syntaxes

Grammar
===
List-Group: "<ol>" List-Item* "</ol>"
List-Item:  "<li>" Title List-Group? "</li>"
Title: ^PlainTitle | ^ContentTitle
^PlainTitle: "<p>" <HTML> "</p>"
^ContentTitle: "<div>" <HTML> "</div>"
"""

import bs4
import ast_elements.base as ast_el

class ASTGenerator:
    def __init__(self):
        self._ast = None

    def get_root(self):
        return self._ast
    
    def parse_root(self, el):
        children = [c for c in el.children if isinstance(c, bs4.Tag)]
        if len(children) == 0:
            raise SyntaxError("Document is empty")
        elif len(children) > 1:
            raise SyntaxError(f"Too many children in document, expected 1 found {len(children)}")
        else:
            self._ast = self.parse_group(el.findChildren()[0])[0]

    def parse_group(self, el):
        if el.name.lower() != 'ol':
            raise SyntaxError(f'Expected Group (ol), Found {el.name} instead')

        group = ast_el.ListGroup(el)
        for child in el.children:
            if isinstance(child, bs4.Tag):
                it, depth = self.parse_listitem(child)
                group.add_item(it)
                group.depth = max(group.depth, depth)

        return group, group.depth

    def parse_listitem(self, el):
        if el.name.lower() != 'li':
            raise SyntaxError(f'Expected List-Item (li), Found {el.name} instead')

        item = ast_el.ListItem(el)
        children = el.findChildren(recursive=False)

        if len(children) == 0:
            #TODO: add ignore support for this
            raise SyntaxError(f'List-Item has no children')
        else:
            item.set_title(self.parse_title(children[0]))
            item.depth = 0
            if len(children) == 2:
                grp, depth = self.parse_group(children[1])
                item.add_group(grp)
                item.depth = grp.depth + 1
            elif len(children) > 2:
                #TODO: treat this as a warning
                raise SyntaxError(f'Found unexpected child in List-Item (expected 1 or 2 children, found {len(children)})')

        return item, item.depth

    def parse_title(self, el):
        if el.name.lower() not in ('p', 'div'):
            raise SyntaxError(f'Expected Title (p, div), Found {el.name} instead')

        title = ast_el.Title(el)
        title.set_text(el.text)

        return title

    def __str__(self):
        return str(self._ast)
