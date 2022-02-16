#!/usr/bin/env python3

import argparse
import string
import random
from utility import Utility

class WordleGame:

    def __init__(self, word_list_file_path: str = None, word_length : int = 5, exclude_plurals:bool=True):
        self.word_list = []
        self.hidden_word = None
        self.word_list_file_path = word_list_file_path
        self.word_length = word_length
        self.exclude_plurals = exclude_plurals
        if self.word_list_file_path is not None:
            self.word_list = Utility.load_word_list(self.word_list_file_path, self.word_length, self.exclude_plurals)

    def are_characters_valid(self, word) -> bool:
        if len(word) != self.word_length:
            return False
        for character in word:
            if character not in string.ascii_lowercase:
                return False
        return True
        
    def pick_a_hidden_word_randomly(self):
        if len(self.word_list) <= 0:
            raise Exception("The word list is empty")
        hidden_word_index = random.randrange(0, len(self.word_list))
        self.hidden_word  = self.word_list[hidden_word_index]


    def guess(self, guessed_word) -> str:
        if not self.hidden_word:
            self.pick_a_hidden_word_randomly()
        
        if not self.are_characters_valid(guessed_word):
            raise Exception("Invalid input")
        
        guessed_word_letters = [letter for letter in guessed_word]
        output_symbols = ["!"] * self.word_length
        hidden_word_letters = [letter for letter in self.hidden_word]

        for i in range(0, self.word_length):
            if guessed_word_letters[i] == hidden_word_letters[i]:
                output_symbols[i] = "+"
                hidden_word_letters[i] = " "

        for i in range(0, self.word_length):
            if output_symbols[i] != "!":
                continue
            if guessed_word_letters[i] in hidden_word_letters:
                letter_index_in_hidden_word = hidden_word_letters.index(guessed_word_letters[i])
                hidden_word_letters[letter_index_in_hidden_word] = " "
                output_symbols[i] = "?"
            else:
                output_symbols[i] = "_"
                    
        if "!" in output_symbols:
            raise Exception(f"Error in generating output symbols for {guessed_word} (hidden: {self.hidden_word}): {''.join(output_symbols)}")

        return "".join(output_symbols)


if __name__ == "__main__":


    argParser = argparse.ArgumentParser()

    argParser.add_argument("--length", help="The length (number of letters) of the hidden word", required=False, default=5, type=int)
    argParser.add_argument("--plurals", help="Do not exclude plurals when loading from the word list", required=False, default=False, type=bool)
    argParser.add_argument("--maxguess", help="The number of guesses allowed", required=False, default=6, type=int)

    args = argParser.parse_args()

    wordle = WordleGame("english_words_10k_mit.txt", args.length, not args.plurals)

    correct_guess_output = "+" * wordle.word_length
    max_guess = args.maxguess

    print("The WORDLE game CLI")
    print(f"(Word length: {wordle.word_length}; Plurals: {'Yes' if not wordle.exclude_plurals else 'No'}; Max guesses: {max_guess})")
    print("Press CTRL+C to exit\n")
    print("Meanings of symbols:")
    print(" +\tletter in the word and in the right spot")
    print(" ?\tletter in the word but in a wrong spot")
    print(" _\tletter not in the word\n")

    guess = 0

    while True:
        print(f"Guess the hidden word of {wordle.word_length} letters")
        user_input = input()
        if not wordle.are_characters_valid(user_input):
            print("Sorry, your input is invalid.")
            continue
        if user_input not in wordle.word_list:
            print("Sorry, your input is not on the word list")
            continue
        output = wordle.guess(user_input)
        reset = False
        guess += 1
        if output == correct_guess_output:
            print(f"Congrats, your guess is correct: {wordle.hidden_word} ({guess}/{max_guess})")
            reset = True
        else:
            if guess >= max_guess:
                print(f"Sorry, the hidden word is: {wordle.hidden_word}")
                reset = True
            else:
                print(output + f" ({guess}/{max_guess})")

        if reset:
            wordle.pick_a_hidden_word_randomly()
            print("A new hidden word has been picked")
            guess = 0
