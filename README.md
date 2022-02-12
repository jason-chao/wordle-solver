# Wordle-Solver
Wordle-Solver helps people who struggle with vocabulary enjoy the famous game of [WORDLE](https://www.powerlanguage.co.uk/wordle/).  So that those who find WORDLE extremely hard, just like the developer of Wordle-Solver, will not be embarrassed for not knowing the hidden word of the day or being unable to show their tries.

Wordle-Solver is positioned as a solver for the WORDLE game in general. Wordle-Solver supports a variable word length and works with other implementations of WORDLE. Therefore, it relies on a broader word list and does not target that of the original implementation of WORDLE. 

## Web-based version

A web-based interface for Wordle-Solver is now available at [https://solvewordle.games/](https://solvewordle.games/).  There is no need to run the Python code in this repo to try out Wordle-Solver.

![Screenshot of Wordle-Solver web-based UI](wordle_solver_webui_screenshot.png)

## How does Wordle-Solver work?

Based on probability, Wordle-Solver helps WORDLE players find the best words for the next try.  Wordle-Solver uses every bit of information gained from WORDLE’s responses to build the search criteria.  The responses from the tries will help Wordle-Solver narrow down to a single, if not a few, possible English word(s).

Usually, in the first two or three tries, the list of possible words may still be quite long.  Wordle-Solver works out the probabilities of letters with unknown inclusion/exclusion status and suggests words with letters of higher frequencies.  It does not matter whether or not these high-frequency letters end up in the hidden word.   WORDLE’s responses to these high-frequency letters will help Wordle-Solver shrink the search space efficiently.

The developer of Wordle-Solver experimented with a number of other approaches.  He found that the approach now implemented in the Wordle-Solver would produce the best results given the limited he has on this mini-project.

## How does Wordle-Solver perform?

Although Wordle-Solver does not specifically target the original WORDLE, it is common to benchmark the performance based on the original WORDLE's word list.  Wordle-Solver takes an average of 4.6 tries to pinpoint a hidden word chosen from the original WORDLE's word list (with plurals excluded).  The game is solved within the limit of 6 tries 90.6% of the time.

For multi-word length challenge, Wordle-Solver takes an average of [3.55 tries](https://botfights.ai/fight/xm7fenzq) to win when the number of tries is not capped.

## Usage of the command-line version

For general users, the use of [the web-based interface](https://solvewordle.games/) is highly recommended.

Follow the steps below if you wish to explore Wordle-Solver at a technical level.

Download Wordle-Solver by cloning this repo. 
```
git clone https://github.com/jason-chao/wordle-solver.git
```

### Run the Wordle-Solver
```
cd wordle-solver
python3 wordle_solver.py
```

### Open WORDLE
Enter a word into WORDLE.  
![Sample WORDLE response to OPERA](wordle_response_example.png)

### Enter WORDLE’s response into Wordle-Solver
When WORDLE tells you the result of the first try, enter the word and WORDLE’s response using the symbols indicated below into Wordle-Solver.   For the time being, Wordle-Solver is only available as a command-line (CLI) application.  Since command-line applications cannot easily handle colours, players need to map the colours of WORDLE’s letter tiles to the following symbols.

* Use _ for ⬜ indicating a letter not in the hidden word in any spot
* Use ?  for 🟨 indicating a letter in the hidden word but in the wrong spot
* Use + for 🟩 indicating a letter in the hidden word and in the correct spot

You should enter the result into Wordle-Solver in the format of word:symbols (the word, a colon `:` and the symbols).  For example, for the screenshot above as an example, the input into Wordle-Solver should look like `opera:_?+?_`.

```
Please enter you last try as word:symbols
opera:_?+?_
Suggested words (from simple word list):
        press
```

Pick a suggested word shown by Wordle-Solver.  Enter it into WORDLE.  Repeat this step until Wordle-Solver finds the hidden word for you.

## Tips
The WORDLE game only accepts on its own word list on every try.  There is a possibility that WORDLE rejects all the words suggested by Wordle-Solver.  In this case, enter the command `!extended` into Wordle-Solver to manually switch to the extended word list.  Then, Wordle-Solver will begin to suggest words from the extended word list.

Wordle-Solver uses two lists of English words.  One is called “simple” and the other one is called “extended”.  The “extended” list has about 11 times more words than the simple list.  As one can imagine, the extended list contains many rarely used English words.  By default, Wordle-Solver searches for words on the “simple” list only.  When no suggestions could be made from the “simple” list, Wordle-Solver will switch to the “extended” list to broaden the search.  Except in the case mentioned case, the switch is usually automatic.  

## Credits
The “simple” word list is derived from [MIT’s 10000-word list](https://www.mit.edu/~ecprice/wordlist.10000).  The “extended” and "full" word lists are derived from the [alpha variant](https://github.com/dwyl/english-words/blob/master/words_alpha.txt) of [dwyl’s “List of English Words”](https://github.com/dwyl/english-words). 
