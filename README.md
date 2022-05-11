# autocheck

Library for automatically checking/grading student responses in Forum Code
Workbooks.

## Overview

We support automatic grading of students' mathematical and numerical responses
in Forum Workbooks in order to provide immediate automated feedback. Optionally,
student responses are also sent to a tracking server so that real-time reports
can be generated on the number of exercises attempted by each student and the
number of correct or incorrect responses grouped by question item. All tracking
is automatically anonymized since no identifying information is available in
Forum Workbooks.

## Installation

To use the library in an IPython environment (including Jupyter notebooks and
Forum Workbooks), install and import the autocheck library using the code below.
This code will automatically install the library if it is not already installed
and import it if it is not already imported. The code is structured such that
installation happens at most once (downloading and installing the package is
relatively slow and will require a few seconds) and only imports it when it is
not already present, to keep the time overhead as low as possible.

```python
try:
    autocheck  # Already imported?
except NameError:
    try:
        import autocheck  # Already installed?
    except:
        import sys, subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'https://github.com/minerva-university/autocheck/releases/latest/download/autocheck-latest-py3-none-any.whl'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import autocheck
    # Optional: disable tracking globally
    # autocheck.notebook_state_tracker.notebook_state_tracker.tracking = False
```

## Example

Once the library is installed, a student response stored in a variable called
`answer` is checked using a function call like this one:

```python
from sympy.abc import n
autocheck.check_symbolic(
    name = 'question name',
    expected = n * (n - 1) / 2,
    answer = globals().get('answer'))
```

The unique name af a question item (unique in the scope of the current workbook)
is provided along with the expected (correct) answer and the student's answer.

For more examples, see the `examples/` directory.

## Development

To develop, test, or build this package, install the development environment.

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements_dev.txt
```

To run tests:

```bash
./test.sh
```

To build the package:

* First, make sure `setup.cfg` and `autocheck/__init__.py` contain the new
  version number.
* Run the build with `./build.sh`
* Copy the new wheel in `dist/autocheck-x.y.z-py3-none-any.whl` to
  `dist/autocheck-latest-py3-none-any.whl`
* Create a new release on Github and attach `autocheck-latest-py3-none-any.whl`
  as a binary.
