#!/usr/bin/env python3

from dataclasses import dataclass
from typing import List
import json
import multiprocessing
from multiprocessing import Pool
import time
import random
import sys


from wordle_game import WordleGame
from wordle_solver import WorldSolverMultiList
from utility import Utility


@dataclass
class Round:
    hidden_word: str
    guessed_times: int
    success: bool
    final_solver: str
    tries: List

word_length = 5
max_tries = 6 # sys.maxsize
exclude_plurals = True
logging_enabled = False
first_guess = None
enabled_multithreading = True

all_correct_symbols = "+" * word_length

opener_word_list_file_path = "english_words_opener.txt"
full_word_list_file_path = "english_words_full.txt"
wordle_original_word_list_file_path = "english_words_original_wordle.txt"

word_list = []

opener_word_list = Utility.load_word_list(opener_word_list_file_path, word_length, exclude_plurals)
full_word_list = Utility.load_word_list(full_word_list_file_path, word_length, exclude_plurals)


multi_solver_word_lists = [opener_word_list, full_word_list]
multi_solver_word_list_paths = [opener_word_list_file_path, full_word_list_file_path]
max_try_indexes_for_lists = [2, sys.maxsize]


def benchmark(word: str):
    game = WordleGame(None, word_length)
    this_round = Round(hidden_word=word, guessed_times=0, success=False, final_solver="simple", tries=[])
    game.hidden_word = this_round.hidden_word
    solver_multi = WorldSolverMultiList()
    solver_multi.word_length = word_length
    solver_multi.word_lists = multi_solver_word_lists
    solver_multi.word_list_file_paths = multi_solver_word_list_paths
    solver_multi.max_try_indexes_for_lists = max_try_indexes_for_lists
    solver_multi.word_entropies = {}
    solver_multi.reset()
    if first_guess:
        guess = first_guess
    else:
        guess = solver_multi.get_suggested_words().words[0]
    while True:
        result_symbols = game.guess(guess)
        this_round.guessed_times += 1
        if result_symbols == all_correct_symbols:
            this_round.success = True
            break
        else:
            if this_round.guessed_times >= max_tries:
                break
            solver_multi.input_guess_result(guess, result_symbols)
            suggested_words_result = solver_multi.get_suggested_words()
            suggested_words = suggested_words_result.words
            this_round.final_solver = suggested_words_result.word_list_file_path
            if len(suggested_words) <= 0:
                break
            guess = suggested_words[0]
    this_round.tries = solver_multi.tries
    return this_round


def do_benchmarking(file_path, n_samples:int=1000):
    chosen_word_list_file_path = file_path
    word_list = Utility.load_word_list(chosen_word_list_file_path, word_length, exclude_plurals)
    random.shuffle(word_list)

    start_time = time.time()

    if n_samples:
        if n_samples > 0:
            word_list = word_list[:n_samples]

    test_rounds = []

    if enabled_multithreading:
        pool = Pool(multiprocessing.cpu_count())
        test_rounds = pool.map(benchmark, word_list)
    else:
        test_rounds = list([benchmark(word) for word in word_list])
    
    end_time = time.time()

    print(f"Benchmarking using {'all' if n_samples is None else n_samples} words of {word_length} letters ({'no' if exclude_plurals else 'with'} plurals) from {file_path} completed in {end_time - start_time}s")

    print("Solver word lists: " + " -> ".join(multi_solver_word_list_paths))

    if logging_enabled:
        with open(f"benchmark_results_{chosen_word_list_file_path.replace('.', '_')}.json", "w") as file:
            file.write(json.dumps([round.__dict__ for round in test_rounds], indent=2))

    average = sum([round.guessed_times for round in test_rounds]) / len(test_rounds)

    print(f"{len(test_rounds)} words - average: {average} tries")

    failed_words = [round.hidden_word for round in test_rounds if not round.success]
    print(f"Guessing failed within {max_tries} tries: {len(failed_words)} words")


do_benchmarking(wordle_original_word_list_file_path)

do_benchmarking(full_word_list_file_path)
