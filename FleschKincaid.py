from curses.ascii import isdigit
from nltk.corpus import cmudict
import string
from string import digits


def comment_analyzer(comment_body):
    """
    Function that analyzes comment bodies to determine the Flesh-Kincaid
    reading level of the comment.
    We need to:

        1. Calculate the average number of words used per sentence
        2. Calculate the average number of syllables per word
        3. Multiply the average number of words by 0.39 and add it
           to the average number of syllables per word multiplied by
           11.8
        4. Subtract 15.59 from the result.

    :param comment_body: Actual text of the comment being analyzed.
    :return: 
    """
    syllable_count = 0
    word_count = 0
    sentence_count = 0

    for word in comment_body.split():
        try:
            remove_digits = str.maketrans('', '', digits)
            word = word.translate(remove_digits)  # Removes digits 1-9 from being checked
            # Once digits are stripped, they show up as ''.
            # This next line just says to ignore them if that's the case
            if word == '':
                continue
            endings_repeat = ["..", "??", "!!"]
            if any(i in word for i in
                   endings_repeat):  # In case someone is extremely excited or confused, we count this as one sentence.
                sentence_count += 1
            else:
                sentence_count += word.count(".")
                sentence_count += word.count("?")
                sentence_count += word.count("!")

            word_count += 1
            translator = str.maketrans('', '', string.punctuation)
            word = word.translate(translator)  # Removes punctuation from word
            syllable_list = nsyl(word)  # Flesh-Kincaid bit ( see nsyl() )
            syllable_count += syllable_list[0]
        except KeyError:
            pass

    if sentence_count == 0:
        sentence_count = 1
    try:
        #print("Sentences: " + str(sentence_count))
        average_words = word_count / sentence_count  # Average words used per sentence
        #print("Avg words: " + str(average_words))
        average_syllables = syllable_count / word_count  # Average syllables per word
        #print("Avg syllables: " + str(average_syllables))
        # All our step three stuff. ( See function details for more information )
        step_three_words = (average_words * .39)
        step_three_syllables = (average_syllables * 11.8)
        step_three_added = (step_three_words + step_three_syllables)
        # Find our final result, the round to the nearest integer.
        result = (step_three_added - 15.59)
        return int(round(result))
    except ZeroDivisionError as e:
        #print("Comment contained zero words. Continuing.")
        pass


d = cmudict.dict()


def nsyl(word):
    """
    The actual magic. Takes a word and makes use to the Natural Language Tool-Kit (nltk) 
    to count the syllables for the word. 
    DEPENDS ON A PRE-DETERMINED DICTIONARY OF ENGLISH LANGUAGE WORDS. IF THE WORD DOES NOT
    MATCH WORD ON THE LIST, THE WORD IS EXCLUDED FROM THE FINAL RESULTS.
    :param word: Word that needs to be checked.
    :return: 
    """
    return [len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]]

