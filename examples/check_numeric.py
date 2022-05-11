'''
This example shows how to test numeric expressions. Answers can be precise or
accepted as correct if they are equal up to a user-defined absolute or relative
tolerance.
'''
import autocheck
import math

expected = 3.14159
answer = math.pi

# When using check_absolute_numeric, the default tolerance is 0 requiring
# answers with perfect numeric precision. In practice, this means up to
# floating-point error which is approximately 1e-16.
print('\n————————\n📋 TEST: Perfect precision required\n————————\n')
autocheck.check_absolute_numeric(
    name = 'test_numeric_1',
    expected = expected,
    answer = answer)


# Absolute numeric checks require abs(expected-answer) ≤ tolerance.
print('\n————————\n📋 TEST: Allow 1e-6 absolute error\n————————\n')
autocheck.check_absolute_numeric(
    name = 'test_numeric_2',
    expected = expected,
    tolerance = 1e-6,
    answer = answer)


# Relative numeric checks require abs((expected-answer)/expected) ≤ tolerance.
print('\n————————\n📋 TEST: Allow 1e-6 relative error\n————————\n')
autocheck.check_relative_numeric(
    name = 'test_numeric_3',
    expected = expected,
    tolerance = 1e-6,
    answer = answer)
