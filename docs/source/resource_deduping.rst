Resource Deduping
#################

String Matching Methods
***********************

* Levenshtein: The number of insertions, deletions, or substitutions to change one string into another (https://en.wikipedia.org/wiki/Levenshtein_distance)
* Jaro: The number of transpositions to change one string into another (https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance)
* Jaro-Winkler: The number of transpositions to change one string into another with transpositions at the beginning counting as a greater change (https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance)
* LCS: The number of single-character insertions and deletions to change one string into another (https://en.wikipedia.org/wiki/Longest_common_subsequence_problem)
* Smith-Waterman: https://en.wikipedia.org/wiki/Smith%E2%80%93Waterman_algorithm