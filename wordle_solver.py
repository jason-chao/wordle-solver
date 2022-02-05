#!/usr/bin/env python3

import string
from utility import Utility
import random

class WordleSolver():

    def __init__(self, word_list_file_path: str = None, word_length : int = 5, exclude_plurals:bool=True):
        self.permitted_input_symbols = "+?_"
        self.word_list = []
        self.symbol_anyletter = "*"
        self.word_list_file_path = word_list_file_path
        self.word_length = word_length
        self.exclude_plurals = exclude_plurals
        if self.word_list_file_path is not None:
            self.word_list = Utility.load_word_list(self.word_list_file_path, word_length, self.exclude_plurals)
        self.reset()

    def reset(self):
        self.tries = []
        self.reset_pattern_parameters()

    def reset_pattern_parameters(self):
        self.included_letters = ""
        self.excluded_letters = ""
        self.high_prob_letters = ""
        self.wrong_spot_pattern = [""] * self.word_length
        self.right_spot_pattern = self.symbol_anyletter * self.word_length
        self.max_letter_occurrence = {}


    def get_pattern_parameter_conflicts(self):
        conflicts = []
        for letter in self.excluded_letters:
            if letter in self.included_letters + self.high_prob_letters:
                conflicts.append((letter, "excluded letter found in inclusion list"))
            if letter in self.right_spot_pattern:
                conflicts.append((letter, "excluded letter found in right spot pattern"))
        for i in range(0, self.word_length):
            if self.right_spot_pattern[i] in self.wrong_spot_pattern[i]:
                conflicts.append((letter, "letter in right spot found in wrong spot pattern"))
        return conflicts
    

    def update_pattern_paramters(self):
        self.reset_pattern_parameters()
        for (word, symbol_pattern) in self.tries:
            for i in range(0, self.word_length):
                if symbol_pattern[i] in ["+", "?"]:
                    self.included_letters += word[i]
                    if symbol_pattern[i] == "+":
                        right_spot_pattern_list = list(self.right_spot_pattern)
                        right_spot_pattern_list[i] = word[i]
                        self.right_spot_pattern = "".join(right_spot_pattern_list)
                    elif symbol_pattern[i] == "?":
                        self.wrong_spot_pattern[i] += word[i]
                elif symbol_pattern[i] == "_":
                    if word[i] not in self.included_letters:
                        self.excluded_letters += word[i]
                    else:
                       if word[i] not in self.max_letter_occurrence:
                           self.max_letter_occurrence[word[i]] = sum([1 for letter in word[:i] if letter == word[i]]) + sum([1 for letter in word[(i+1):] if letter == word[i]])
        self.included_letters = "".join(set(self.included_letters))
        self.excluded_letters = "".join(set([letter for letter in self.excluded_letters if letter not in self.included_letters]))
        self.wrong_spot_pattern = ["".join(set(pattern)) for pattern in self.wrong_spot_pattern]


    def get_letter_prob_dict(self, word_list):

        if len(word_list) <= 0:
            return []

        letter_freq_dict = {}
        for letter in string.ascii_lowercase:
            letter_freq_dict[letter] = 0

        for word in word_list:
            for letter in word:
                letter_freq_dict[letter] += 1

        letter_prob_dict = {}
        total_letters = sum([len(word) for word in word_list])

        for letter in letter_freq_dict.keys():
            letter_prob_dict[letter] = (letter_freq_dict[letter] / total_letters)

        return letter_prob_dict


    def get_suggested_letters_by_freq(self, possible_words):
        if len(possible_words) <= 0:
            return []
        letter_freqs = [(letter, prob) for index, (letter, prob) in enumerate(self.get_letter_prob_dict(possible_words).items()) if letter not in self.included_letters + self.excluded_letters + self.high_prob_letters]
        return letter_freqs


    def get_letter_positional_prob_dict(self, words):
        positional_prob = []
        for i in range(0, len(self.right_spot_pattern)):
            if self.right_spot_pattern[i] == self.symbol_anyletter:
                letter_list = [word[i] for word in words]
                positional_prob.append(self.get_letter_prob_dict(letter_list))
            else:
                positional_prob.append({})
        return positional_prob


    def sort_words_with_letter_positional_prob(self, words):
        letter_position_prob = self.get_letter_positional_prob_dict(words)
        words_with_prob = []
        for word in words:
            score = 1
            for i in range(0, len(letter_position_prob)):
                if letter_position_prob[i]:
                    score *= letter_position_prob[i][word[i]]
            words_with_prob.append((word, score))
        words_with_prob.sort(key=lambda element: element[1], reverse=True)
        return [word_with_prob[0] for word_with_prob in words_with_prob]


    def is_not_in_word(self, word):
        return all([letter not in word for letter in self.excluded_letters])

    def is_in_word(self, word):
        return all([letter in word for letter in self.included_letters + self.high_prob_letters])

    def is_not_tried(self, word):
        return word not in self.tries

    def match_right_spot_pattern(self, word):
        for i in range(0, len(self.right_spot_pattern)):
            if self.right_spot_pattern[i] == self.symbol_anyletter:
                continue
            elif self.right_spot_pattern[i] != word[i]:
                return False
        return True
    

    def get_possible_words(self):
        all_tried_words = [attempt[0] for attempt in self.tries]
        first_level_filter = [word for word in self.word_list if self.is_in_word(word) and self.is_not_in_word(word) and self.is_not_tried(word) and word not in all_tried_words]
        second_level_filter = [word for word in first_level_filter if all([word[i] not in self.wrong_spot_pattern[i] for i in range(0, self.word_length)])]
        third_level_filter = [word for word in second_level_filter if self.match_right_spot_pattern(word)]
        if len(self.max_letter_occurrence) <= 0:
            return third_level_filter
        else:
            for letter in self.max_letter_occurrence.keys():
                fourth_level_filter = [word for word in third_level_filter if sum([1 for l in word if l == letter]) <= self.max_letter_occurrence[letter]]
            return fourth_level_filter


    def get_suggested_words(self):
        all_possible_words = self.get_possible_words()
        if len(all_possible_words) <= 0:
            return []
        unknown_letter_count = self.word_length - len(self.included_letters)
        suggested_letters_with_prob = self.get_suggested_letters_by_freq(all_possible_words)
        if len(suggested_letters_with_prob) <= 0:
            return []
        suggested_letters_with_prob.sort(key=lambda element: element[1], reverse=True)
        suggested_letters = list([letter for (letter, prob) in suggested_letters_with_prob])
        for i in range(unknown_letter_count, 0, -1):
            self.high_prob_letters = suggested_letters[:i]
            self.update_pattern_paramters()
            suggested_words = self.get_possible_words()
            self.high_prob_letters = ""
            if len(suggested_words) > 0:
                suggested_words = self.sort_words_with_letter_positional_prob(suggested_words)
                return suggested_words
        all_possible_words = self.sort_words_with_letter_positional_prob(all_possible_words)
        return all_possible_words


    def input_guess_result(self, word, result_symbols):
        if len(word) != self.word_length or len(result_symbols) != self.word_length:
            raise Exception("Word length or symbol length is invalid")
        if not all([character in string.ascii_lowercase for character in word]):
            raise Exception("Word contains invalid character")
        if not all([symbol in self.permitted_input_symbols for symbol in result_symbols]):
            raise Exception("Symbols contains an invalid symbol")
        self.tries.append((word, result_symbols))
        self.update_pattern_paramters()


