'''
Core functions for checking student answers and providing feedback.
'''

from .cache import check_cache
from .notebook_state_tracker import notebook_state_tracker


def display_failure(result):
    '''
    Print a failure message to the standard output based on the type of error
    in `result`. This typically happens when an exception was raised.  Hints are
    provided if the student input was empty or contains a common error.
    '''
    print(
        '⚠️ I could not check the answer because there was an error.\n'
        'I got this input\n')
    print(result['answer'])
    print()
    if result['answer'] in [..., None]:
        print("⚠️ HINT: It looks like you didn't enter an answer.")
    elif type(result['answer']).__name__ in ['Xor', 'Not']:
        print(
            "⚠️ HINT: It looks like you need to use ** to raise to a power"
            " (and not ^).")


def display_correct(result):
    '''
    Print a success message to the standard output.
    '''
    print('✅ Success!')


def display_incorrect(result, show_answer):
    '''
    Print a failure message to the standard output if the student input was
    incorrect. Optionally, it displays the correct answer if `show_answer` is
    `True`.
    '''
    if result['unique']:
        message = '❌ This answer is incorrect.'
    else:
        message = '😕 It looks like you tried that answer before.'
    print(message)
    print('I got this input\n')
    print(result['answer'])
    if show_answer:
        print('\nbut was expecting this\n')
        print(result['expected'])
        print('\nPlease try again.')
    else:
        print('\nbut was expecting something else. Please try again.')


def _do_callback(callback, result):
    '''
    Put a safety net around user-provided callback functions, print exception
    error messages (if any) and return without interrupting execution.
    '''
    try:
        callback(result)
    except:
        print(process_exception()['error'])


def track(vars=None, name=None, course=None, lp=None, workbook=None):
    '''
    Push new IPython inputs and outputs to the tracker but don't take any other
    action. No student inputs are checked.

    This call will do nothing if `name` and `course` are not specified. The
    `lp` and `workbook` variables are optional.
    '''
    if (name is None) or (course is None):
        return
    notebook_state_tracker.process_new_cells()
    result = {
        'name': name,
        'course': course,
        'lp': lp,
        'workbook': workbook,
        'track_vars': vars}
    # Push outcome of the response check to the tracker
    notebook_state_tracker.process_check_result(result)


def process_result(
    result,
    show_answer=False,
    name=None, course=None, lp=None, workbook=None,
    callback_failure=None, callback_correct=None, callback_incorrect=None,
    enable_tracking=True,
):
    '''
    Generic function for processing student input _after_ it has be checked and
    marked as correct or incorrect. Never call this function directly. Use one
    of the check_* functions instead.

    Processing the marked input sends a message to the tracking (if enabled)
    server and prints a success/failure message to standard output.

    Even if tracking is enabled, this call will not send information to the
    tracking server unless `name` and `course` are specified.

    The user can provide callback functions for `correct` when the answer is
    correct, `incorrect` when the answer was incorrect, and `failure` for when
    an exception occurred. The `result` dictionary which contains the user
    and expected answers provided is passed as the only argument.
    '''

    # Allow tracking only if the course and question name are specified
    enable_tracking &= (name is not None) and (course is not None)
    # Push new IPython inputs and outputs to the tracker
    if enable_tracking:
        notebook_state_tracker.process_new_cells()
    # Record problem identifier
    result['name'] = name
    result['course'] = course
    result['lp'] = lp
    result['workbook'] = workbook
    # Handle the outcome of the response check
    if 'error' in result:
        print(result['error'])
        display_failure(result)
        if callback_failure:
            _do_callback(callback_failure, result)
    elif result['passed']:
        display_correct(result)
        if callback_correct:
            _do_callback(callback_correct, result)
    else:
        # Check that this response is not the same as earlier ones
        unique_attempts = check_cache.setdefault(result['name'], [])
        cache_result = str(result['answer'])
        if cache_result not in unique_attempts:
            result['unique'] = True
            unique_attempts.append(cache_result)
        else:
            result['unique'] = False
        show_answer = show_answer and len(unique_attempts) > 2
        display_incorrect(result, show_answer)
        if callback_incorrect:
            _do_callback(callback_incorrect, result)
    # Push outcome of the response check to the tracker
    if enable_tracking:
        notebook_state_tracker.process_check_result(result)


def process_exception():
    import traceback
    # Using the line below instead of `traceback.print_exc(limit=0)`
    # since the Forum Python version (3.8.5) prints a traceback header
    # even if `limit=0` while newer versions (tested with 3.8.8) don't.
    return {
        'passed': False,
        'error': traceback.format_exc(limit=0).strip().split('\n')[-1]}


def check_function(function, answer, **kwargs):
    '''
    Check a student input by calling a user-defined function. The function is
    expected to return a dictionary with at least the fields 'passed' and
    'expected'. The 'passed' field is of type bool, indicating whether the
    student input is correct. The 'expected' field is of any type and contains
    the correct (expected) answer to the question.

    Any additional fields present in the dictionary return by `function` will
    also be sent to the tracking server.
    '''
    try:
        result = function(answer)
    except:
        result = process_exception()
    else:
        assert 'passed' in result
        assert 'expected' in result
    result['answer'] = answer
    process_result(result, **kwargs)


def check_symbolic(expected, answer, **kwargs):
    '''
    Compare two symbolic SymPy expressions and check that they are equal.
    '''
    from sympy import simplify, powdenest
    try:
        result = {
        'passed': (
            bool(
                simplify(
                    powdenest(
                        answer - expected,
                        force=True),
                    rational=True, inverse=True) == 0)
            or bool(
                simplify(
                    powdenest(
                        answer / expected,
                        force=True),
                    rational=True, inverse=True) == 1))}
    except:
        result = process_exception()
    result['answer'] = answer
    result['expected'] = expected
    process_result(result, **kwargs)


def check_absolute_numeric(expected, answer, tolerance=0, **kwargs):
    '''
    Numeric absolute error check: abs(answer - expected) <= tolerance. The
    default tolerance is 0 which means the values have to match precisely.
    '''
    try:
        result = {'passed': bool(abs(answer - expected) <= tolerance)}
    except:
        result = process_exception()
    result['answer'] = answer
    result['expected'] = expected
    process_result(result, **kwargs)


def check_relative_numeric(expected, answer, tolerance=1e-6, **kwargs):
    '''
    Numeric relative error check: abs(answer/expected - 1) <= tolerance.
    '''
    try:
        result = {'passed': bool(abs(answer/expected - 1) <= tolerance)}
    except:
        result = process_exception()
    result['answer'] = answer
    result['expected'] = expected
    process_result(result, **kwargs)
