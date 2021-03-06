"""
QBEmitter
===

An emitter that emits questions in a Question Bank format. This is the only emitter that produces tags.

Given a annotated AST we aim to emit xml in the expected output quiz format. The emitted xml will remain in a in-memory
representation, allowing for the compiler main to decide on how it should be serialized (this should largely only be a
consideration of prettyfying).

The emitter will not deal with categorization, complex tagging, or all but the simplest metadata. Requirements of such should be
realised using the tagger. (See description.md for more details)

Example:
AST
Question-Set 1 [role=Question]
\___ Question-Super 2 [title=Title]
     \_______________ Question-Set 3 [title=Title, role=SubQuestion]
                      \_____________ Question 4 [title=Title]
                                     \_________ Answer-Set 5
                                                \___________ Answer 6

Grouping is done by category - i.e. each emission is associated with one category. This is since moodle
does not support adding from tags.
"""

from ast_elements import base as ast_bs, extended as ast_el
import datetime
import xml.etree.ElementTree as xml

class QBEmitter:
    def __init__(self, ast, quiz_id):
        self._ast = ast
        self._root = None
        self._quiz_id = quiz_id

    def emit_root(self):
        root = xml.Element('quiz')
        self.emit_category(root)
        self.emit_question_set(self._ast, root)

        # Support python3.7
        self._root = root
        return root

    def emit_category(self, root, parent_group=None):
        if parent_group is None:
            parent_group = datetime.datetime.today().year

        question = xml.SubElement(root, 'question', {'type': 'category'})
        category = xml.SubElement(question, 'category')
        text     = xml.SubElement(category, 'text')
        text.text = f"$course$/Earth & Environmental Summer School/{parent_group}/{self._quiz_id}"

    def emit_question_set(self, qs, root):
        assert isinstance(qs, ast_el.QuestionSet)

        for i, child in enumerate(qs.children):
            if isinstance(child, ast_el.Question):
                self.emit_question(child, root)
            elif isinstance(child, ast_el.QuestionSuper):
                self.emit_super(child, root)
            else:
                raise TypeError(f'Found unexpected child of question_set with type {type(child).__name__}')

    def emit_super(self, s, root):
        assert isinstance(s, ast_el.QuestionSuper)
        # If a super contains a description we emit it here
        if s.title is not None:
            title = str(s.title)
            question = xml.SubElement(root, 'question', {'type': 'description'})

            name = xml.SubElement(question, 'name')
            name_text = xml.SubElement(name, 'text')
            name_text.text = title[:32] + '...'

            question_text = xml.SubElement(question, 'questiontext', {'format': 'html'})
            question_text = xml.SubElement(question_text, 'text')
            question_text.text = title

            tmp = xml.SubElement(question, 'generalfeedback', {'format': 'html'})
            tmp = xml.SubElement(tmp, 'text')
            defaults = {'defaultgrade': '0.0000000', 'penalty': '0.0000000', 'hidden': '0'}
            for field, val in defaults.items():
                tmp = xml.SubElement(question, field)
                tmp.text = val

        self.emit_question_set(s.sub_questions, root)


    def emit_question(self, q, root):
        question = xml.SubElement(root, 'question', {'type': q.question_type})

        # We assume multichoice question as that is the only format we support
        tmp = None

        # TODO: clean this up -- write a dict to xml converter or some sort of wrapper around ElementTree
        #                        alternatively dynamically consume a question template file and fill it in
        # <name><text>QUESTION NAME</text></name>
        tmp = xml.SubElement(question, 'name')
        tmp = xml.SubElement(tmp,      'text')
        tmp.text = str(q.title)[:32] + '...' # TODO: better generation scheme for question names

        # <questiontext><text>QUESTION TEXT</text></questiontext>
        tmp = xml.SubElement(question, 'questiontext', {'format': 'html'})
        tmp = xml.SubElement(tmp,      'text')
        tmp.text = str(q.title)

        # <generalfeedback><text></text></generalfeedback>
        tmp = xml.SubElement(question, 'generalfeedback', {'format': 'html'})
        tmp = xml.SubElement(tmp,      'text')

        # <defaultgrade></defaultgrade>
        tmp = xml.SubElement(question, 'defaultgrade')
        tmp.text = str(len(q.answers.answers)) # NOTE: For weighing everything the same: '1.0000000'

        # <penalty></penalty>
        tmp = xml.SubElement(question, 'penalty')
        tmp.text = '0'

        # <hidden>, <single>, <shuffleanswers>, <answernumbering>, <correctfeedback>, <partiallycorrectfeedback>
        # <incorrectfeedback>
        defaults = {
            'hidden': '0',
            'single': 'false',
            'shuffleanswers': 'false',  # NOTE: For shuffling answers 'true',
            'answernumbering': 'abc'
        }
        feedback_defaults = {
            'correctfeedback': 'Your answer is correct.',
            'partiallycorrectfeedback': 'Your answer is partially correct.',
            'incorrectfeedback': 'Your answer is incorrect.'
        }
        for field, val in defaults.items():
            tmp = xml.SubElement(question, field)
            tmp.text = val

        for field, val in feedback_defaults.items():
            tmp = xml.SubElement(question, field, {'format': 'html'})
            tmp = xml.SubElement(tmp, 'text')
            tmp.text = val

        self.emit_answerset(q.answers, question)

        return question

    def emit_answerset(self, answers, root):
        # As moodle does not have a corresponding answer set structure, we transparently
        # hand off to the answer emitter
        for answer in answers.answers:
            self.emit_answer(answer, root)

    def emit_answer(self, answer, root):
        answer_xml = xml.SubElement(root, 'answer', {'fraction': str(answer.marks), 'format': 'html'})

        text = xml.SubElement(answer_xml, 'text')
        text.text = str(answer.text)

        feedback = xml.SubElement(answer_xml, 'feedback', {'format': 'html'})
        feedback_text = xml.SubElement(feedback, 'text')
        feedback_text.text = 'No'  # TODO: get proper feedback

        return answer_xml

    def debug_print(self, el=None, indent=""):
        if el is None: el = self._root

        print(indent + str(el))
        for c in el.getchildren():
            self.debug_print(el=c, indent=" " * (len(indent)+2))


    def __str__(self):
        return xml.tostring(self._root, xml_declaration=True,  encoding='unicode', short_empty_elements=False)
