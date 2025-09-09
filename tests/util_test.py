# This file includes code from:  pre-commit/pre-commit-hooks
# Repository: https://github.com/pre-commit/pre-commit-hooks/
#
# Copyright (c) 2014 pre-commit dev team: Anthony Sottile, Ken Struys
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import annotations

import pytest

from pre_commit_hooks.util import CalledProcessError
from pre_commit_hooks.util import cmd_output
from pre_commit_hooks.util import zsplit


def test_raises_on_error():
    with pytest.raises(CalledProcessError):
        cmd_output('sh', '-c', 'exit 1')


def test_output():
    ret = cmd_output('sh', '-c', 'echo hi')
    assert ret == 'hi\n'


@pytest.mark.parametrize('out', ('\0f1\0f2\0', '\0f1\0f2', 'f1\0f2\0'))
def test_check_zsplits_str_correctly(out):
    assert zsplit(out) == ['f1', 'f2']


@pytest.mark.parametrize('out', ('\0\0', '\0', ''))
def test_check_zsplit_returns_empty(out):
    assert zsplit(out) == []
