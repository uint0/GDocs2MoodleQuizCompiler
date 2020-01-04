class QuestionSet:
    def __init__(self):
        self._questions = []

    def add_question(self, q):
        self._questions.append(q)

    @property
    def children(self):
        return self._questions

    def __str__(self, indent=0):
        padding = " " * indent
        return padding + "QuestionSet {\n" +\
            "\n".join(q.__str__(indent=indent+2) for q in self._questions) +\
        "\n" + padding + "}"


class QuestionSuper:
    def __init__(self):
        self._title = None
        self._sub_questions = []  # QuestionSet

    @property
    def sub_questions(self): return self._sub_questions

    @sub_questions.setter
    def sub_questions(self, v): self._sub_questions = v

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, v):
        self._title = v

    def __str__(self, indent=0):
        padding = " " * indent
        return padding + f"QuestionSuper[text={self._title}] {{\n" +\
            self._sub_questions.__str__(indent=indent+2) +\
        "\n" + padding + "}"


class Question:
    def __init__(self):
        self._title = None
        self._answers = None

    @property
    def question_type(self): return 'multichoice'

    @property
    def answers(self): return self._answers

    @answers.setter
    def answers(self, v): self._answers = v

    @property
    def title(self): return self._title

    @title.setter
    def title(self, v): self._title = v

    def __str__(self, indent=0):
        padding = " " * indent
        return padding + f"Question[text={self._title}] {{\n" +\
            self._answers.__str__(indent=indent+2)
        "\n" + padding + "}"


class AnswerSet:
    def __init__(self):
        self._answers = []

    def add_answer(self, v):
        self._answers.append(v)

    @property
    def answers(self): return self._answers[:]

    def __str__(self, indent=0):
        padding = " " * indent
        return padding + "AnswerSet {\n" +\
            "\n".join(q.__str__(indent=indent+2) for q in self._answers) +\
        "\n" + padding + "}"


class Answer:
    def __init__(self):
        self._text = None
        self._marks = 0

    @property
    def marks(self): return self._marks

    @property
    def text(self): return self._text

    def set_text(self, v):
        self._text = v

    def set_marks(self, mark):
        self._marks = mark

    def __str__(self, indent=0):
        padding = " " * indent
        return padding + f"Answer[marks={self._marks}] {{ " + str(self._text) + " }"
