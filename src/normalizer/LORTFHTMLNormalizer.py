"""
LORTFHTMLNormalizer
===

Normalizes a the html file produced by running lowriter on a rtf file.

Users can either manually call the RTFNormalizer or use the normalize_file(<file>) autorunner
to directly get the output.
"""
import logging
from bs4 import BeautifulSoup, Tag as bs4Tag, Comment as bs4Comment

class LORTFHTMLNormalizer:
    def __init__(self, html_file):
        self._file = html_file
        self._html = None
        self._questions = None

    def prepare(self):
        return None

    def scan(self):
        self._html = BeautifulSoup(open(self._file).read(), "html.parser")

    def generate(self):
        assert(self._html is not None)

        # As we already have a walkable tree format we just need to find the list corresponding with
        # the questions

        # Our strategy will be as follows
        #   Determine if "MCQ" exists in the document
        #   If it does add (merging) all lists following "MCQ" (but before "END MCQ")
        #   Otherwise find the longest list (in terms of textContent) and set that as our list
        # TODO: add multi question set per document support
        # TODO: add human specified === MCQ === === END MCQ === Support
        # TODO: add non-top level MCQ/list support (current MCQ/question list must be a child of body)
        # TODO: add naked text support (it is current skipped)
        # TODO: add intelligent selection based on ol[start]

        # NOTE: This notably (hehe) misses any question sets that are nested within an element
        lists = []
        mcq_mode = False
        for child in self._html.body.children:
            if not isinstance(child, bs4Tag): continue
            if child.text.strip() == 'MCQ':
                lists = []
                mcq_mode = True

            if child.name.lower() == 'ol' or child.name.lower() == 'ul':
                lists.append(child)

        question_set = None
        if mcq_mode:
            question_set = lists[0]
            for i in range(1, len(lists)):
                # TODO: investigate using list().extend(list(children))
                for c in lists[i].children:
                    assert(c.name == 'li')
                    question_set.append(c)
        else:
            question_set = max(lists, key=lambda ls: len(ls.text))

        # Next strip out styling  (TODO: investigate the impact of this on boldness)
        list_elements = question_set.select('ol > li')
        for li in list_elements:
            annot = li.findChildren()[0].findChildren()[0]
            if annot.name.lower() == 'span':
                annot.decompose()

        for p in question_set.select('p, div'):
            p.attrs = {}

        for o in question_set.select('span.odfLiEnd, span[style="margin-left:0cm"]'):
            o.decompose()

        for imgspan in question_set.select('span[id^="Image"]'):
            del imgspan.attrs['style']
            del imgspan.attrs['class']

        for comment in question_set.find_all(string=lambda text: isinstance(text, bs4Comment)):
            comment.extract()

        self._questions = question_set
        return question_set

    def emit(self, stream, pretty=False):
        stream.write(self._questions.prettify() if pretty else str(self._questions))


def normalize_file(f, stream, pretty=False):
    normalizer = LORTFHTMLNormalizer(f)
    normalizer.prepare()
    normalizer.scan()
    normalizer.generate()
    normalizer.emit(stream, pretty)
    return normalizer


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        sys.stderr.write(f'Usage: {sys.argv[0]} [--pretty] <rtf html file>')
    else:
        pretty = False
        fn = sys.argv[1]
        if len(sys.argv) > 2:
            pretty = sys.argv[1] == '--pretty'
            fn = sys.argv[2]
        normalize_file(fn, sys.stdout, pretty=pretty)

