#!/usr/bin/env python3

from flask import Flask, request, jsonify, make_response
from dataclasses import dataclass
import string
import json
import sys
import random


app = Flask(__name__)
from wordle_solver import WorldSolverMultiList


@dataclass
class SolverAPIParameters:
    opener_word_list_file_path:str = "english_words_opener.txt"
    full_word_list_file_path:str = "english_words_full.txt"
    max_suggested_words:str = 10
    logging_enabled:bool = True


def write_log(log):
    if SolverAPIParameters.logging_enabled:
        print(log)


def handle_tries(ui_tries:list, word_length: int, exclude_plurals: bool=True, shuffle_suggested_words: bool=False, visit: str=None):
    if isinstance(ui_tries, list):
        tries = [(attempt["word"].lower(), attempt["symbols"]) for attempt in ui_tries if "word" in attempt and "symbols" in attempt]
        solver_multi = WorldSolverMultiList([SolverAPIParameters.opener_word_list_file_path, SolverAPIParameters.full_word_list_file_path], word_length=word_length, exclude_plurals=exclude_plurals)
        solver_multi.max_try_indexes_for_lists = [2, sys.maxsize]
        if any([True for attempt in tries if any([True for letter in attempt[0] if letter not in string.ascii_lowercase])]):
            write_log(json.dumps({"error":"invalid_chars", "request": ui_tries}))
            return make_response(jsonify(message="Invalid character(s) detected in words"), 400)
        if any([True for attempt in tries if any([True for symbol in attempt[1] if symbol not in solver_multi.solvers[0].permitted_input_symbols])]):
            write_log(json.dumps({"error":"invalid_symbols", "request": ui_tries}))
            return make_response(jsonify(message="Invalid symbol(s) detected in symbols"), 400)
        if sum([1 for attempt in tries if len(attempt[0]) == word_length and len(attempt[1]) == word_length]) != len(tries):
            write_log(json.dumps({"error":"invalid_lengths", "request": ui_tries}))
            return make_response(jsonify(message="Invalid length for word(s) or symbol(s)"), 400)
        solver_multi.tries = tries
        solver_multi.update_pattern_paramters()
        suggested_words_results = solver_multi.get_suggested_words()
        suggested_words = suggested_words_results.words[:SolverAPIParameters.max_suggested_words]
        if shuffle_suggested_words:
            random.shuffle(suggested_words)
        write_log(json.dumps({"error":None, "request": ui_tries, "response": suggested_words, "visitId": visit}))
        return jsonify(word_list=suggested_words_results.word_list_file_path,
                        suggested_words=suggested_words)
    write_log(json.dumps({"error":"wrong_parameter_type", "request": ui_tries, "visitId": visit}))
    return make_response(jsonify(message="Invalid request"), 400)


def entrypoint_cloudfunction(flask_request):
    if request.method == "OPTIONS":
        cors_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600"
        }
        return ("", 204, cors_headers)
    word_length = 5
    exclude_plurals=True
    shuffle_suggested_words=False
    visitId = None
    if flask_request.args:
        if "wordlength" in flask_request.args:
            word_length = int(flask_request.args.get("wordlength"))
        if "plurals" in flask_request.args:
            exclude_plurals = not (flask_request.args.get("plurals") == "true")
        if "shuffle" in flask_request.args:
            shuffle_suggested_words = (flask_request.args.get("shuffle") == "true")
        if "visit" in flask_request.args:
            visitId = flask_request.args.get("visit")
    ui_tries = flask_request.get_json()
    http_response = handle_tries(ui_tries=ui_tries, word_length=word_length, exclude_plurals=exclude_plurals, shuffle_suggested_words=shuffle_suggested_words, visit=visitId)
    http_response.headers["Access-Control-Allow-Origin"] = "*"
    return http_response


@app.route("/", methods=["POST", "OPTIONS"])
def entrypoint_flask():
    return entrypoint_cloudfunction(request)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7210)
