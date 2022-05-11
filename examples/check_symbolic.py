'''
This example shows how to test symbolic expressions using SymPy. The check
function automatically simplifies the student and expected answers to see if
they are equivalent.
'''
import autocheck


import sympy
from sympy.abc import x

print('\n————————\n📋 TEST: Compare polynomials and square roots\n————————\n')
expected = sympy.sqrt((x - 1) * (x + 1))
answer = (x**2 - 1) ** 0.5
print('Expected:', expected)
print('Answer:  ', answer)
autocheck.check_symbolic(
    name = 'test_symbolic_1',
    expected = expected,
    answer = answer)


print('\n————————\n📋 TEST: Compare functions\n————————\n')
Phi = sympy.Function('ϕ')
mu = sympy.Symbol('μ')
sigma = sympy.Symbol('σ')
expected = Phi((x - mu) / sigma)
answer = Phi(x/sigma - mu/sigma)
print('Expected:', expected)
print('Answer:  ', answer)
autocheck.check_symbolic(
    name = 'test_symbolic_2',
    expected = expected,
    answer = answer)
