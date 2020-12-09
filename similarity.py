from typing import List, Set, Union


def jaccard(s1: Union[str, set], s2: Union[str, set]) -> float:
    '''
    如果输入是字符串，默认是char level
    >>> jaccard('', '')
    1.0
    >>> jaccard('jaccard', '')
    0.0
    >>> jaccard('jaccard', 'jacard')
    1.0
    >>> 
    '''
    if not s1 and not s2:
        return 1.0
    if not isinstance(s1, set):
        s1 = set(s1)
    if not isinstance(s2, set):
        s2 = set(s2)
    return len(s1 & s2)/(len(s1 | s2) + 1e-8)


def editdistance(s1: Union[str, List], s2: Union[str, List]) -> int:
    '''
    >>> editdistance('', '')
    (0, 1.0)
    >>> editdistance('a', 'b')
    (1, 0.0)
    >>> editdistance('jaccard', '')
    (7, 0.0)
    >>> editdistance('jaccard', 'jacard')
    (1, 0.8571428571428572)
    '''
    if s1 == s2:
        return 0, 1.0
    edit, ratio = 0, 0
    if not (s1 and s2):
        edit = len(s1) if s1 else len(s2)
        ratio = 1 - edit/max(len(s1), len(s2))
        return edit, ratio
    dp = [[0 for j in range(len(s2)+1)] for i in range(len(s1)+1)]
    for i in range(len(s1)):
        dp[i][0] = i
    for j in range(len(s2)):
        dp[0][j] = j
    for i in range(1, len(s1)+1):
        for j in range(1, len(s2)+1):
            dp[i][j] = min(
                dp[i-1][j-1]+(0 if s1[i-1] == s2[j-1] else 1),
                dp[i][j-1]+1,
                dp[i-1][j]+1,
            )
    edit = dp[len(s1)][len(s2)]
    ratio = 1 - edit/max(len(s1), len(s2))
    return edit, ratio
