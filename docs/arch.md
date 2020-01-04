# Input data
We require the input to be directly exported from google docs with no changes. We current support the 
html export format (referred to as ghtml) and rtf.

# Structure
The compiler works in two compulsory steps and one optional step.

First we introduce a compiler frontend that we call the normalizer.
This takes the raw exported data and converts it into an intermediate representation.

Next the compiler backend operates on the IR and emits the appropriate xml format. There is also an option
for the backend to emit the raw ast.

Finally the user has the option to run a optional tagger on the backend generated ast. This will tag
questions as well as allow the user to add titles, marks, etc. This should then generate a tagged
xml format.

## Normalization
Each input format is associated with a different normalizer. E.g. the ghtml-normalizer will take in
the zipped html export and emit the equivalent IR to the rtf-normalizer taking in a rtf file.

```
+-------------------+                +------------+
| Raw Export format | -- Scanner --> | Token List | --+
+-------------------+                +------------+   |
                                                      |
+------------------ AST Generation -------------------+
|
|    +-----+                +---------+
+--> | AST | -- Emitter --> | HTML IR |
     +-----+                +---------+
```

The HTML IR is based on the output of the lowriter rtf -> html conversion. All other normalizers should
aim to produce equivalent output. It is also for this reason that we need to re-emit a HTML IR instead
of just handing the ast down to the backend.

## Compilation
The backed will take in normalized HTML IR and generate a moodle xml question bank format.

```
+---------+                +------------+
| HTML IR | -- Scanner --> | Token List | --+
+---------+                +------------+   |
                                            |
+------------- AST Generation --------------+
|
|    +-----+                      +------------+
+--> | AST | -- Type inferrer --> | Tagged AST | --+
     +-----+                      +------------+   |
                                                   |
+-------------------- Emitter ---------------------+
|
|    +-------------------+
+--> | Moodle XML Format |
     +-------------------+
```

The user can specify a flag for the compiler to generate either a plain xml format or a raw ast file, to be
passed into the tagger

## Tagging
The user can further manually annotate the AST by providing marks, tags as well as general metadata about
both questions and the quiz

AST -- Manual Tagging --> Tagged AST -- Emitter --> Moodle XML Format

```
+-----+                       +------------+
| AST | -- Manual Tagging --> | Tagged AST | --+
+-----+                       +------------+   |
                                               |
+------------------ Emitter -------------------+
|
|    +-------------------+
+--> | Moodle XML Format |
     +-------------------+
```
