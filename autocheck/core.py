from .cache import check_cache
from .notebook_state_tracker import notebook_state_tracker


def display_failure(result):
    print('⚠️ I could not check the answer because there was an error.\nI got this input\n')
    print(result['answer'])
    print()
    if result['answer'] in [..., None]:
        print("HINT: It looks like you didn't enter an answer.")
    elif type(result['answer']).__name__ in ['Xor', 'Not']:
        print("HINT: It looks like you need to use ** to raise to a power (and not ^).")


def display_correct(result):
    print('✅ Success!')


def display_incorrect(result, show_answer):
    if not result['unique']:
        print('😕 It looks like you tried that answer before. Please try again.')
    else:
        print('❌ This answer is incorrect. \nI got this input\n')
        print(result['answer'])
        if show_answer:
            print('\nbut was expecting this\n')
            print(result['expected'])
            print('\nPlease try again.')
        else:
            print('\nbut was expecting something else. Please try again.')


def _do_callback(callback, result):
    # Put a safety net around callbacks, print exception errors and return.
    try:
        callback(result)
    except:
        print(process_exception()['error'])


def process_result(
    result, show_answer=False, callback_failure=None, callback_correct=None,
    callback_incorrect=None
):
    # Push new IPython inputs and outputs to the tracker
    notebook_state_tracker.process_new_cells()
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
        if result['answer'] not in unique_attempts:
            result['unique'] = True
            unique_attempts.append(result['answer'])
        else:
            result['unique'] = False
        show_answer = show_answer and len(unique_attempts) > 1
        display_incorrect(result, show_answer)
        if callback_incorrect:
            _do_callback(callback_incorrect, result)
    # Push outcome of the response check to the tracker
    notebook_state_tracker.process_check_result(result)


def process_exception():
    import traceback
    # Using the line below instead of `traceback.print_exc(limit=0)`
    # since the Forum Python version (3.8.5) prints a traceback header
    # even if `limit=0` while newer versions (tested with 3.8.8) don't.
    return {
        'passed': False,
        'error': traceback.format_exc(limit=0).strip().split('\n')[-1]}


def check_function(func, answer, name=None, **kwargs):
    try:
        result = func(answer)
    except:
        result = process_exception()
    else:
        assert 'passed' in result
        assert 'expected' in result
    result['answer'] = answer
    if name is None:
        result['name'] = func.__name__
    else:
        result['name'] = name
    process_result(result, **kwargs)


def check_symbolic(expected, answer, name, **kwargs):
    # Compare two symbolic SymPy expressions and check that they are equal.
    from sympy import simplify
    try:
        result = {'passed': bool(simplify(answer - expected) == 0)}
    except:
        result = process_exception()
    result['answer'] = answer
    result['expected'] = expected
    result['name'] = name
    process_result(result, **kwargs)


def check_absolute_numeric(expected, answer, name, tolerance=0, **kwargs):
    # Numeric absolute error check: abs(answer - expected) <= tolerance.
    try:
        result = {'passed': bool(abs(answer - expected) <= tolerance)}
    except:
        result = process_exception()
    result['answer'] = answer
    result['expected'] = expected
    result['name'] = name
    process_result(result, **kwargs)


def check_relative_numeric(expected, answer, name, tolerance=1e-6, **kwargs):
    # Numeric relative error check: abs(answer/expected - 1) <= tolerance.
    try:
        result = {'passed': bool(abs(answer/expected - 1) <= tolerance)}
    except:
        result = process_exception()
    result['answer'] = answer
    result['expected'] = expected
    result['name'] = name
    process_result(result, **kwargs)
