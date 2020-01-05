import os
import sys
# Ugly hacks to allow relative importing without packaging the source code
SERVER_DIR = os.path.dirname(os.path.realpath(__file__))

sys.path.append(f"{SERVER_DIR}/src/compiler")
sys.path.append(f"{SERVER_DIR}/src/normalizer")
import compiler
import RTFNormalizer

import flask
from werkzeug.utils import secure_filename
import base64 as b64

app = flask.Flask(__name__)

INDEX_HTML = """
<!doctype html>
<html>
<head>
    <title>Quiz Compiler</title>
</head>
<body style="padding: 0; margin: 0; display: grid; grid-template-columns: 1fr 2fr 1fr; height: 100vh; font-family: sans-serif">
    <div style="background-color: #eee; height: 100%; padding: 1em">
        <div style="font-weight: bold">Instructions</div>
        <ol>
            <li>Copy the questions to be generated into a google doc</li>
            <li>Export the google doc as RTF</li>
            <li>Input a name</li>
            <li>Upload the RTF file</li>
            <li>Download the produced file import it as a Moodle XML file to the moodle question bank</li>
            <li>When creating the quiz, filter by questions in category <code>[SOME PREFIX]/2020/QuizName</code></li>
        </ol>
    </div>
    <div style="padding: 1em">
        <div style="font-weight: bold">Compile</div>
        <!-- Basic form upload, TODO: make this pretty and AJAX -->
        <form action="/" method="POST" enctype="multipart/form-data" style="margin: 1em; display: grid; grid-template-columns: 1fr 3fr; row-gap: 0.5rem;">
            <label>Quiz Name:</label>
            <input type="text" placeholder="Quiz Name" name="name" required>
            <label>RTF File:</label>
            <input type="file" name="spec" required>
            <input type="submit" value="Generate">
        </form>
    </div>
    <div style=" background-color: #eee; height: 100%; padding: 1em">
        <div style="font-weight: bold;">Result</div>
        <div>{result}</div>
    </div>
</body>
</html>
"""

UPLOAD_DIR = os.getcwd() + "/uploads"

@app.route('/', methods=["GET", "POST"])
def generate():
    result = ""
    if flask.request.method == 'POST':
        file = flask.request.files['spec']
        quiz_name = flask.request.form['name']
        file_name = secure_filename(file.filename)
        file_loc = os.path.join(UPLOAD_DIR, file_name)
        ir_filename = UPLOAD_DIR + "/" + file_name + ".ir.html"
        file.save(file_loc)

        rtfn = RTFNormalizer.RTFNormalizer(file_loc)
        rtfn.prepare(out_dir=UPLOAD_DIR)
        rtfn.scan()
        rtfn.generate()
        rtfn.emit(open(ir_filename, "w"))

        comp = compiler.Compiler(ir_filename, quiz_name)
        comp.prepare()
        comp.scan()
        comp.generate()
        comp.annotate()
        compiled = comp.emit()
        result = b64.b64encode(compiled.encode()).decode()

        result = f'<a href="data:text/xml;base64,{result}" download="{quiz_name}.moodle.xml">Download</a>'

    return INDEX_HTML.format(result=result)

if __name__ == '__main__':
    app.run(port=5000)
