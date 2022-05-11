'''
This example shows how to define your own function to check a student input.
This can be useful for checking unusual data types or in cases where multiple
answers are acceptable.
'''
import autocheck

# Below is the user-defined function. Here, the student can provide strings in
# upper or lower case and in any order in a Python list. We convert the list to
# a set to do a check that doesn't care about the order of the items. This is
# useful for a question like "Identify all the nodes in this graph that have a
# degree of exactly 3" where the nodes are labeled with letters.

def check_answer(answer):
    # The student answer is the only input to this function
    expected = ['A', 'E', 'I', 'O', 'U']
    # Do the check
    passed = set(string.upper() for string in answer) == set(expected)
    # You have to return a Boolean in 'passed' and the expected response in
    # 'expected' below. The library uses that to provide feedback to the
    # student. Any additional fields included below are not used directly by
    # the library but will get sent to the tracking server.
    return {
        'passed': passed,
        'expected': expected}


# This prints out the success message.
print('\n————————\n📋 TEST: Check with a user-defined function\n————————\n')
answer = ['a', 'U', 'I', 'o', 'E']
autocheck.check_function(
    name = 'test_function',
    function = check_answer,
    answer=answer)
