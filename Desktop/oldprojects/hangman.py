import random

def hangman():
    word_list = ["python", "flask", "pandas", "numpy"]
    chosen_word = random.choice(word_list)
    guess = input("Guess the letter: " ).lower()

    display = []
    for _ in range(len(chosen_word)):
        display += ' '

    for position in range(len(chosen_word)):
        letter = chosen_word[position]
        if letter == guess:
            display[position] = letter
            print(display)

print(hangman())