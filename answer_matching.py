import json

class AnswerMatcher:
    def __init__(self, predefined_answers_path):
        with open(predefined_answers_path, 'r') as file:
            self.predefined_answers = json.load(file)

    def match_answer(self, recognized_text):
        recognized_text = recognized_text.lower()
        for key, value in self.predefined_answers.items():
            if key == recognized_text:
                return value
        return "Unknown"
