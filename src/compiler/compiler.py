from bs4 import BeautifulSoup
from ASTGenerator import ASTGenerator
from ASTAnnotater import ASTAnnotator
from QBEmitter import QBEmitter

class Compiler:
    def __init__(self, ir_file):
        self._ir_filename = ir_file
        self._html = None
        self._ast = None

    def prepare(self):
        pass

    def scan(self):
        self._html = BeautifulSoup(open(self._ir_filename).read(), 'html.parser')

    def generate(self):
        assert(self._html is not None)

        self._ast = ASTGenerator()
        self._ast.parse_root(self._html)

        # print(str(self._ast))

    def annotate(self):
        assert(self._ast is not None)

        self._aast = ASTAnnotator(self._ast)
        self._aast.anno_root(self._ast.get_root())

        # print(str(self._aast))

    def emit(self):
        assert(self._aast is not None)
        self._emitted = QBEmitter(self._aast.get_root(), 'test-quiz')
        self._emitted.emit_root()

        return str(self._emitted)

    def tmp_print(self, tree):
        attrs = []
        for img in tree.select('img'):
            attrs.append(img.attrs['src'])
            img.attrs['src'] = ''

        print(tree.prettify())

        for i, img in enumerate(tree.select('img')):
            img.attrs['src'] = attrs[i]


if __name__ == '__main__':
    import sys

    compiler = Compiler(sys.argv[1])
    compiler.prepare()
    compiler.scan()
    compiler.generate()
    compiler.annotate()
    compiled = compiler.emit()

    print(compiled)
