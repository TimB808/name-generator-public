import random

SINGLE_CONSONANTS = ["b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "w", "x", "y", "z"]
CONSONANT_BLENDS = ["bl", "ch", "sh", "ph", "st", "tr", "cl", "fl", "gl", "pl", "sl", "br", "dr", "fr", "gr", "pr", "sk", "sm", "sn", "sp"]
VOWELS = ["a", "e", "i", "o", "u", "y"]
END_EXCLUDED_BLENDS = ["bl", "tr", "cl", "fl", "gl", "pl", "sl", "br", "dr", "fr", "gr", "pr", "sn", "sp"]

ALL_CONSONANTS = SINGLE_CONSONANTS + CONSONANT_BLENDS

def generate_name(length=None, first_letter=None):
    length = length or random.choices([3, 4, 5, 6, 7, 8], weights=[1, 3, 3, 3, 2, 1], k=1)[0]

    name = ""
    i = 0

    if first_letter:
        if first_letter.lower() in SINGLE_CONSONANTS + CONSONANT_BLENDS + VOWELS:
            name += first_letter.lower()
            i += len(first_letter)
        else:
            print("Invalid first letter. Using random choice.")
            name += random.choice(ALL_CONSONANTS + VOWELS)
            i += len(name) #added this to update i
    else:
        name += random.choice(ALL_CONSONANTS + VOWELS)
        i += len(name) #added this to update i

    while i < length:
        if name[-1] in VOWELS:
            available_consonants = ALL_CONSONANTS if i < length - 2 else SINGLE_CONSONANTS
            consonant_choice = random.choice(available_consonants)
            name += consonant_choice
            i += len(consonant_choice)
        else:
            name += random.choice(VOWELS)
            i += 1

    return name.capitalize()
