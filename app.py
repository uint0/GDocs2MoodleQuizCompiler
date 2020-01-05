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

app = flask.Flask(__name__)

INDEX_HTML = """
<!doctype html>
<html>
<head>
<title>Quiz Compiler</title>
<style></style>
</head>
<body>
    <div>
        <div>Instructions</div>
        <ol>
            <li>Copy the questions to be generated into a google doc</li>
            <li>Export the google doc as RTF</li>
            <li>Input a name</li>
            <li>Upload the RTF file</li>
            <li>Download the produced file import it as a Moodle XML file to the moodle question bank</li>
            <li>When creating the quiz, filter by questions in category <code>[SOME PREFIX]/2020/QuizName</code></li>
        </ol>
    </div>
    <div>
        <!-- Basic form upload, TODO: make this pretty and AJAX -->
        <form action="/generate" method="POST" enctype="multipart/form-data">
            <input type="text" placeholder="Quiz Name" name="name" required>
            <input type="file" name="spec" required>
            <input type="submit" value="Generate">
        </form>
    </div>
</body>
</html>
"""

UPLOAD_DIR = os.getcwd() + "/uploads"

@app.route('/')
def index():
    return INDEX_HTML

@app.route('/generate', methods=["POST"])
def generate():
    file = flask.request.files['spec']
    file_name = secure_filename(file.filename)
    file_loc = os.path.join(UPLOAD_DIR, file_name)
    ir_filename = UPLOAD_DIR + "/" + file_name + ".ir.html"
    file.save(file_loc)

    print(file_loc)
    rtfn = RTFNormalizer.RTFNormalizer(file_loc)
    rtfn.prepare(out_dir=UPLOAD_DIR)
    rtfn.scan()
    rtfn.generate()
    rtfn.emit(open(ir_filename, "w"))

    comp = compiler.Compiler(ir_filename, flask.request.form['name'])
    comp.prepare()
    comp.scan()
    comp.generate()
    comp.annotate()
    compiled = comp.emit()

    return flask.Response(
        compiled,
        mimetype="text/xml",
        headers={'Content-Disposition': f"attachment; filename={flask.request.form['name']}.moodle.xml"}
    )

if __name__ == '__main__':
    import sys
    import os

    app.run(port=5000, debug=True)
