import unittest
from unittest.mock import patch

from io import StringIO

from ..core import (
    display_failure, display_correct, display_incorrect,
    process_result,
    check_function, check_symbolic, check_absolute_numeric, check_relative_numeric,
    track,
)
from .. import notebook_state_tracker


class Tests(unittest.TestCase):

    def setUp(self):
        self.correct_output = '✅ Success!\n'
        self.incorrect_output = '❌ This answer is incorrect.\nI got this input\n\n{answer}\n\nbut was expecting something else. Please try again.\n'

    def test_callback_with_exception(self):
        '''Callback functions that raise exceptions are handled gracefully'''

        def callback(result):
            raise Exception("I made a whoopsie")

        # Patch sys.stdout to suppress output
        with patch('sys.stdout', new=StringIO()) as patched_out:
            # This should not raise an exception
            process_result({'passed': True}, callback_correct=callback)

    def test_empty_answer_output(self):
        '''Empty answers are detected and a hint is displayed'''

        for answer in [..., None]:
            # Patch sys.stdout to capture output
            with patch('sys.stdout', new=StringIO()) as patched_out:
                display_failure({'answer': answer})
                self.assertEqual(
                    patched_out.getvalue(),
                    '⚠️ I could not check the answer because there was an error.\n'
                    f'I got this input\n\n{answer}\n\n'
                    "⚠️ HINT: It looks like you didn't enter an answer.\n")

    def test_sympy_xor_output(self):
        '''SymPy xor (n^2) prompts a hint that you should use power (n**2) instead'''

        # Make an empty class with the same name as the SymPy class
        class Xor:
            pass
        answer = Xor()

        # Patch sys.stdout to capture output
        with patch('sys.stdout', new=StringIO()) as patched_out:
            display_failure({'answer': answer})
            self.assertEqual(
                patched_out.getvalue(),
                '⚠️ I could not check the answer because there was an error.\n'
                f'I got this input\n\n{answer}\n\n'
                "⚠️ HINT: It looks like you need to use ** to raise to a power (and not ^).\n")

    def test_check_function(self):
        '''Check a user response with a custom function'''

        def check_answer(answer):
            expected = 'the cat sat on the mat'
            return {
                'passed': answer == expected,
                'expected': expected}

        answer = 'the cat sat on the mat'
        with patch('sys.stdout', new=StringIO()) as patched_out:
            check_function(check_answer, answer)
            self.assertEqual(patched_out.getvalue(), self.correct_output)
        answer = 'the mat sat on the cat'
        with patch('sys.stdout', new=StringIO()) as patched_out:
            check_function(check_answer, answer)
            self.assertEqual(patched_out.getvalue(), self.incorrect_output.format(answer=answer))

    def test_check_symbolic(self):
        '''Check a SymPy user response'''
        from sympy.abc import n
        expected = n * (n - 1) / 2
        answer = (n ** 2 - n) / 2
        with patch('sys.stdout', new=StringIO()) as patched_out:
            check_symbolic(expected, answer)
            self.assertEqual(patched_out.getvalue(), self.correct_output)
        answer = n ** 2
        with patch('sys.stdout', new=StringIO()) as patched_out:
            check_symbolic(expected, answer)
            self.assertEqual(patched_out.getvalue(), self.incorrect_output.format(answer=answer))

    def test_check_absolute_numeric(self):
        '''Check a numeric user response with absolute error tolerance'''
        expected = 123
        answer = 123.1
        with patch('sys.stdout', new=StringIO()) as patched_out:
            check_absolute_numeric(expected, answer, tolerance=0.5)
            self.assertEqual(patched_out.getvalue(), self.correct_output)
        answer = 124
        with patch('sys.stdout', new=StringIO()) as patched_out:
            check_absolute_numeric(expected, answer, tolerance=0.5)
            self.assertEqual(patched_out.getvalue(), self.incorrect_output.format(answer=answer))

    def test_check_relative_numeric(self):
        '''Check a numeric user response with relative error tolerance'''
        expected = 1
        answer = 1.01
        with patch('sys.stdout', new=StringIO()) as patched_out:
            check_relative_numeric(expected, answer, tolerance=0.05)
            self.assertEqual(patched_out.getvalue(), self.correct_output)
        answer = 1.1
        with patch('sys.stdout', new=StringIO()) as patched_out:
            check_relative_numeric(expected, answer, tolerance=0.05)
            self.assertEqual(patched_out.getvalue(), self.incorrect_output.format(answer=answer))

    def test_course_and_problem_identifiers(self):
        '''Provide course, lesson plan, and other identifiers in a check call'''
        class RecordResult:
            def __call__(self, result):
                self.result = result
        with patch('sys.stdout', new=StringIO()) as patched_out:
            with patch(
                __name__ + '.notebook_state_tracker.notebook_state_tracker.process_check_result',
                new=RecordResult()
            ) as patched_call:
                check_absolute_numeric(
                    expected = 10,
                    answer = 10,
                    name = 'test_problem',
                    course = 'cs114', lp = 1, workbook = 'pcw')
                self.assertEqual(
                    patched_call.result,
                    {
                        'name': 'test_problem', 'course': 'cs114', 'lp': 1, 'workbook': 'pcw',
                        'passed': True, 'answer': 10, 'expected': 10})


    def test_track_vars(self):
        '''Provide tracking variables in a track call'''
        class RecordResult:
            def __call__(self, result):
                self.result = result
        with patch('sys.stdout', new=StringIO()) as patched_out:
            with patch(
                __name__ + '.notebook_state_tracker.notebook_state_tracker.process_check_result',
                new=RecordResult()
            ) as patched_call:
                track(
                    vars = {'test': 'vars', 0: 1},
                    name = 'test_problem',
                    course = 'cs114', lp = 1, workbook = 'pcw')
                self.assertEqual(
                    patched_call.result,
                    {
                        'name': 'test_problem', 'course': 'cs114', 'lp': 1, 'workbook': 'pcw',
                        'track_vars': {'test': 'vars', 0: 1}})

    def test_simplify_floats(self):
        '''Simplify mixtures of rational numbers and floats correctly'''
        import sympy
        from sympy.abc import n
        expected = sympy.Rational(2, 3) ** n  # rational numbers
        answer = (2 / 3) ** n  # floating point numbers
        with patch('sys.stdout', new=StringIO()) as patched_out:
            check_symbolic(expected, answer)
            self.assertEqual(patched_out.getvalue(), self.correct_output)
        answer = (0.6667) ** n
        with patch('sys.stdout', new=StringIO()) as patched_out:
            check_symbolic(expected, answer)
            self.assertEqual(patched_out.getvalue(), self.incorrect_output.format(answer=answer))

    def test_simplify_sqrts(self):
        '''Simplify square roots of powers of symbols by assuming the symbols are positive'''
        from sympy.abc import n
        from sympy import pi, sqrt
        expected = sqrt(2/pi/n)
        answer = 1/sqrt(pi*n/2)
        with patch('sys.stdout', new=StringIO()) as patched_out:
            check_symbolic(expected, answer)
            self.assertEqual(patched_out.getvalue(), self.correct_output)
