'''
This example shows how autocheck handles student inputs that incorrectly use
`^` instead of `**` to write "to the power of" in mathematical expressions. This
is a common error in SymPy, especially if the user is used to Matlab or Sage.
'''
import autocheck
import sympy
from sympy.abc import n

expected = n*(n+1)

# This prints out a hint, "It looks like you need to use ** to raise to a power
# (and not ^)."
print('\n————————\n📋 TEST: Incorrectly use ^\n————————\n')
answer = n^2 + n
autocheck.check_symbolic(name='test_exponent', expected=expected, answer=answer)


# This prints out the success message.
print('\n————————\n📋 TEST: Correct input\n————————\n')
answer = n**2 + n
autocheck.check_symbolic(name='test_exponent', expected=expected, answer=answer)
