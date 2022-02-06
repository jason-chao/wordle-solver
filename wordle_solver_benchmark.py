#!/usr/bin/env python3

from dataclasses import dataclass
from typing import List
import json
import multiprocessing
from multiprocessing import Pool
import time

from wordle_game import WordleGame
from wordle_solver import WordleSolver
from utility import Utility


@dataclass
class Round:
    hidden_word: str
    guessed_times: int
    success: bool
    final_solver: str
    tries: List

word_length = 5
max_tries = 6
first_guess = "opera"

simple_word_list_file_path = "english_words_simple.txt"
mit10k_word_list_file_path = "english_words_10k_mit.txt"
dwyl_alpha_word_list_file_path = "english_words_alpha_dwyl.txt"
wordle_original_word_list_file_path = "english_words_original_wordle.txt"

word_list = [] 

simple_word_list = Utility.load_word_list(simple_word_list_file_path)
mit10k_word_list = Utility.load_word_list(mit10k_word_list_file_path)
dwyl_alpha_word_list = Utility.load_word_list(dwyl_alpha_word_list_file_path)
wordle_original_word_list = Utility.load_word_list(wordle_original_word_list_file_path)

all_correct_symbols = "+" * word_length


def benchmark_word_single_list(word:str):
    game = WordleGame(None, word_length)
    this_round = Round(hidden_word=word, guessed_times=0, success=False, final_solver="simple", tries=[])
    game.hidden_word = this_round.hidden_word
    solver = WordleSolver()
    solver.word_list = wordle_original_word_list
    if first_guess:
        guess = first_guess
    else:
        guess = solver.get_suggested_words()[0]
    while True:
        result_symbols = game.guess(guess)
        this_round.guessed_times += 1
        if result_symbols == all_correct_symbols:
            this_round.success = True
            break
        else:
            if this_round.guessed_times >= max_tries:
                break
            solver.input_guess_result(guess, result_symbols)
            suggested_words = solver.get_suggested_words()
            if len(suggested_words) <= 0:
                break
            guess = suggested_words[0]
    this_round.tries = solver.tries
    return this_round


def benchmark_word_autoswitch(word: str):
    game = WordleGame(None, word_length)
    this_round = Round(hidden_word=word, guessed_times=0, success=False, final_solver="simple", tries=[])
    game.hidden_word = this_round.hidden_word
    solver_simple = WordleSolver()
    solver_simple.word_list = mit10k_word_list
    solver_extended = WordleSolver()
    solver_extended.word_list = dwyl_alpha_word_list
    if first_guess:
        guess = first_guess
    else:
        guess = solver_simple.get_suggested_words()[0]
    while True:
        result_symbols = game.guess(guess)
        this_round.guessed_times += 1
        if result_symbols == all_correct_symbols:
            this_round.success = True
            break
        else:
            if this_round.guessed_times >= max_tries:
                break
            solver_simple.input_guess_result(guess, result_symbols)
            suggested_words = solver_simple.get_suggested_words()
            if len(suggested_words) <= 0:
                solver_extended.tries = solver_simple.tries
                solver_extended.update_pattern_paramters()
                suggested_words = solver_extended.get_suggested_words()
                this_round.final_solver = "extended"
            if len(suggested_words) <= 0:
                break
            guess = suggested_words[0]
    this_round.tries = solver_simple.tries
    return this_round


def do_benchmarking(file_path):
    chosen_word_list_file_path = file_path
    word_list = Utility.load_word_list(chosen_word_list_file_path)

    start_time = time.time()

    pool = Pool(multiprocessing.cpu_count())
    test_rounds = pool.map(benchmark_word_autoswitch, word_list)
    
    end_time = time.time()

    print(f"Benchmarking using {file_path} completed in {end_time - start_time}s")

    with open(f"{chosen_word_list_file_path.replace('.', '_')}_benchmark.json", "w") as file:
        file.write(json.dumps([round.__dict__ for round in test_rounds], indent=2))

    average = sum([round.guessed_times for round in test_rounds]) / len(test_rounds)

    print(f"{len(test_rounds)} words - average: {average} tries")

    failed_words = [round.hidden_word for round in test_rounds if not round.success]
    print(f"Guessing failed within {max_tries} tries: {len(failed_words)} words")


do_benchmarking(simple_word_list_file_path)

do_benchmarking(mit10k_word_list_file_path)

do_benchmarking(dwyl_alpha_word_list_file_path)
