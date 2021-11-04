Resource Deduping
#################

String Matching Methods
***********************

* `Levenshtein Distance <https://en.wikipedia.org/wiki/Levenshtein_distance>`_: The number of insertions, deletions, or substitutions to change one string into another
* `Jaro Distance <https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance>`_: The number of transpositions to change one string into another
* `Jaro-Winkler Distance <https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance>`_: The number of transpositions to change one string into another with transpositions at the beginning counting as a greater change
* `Longest Common Subsequence (LCS) <https://en.wikipedia.org/wiki/Longest_common_subsequence_problem>`_: The number of single-character insertions and deletions to change one string into another
* `Smith-Waterman Algorithm <https://en.wikipedia.org/wiki/Smith%E2%80%93Waterman_algorithm>`_: A mathematical computation based on finding similar regions in two strings
* `Partial String Similarity <https://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/#partial-string-similarity>`_: Compares a shorter string to all possible substrings of the same length in a longer string
* `Token Sort Ratio <https://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/#token-sort>`_: Compares strings after alphabetizing the words in both strings
* `Token Set Ratio <https://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/#token-set>`_: Compares alphabetized strings against one another and the alphabetized set of words found in both strings, returning the closest of the three comparisons