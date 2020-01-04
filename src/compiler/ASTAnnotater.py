"""
Rules
===

Translation happens on a set of rules.
We keep walking the tree and reapplying the rules until the tree stops
changing

The most complex case is as follows

Parse Tree

Group 1
 \_____ ListItem 2
        \_________ Title
        \_________ Group 3
                   \______ ListItem 4
                           \_________ Title
                           \_________ Group 5
                                      \______ ListItem 6
                                              \_________ Title
                  \______ ListItem ...
                                      \______ ListItem ...
\_____ ListItem ...


AST

Question-Set 1 [role=Question]
\___ Question-Super 2 [title=Title]
     \_______________ Question-Set 3 [title=Title, role=SubQuestion]
                      \_____________ Question 4 [title=Title]
                                     \_________ Answer-Set 5
                                                \___________ Answer 6

As of now we do not support nesting depths > 3

Allowed children
Question-Set:   (Question-Super | Question)*
Question-Super: [^Title] (Question-Set)+
Question:       ^Title Answer-Set
Answer-Set:     (Answer)*
Answer:         ^Title
"""

from ast_elements import base as ast_bs, extended as ast_el

class ASTAnnotator:
    def __init__(self, raw_ast):
        self._raw = raw_ast
        self._aast = None

    def anno_root(self, root):
        self._aast = self.anno_question_set(root)

    def anno_question_set(self, el):
        assert isinstance(el, ast_bs.ListGroup)

        qs = ast_el.QuestionSet()
        for child in el.children:
            assert isinstance(child, ast_bs.ListItem)
            if child.depth == 0:
                raise Exception(f'Found ListItem of depth 0 in question set. Please ensure all answers have an associated question')
            if child.depth == 1:
                qs.add_question(self.anno_question(child))
            elif child.depth == 2:
                qs.add_question(self.anno_question_super(child))
            else:
                raise TypeError(f'Questions of depth {child.depth} are currently not supported')

        return qs

    def anno_question_super(self, el):
        assert isinstance(el, ast_bs.ListItem)
        assert len(el.groups) == 1

        sup = ast_el.QuestionSuper()

        sup.title = el.title
        sup.sub_questions = self.anno_question_set(el.groups[0])

        return sup

    def anno_question(self, el):
        assert isinstance(el, ast_bs.ListItem)
        assert len(el.groups) == 1

        q = ast_el.Question()
        q.title   = el.title
        q.answers = self.anno_answer_set(el.groups[0])

        return q

    def anno_answer_set(self, el):
        assert isinstance(el, ast_bs.ListGroup)

        anss = ast_el.AnswerSet()

        # NOTE: We treat (Y) as indicative of a correct answer
        # NOTE: We aim to produce a marking scheme which achieves the following
        #       For each question, a correct answer produces +1 mark, and each incorrect answer
        #       produces -0.5 marks, with the total score per question being capped at 0
        #
        #       We are not concerned with relative important, i.e. a question with 100 correct answers
        #       will be worth 100 marks, even if it is less challenging than a question with 1 correct answer
        #       (which would be worth one mark). In order to normalize the relative weights, it is nessecary
        # NOTE: marking scheme is calculated as follows
        #       A question with `n` correct answers is allocated n marks.
        #       a   correct answer is weighted    1/(# correct) * 100
        #       a incorrect answer is weighted -0.5/(# correct) * 100
        #
        #       
        n_correct   = sum(1 for child in el.children if '(Y)' in str(child.title))

        # Due to moodle not allowing arbitrary weighitngs this may not work
        correct_weight   =  1/n_correct * 100
        incorrect_weight = -0.5/n_correct * 100

        for child in el.children:
            assert child.depth == 0
            mark = incorrect_weight
            if '(Y)' in str(child.title):
                child.title.set_text(str(child.title).replace('(Y)', ''))
                mark = correct_weight

            answer = self.anno_answer(child)
            answer.marks = mark
            anss.add_answer(answer)

        return anss

    def anno_answer(self, el):
        assert isinstance(el, ast_bs.ListItem)
        assert len(el.groups) == 0

        ans = ast_el.Answer()
        ans.set_text(el.title)

        return ans

    def get_root(self):
        return self._aast

    def __str__(self):
        return str(self._aast)
