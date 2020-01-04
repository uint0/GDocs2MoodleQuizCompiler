# Quiz Compiler

This a utility for "transpiling" a bullet-point google docs quiz into a format that may be imported into moodle.
Curently there is only support for the HTML and RTF exported formats of a google doc, with the RTF format
requiring an additional dependancy on libreoffice.

For more details on internals please see the `docs/` folder.

## Installation
This utility only depends on `beautifulsoup4` for parsing HTML IR. If you wish to also 

## Usage

## TODOs
 - Images and tables are present within the IR, they are however stripped during the final production. Ideally these would be kept so Images do not need to be manually inserted.
 - Currently the quiz itself is not generated, ideally a moodle backup just for the quiz could be generated and restored.
 - The tagger is not implemented