if __name__ == "__main__":

    solver_simple = WordleSolver("english_words_simple.txt")

    solver_extended = WordleSolver("english_words_alpha_dwyl.txt")

    print("The WORDLE Solver CLI")
    print("Press CTRL+C to exit\n")
    print("Meanings of symbols:")
    print(" +\tletter in the word and in the right spot (green box)")
    print(" ?\tletter in the word but in a wrong spot (orange box)")
    print(" _\tletter not in the word (grey box)\n")
    print("Commands:")
    print(" !done\t\tyou're done guessing a hidden word.  this will reset the state of the solver for you to guess a new hidden word")
    print(" !extended\tuse the extended word list if all suggested words shown are not accepted")
    print(" !tries\t\tsee the tries entered")
    print(" !remove_last\tremove the last try entered\n")

    print("Tips: This Solver recommends entering 'opera' as the first word.\n\n")

    use_extended_solver = False

    while True:
        print("Please enter you last try as word:symbols")
        user_input = input().lower()

        reset = False

        if ":" in user_input:
            values = user_input.split(":")
            if len(values) < 2:
                print("Invalid format")
                continue
            if not all([len(value) == solver_simple.word_length for value in values]):
                print("Invalid format: length of word or symbol is incorrect")
                continue
            if values[1] == "+" * solver_simple.word_length:
                print("Great!")
                reset = True
            else:
                solver_simple.input_guess_result(values[0], values[1])
                conflicts = solver_simple.get_pattern_parameter_conflicts()
                if len(conflicts) > 0:
                    for conflict in conflicts:
                        print(f"{conflict[0]}: {conflict[1]}")
                    solver_simple.tries = solver_simple.tries[:-1]
                    print("Your last try has been removed")
                    continue
        elif (user_input == "!done"):
            reset = True
        elif (user_input in "!extended"):
            use_extended_solver = True
            print("You are now using an extended word list")
        elif (user_input == "!remove_last"):
                solver_simple.tries = solver_simple.tries[:-1]
                print("Your last try has been removed")
                continue
        elif (user_input == "!tries"):
            if len(solver_simple.tries) <= 0:
                print("No tries entered")
            else:
                for i in range(0, len(solver_simple.tries)):
                    print(f"\tTry {i}: {solver_simple.tries[i]}")
            continue
        else:
            print("Invalid input")


        if reset:
            solver_simple.tries = []
            use_extended_solver = False
            print("The state is reset")
            continue

        suggested_words = solver_simple.get_suggested_words()
        if use_extended_solver or len(suggested_words) <= 0:
            solver_extended.tries = solver_simple.tries
            solver_extended.update_pattern_paramters()
            suggested_words = solver_extended.get_suggested_words()
            use_extended_solver = True
        if len(suggested_words) > 0:
            print(f"Suggested words (from {'simple' if not use_extended_solver else 'extended'} word list):")
            for suggestion in suggested_words[:10]:
                print(f"\t{suggestion}")
        else:
            print("Sorry, no other possible words.  Please check the result symbols you entered.")
