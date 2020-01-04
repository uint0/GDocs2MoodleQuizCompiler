# Quiz Compiler

This a utility for "transpiling" a bullet-point google docs quiz into a format that may be imported into moodle.

For more details on internals please see the `docs/` folder.

## Installation
This utility depends on `lowriter` for conversion of RTF to HTML IR, there is a additional python dependancy on
`beautifulsoup4` for working with the HTML.

1. Install libreoffice
2. `pip install -r requirements.txt`

## Usage
Each part of the compiler must be invoked sequentially. As running lowriter produces a substantial amount of garbage, it is recommended to run this in a empty directory.
1. Export a google doc as a rtf file
2. Run the normalizer `python /path/to/RTFNormalizer.py <RTF file> <output file name | e.g. ir.html>`
3. Run the compiler `python /path/to/compiler.py <IR HTML> <Quiz Name | e.g. Minerals Quiz>`
4. Save the output (or pipe it) and upload the resultant file to moodle.

## TODOs
 - Images and tables are present within the IR, they are however stripped during the final production. Ideally these would be kept so Images do not need to be manually inserted.
 - Currently the quiz itself is not generated, ideally a moodle backup just for the quiz could be generated and restored.
 - The tagger is not implemented
