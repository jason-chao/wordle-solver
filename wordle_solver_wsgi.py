#!/usr/bin/env python3

from flask import Flask, request, jsonify, make_response
import string
from datetime import datetime
app = Flask(__name__)
from wordle_solver import WordleSolver

simple_word_list_file_path = "english_words_10k_mit.txt"
extended_word_list_file_path = "english_words_alpha_dwyl.txt"
max_suggested_words = 10

@app.route("/<int:word_length>", methods=["POST"])
def solve(word_length: int):
    ui_tries = request.json
    if isinstance(ui_tries, list):
        tries = [(attempt["word"].lower(), attempt["symbols"]) for attempt in ui_tries if "word" in attempt and "symbols" in attempt]
        solver_simple = WordleSolver(simple_word_list_file_path, word_length=word_length)
        if any([True for attempt in tries if any([True for letter in attempt[0] if letter not in string.ascii_lowercase])]):
            return make_response(jsonify(message="Invalid character(s) detected in words"), 400)
        if any([True for attempt in tries if any([True for symbol in attempt[1] if symbol not in solver_simple.permitted_input_symbols])]):
            return make_response(jsonify(message="Invalid symbol(s) detected in symbols"), 400)
        if sum([1 for attempt in tries if len(attempt[0]) == word_length and len(attempt[1]) == word_length]) != len(tries):
            return make_response(jsonify(message="Invalid length for word(s) or symbol(s)"), 400)
        word_list_source = "simple"
        solver_simple.tries = tries
        solver_simple.update_pattern_paramters()
        suggested_words = solver_simple.get_suggested_words()
        if len(suggested_words) <= 0:
            word_list_source = "extended"
            solver_extended = WordleSolver(extended_word_list_file_path, word_length=word_length)
            solver_extended.tries = solver_simple.tries
            solver_extended.update_pattern_paramters()
            suggested_words = solver_extended.get_suggested_words()
        return jsonify(word_list=word_list_source,
                        suggested_words=suggested_words[:max_suggested_words])
    return make_response(jsonify(message="Invalid request"), 400)
    

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=7210)
