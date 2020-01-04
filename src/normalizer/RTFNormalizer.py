"""
RTFNormalizer
===

Normalizes a rtf file.

Users can either manually call the RTFNormalizer or use the normalize_file(<file>) autorunner
to directly get the output.

Calls lowriter to convert the rtf into html and then hands work off to the LORTFHTMLNormalizer
"""
import os
import tempfile
import logging
import subprocess
from LORTFHTMLNormalizer import LORTFHTMLNormalizer

rtf_exporters = [
    {
        "name": "lowriter",
        "command": ["/usr/bin/lowriter",
                        "--headless",
                        "--convert-to", "html:XHTML Writer File", "--outdir", "<od>",
                        "<file>"],
        "normalizer": LORTFHTMLNormalizer
    }
]

class RTFNormalizer:
    def __init__(self, raw_file):
        self._file_name = raw_file
        self._delegate = None

    def prepare(self):
        assert(len(rtf_exporters) > 0)
        exporter = rtf_exporters[0]

        logging.info(f'Using rtf exporter [{exporter["name"]}]')

        cmd = []
        for c in exporter['command']:
            if c == '<od>': cmd.append('.')
            elif c == '<file>': cmd.append(self._file_name)
            else: cmd.append(c)

        logging.info(f'Calling: [{" ".join(cmd)}]')
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            logging.fatal('Failed to generate rtfhtml')
            return 1

        self._delegate = exporter['normalizer'](
            (self._file_name[:-4] if self._file_name.endswith('.rtf') else self._file_name) + '.html'
        )
        return self._delegate.prepare()

    def scan(self):
        assert(self._delegate is not None)
        return self._delegate.scan()

    def generate(self):
        assert(self._delegate is not None)
        return self._delegate.generate()

    def emit(self, stream):
        assert(self._delegate is not None)
        return self._delegate.emit(stream)

if __name__ == '__main__':
    import sys
    logging.basicConfig(level=logging.DEBUG)
    rtfn = RTFNormalizer(sys.argv[1])
    rtfn.prepare()
    rtfn.scan()
    rtfn.generate()
    rtfn.emit(open(sys.argv[2], 'w'))
