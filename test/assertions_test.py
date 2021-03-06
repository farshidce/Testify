from __future__ import with_statement

from testify import TestCase
from testify import assertions
from testify import run
from testify import assert_between
from testify import assert_dict_subset
from testify import assert_equal
from testify import assert_not_reached


class DiffMessageTestCase(TestCase):

    def test_shows_string_diffs(self):
        expected = 'Diff:\nl: abc<>\nr: abc<def>'
        diff_message = assertions._diff_message('abc', 'abcdef')
        assert_equal(expected, diff_message)

    def test_shows_repr_diffs(self):
        class AbcRepr(object):
            __repr__ = lambda self: 'abc'

        class AbcDefRepr(object):
            __repr__ = lambda self: 'abcdef'

        expected = 'Diff:\nl: abc<>\nr: abc<def>'
        diff_message = assertions._diff_message(AbcRepr(), AbcDefRepr())
        assert_equal(expected, diff_message)


class AssertBetweenTestCase(TestCase):

    def test_argument_order(self):
        try:
            assert_between(1, 2, 3)
        except AssertionError:
            assert False, "Expected assert_between(1, 2, 3) to pass."

        try:
            assert_between(2, 1, 3)
            assert False, "Expected assert_between(2, 1, 3) to fail."
        except AssertionError:
            pass


class AssertEqualTestCase(TestCase):

    def test_shows_pretty_diff_output(self):
        expected = \
            'assertion failed: l == r\n' \
            "l: 'that reviewboard differ is awesome'\n" \
            "r: 'dat reviewboard differ is ozsom'\n\n" \
            'Diff:' \
            '\nl: <th>at reviewboard differ is <awe>som<e>\n' \
            'r: <d>at reviewboard differ is <oz>som<>'

        try:
            assert_equal('that reviewboard differ is awesome',
                         'dat reviewboard differ is ozsom')
        except AssertionError, e:
            assert_equal(expected, e.args[0])
        else:
            assert False, 'Expected `AssertionError`.'


class MyException(Exception):
    pass

class AssertRaisesAsContextManagerTestCase(TestCase):

    def test_fails_when_exception_is_not_raised(self):
        def exception_should_be_raised():
            with assertions.assert_raises(MyException):
                pass

        try:
            exception_should_be_raised()
        except AssertionError:
            pass
        else:
            assert_not_reached('AssertionError should have been raised')

    def test_passes_when_exception_is_raised(self):
        def exception_should_be_raised():
            with assertions.assert_raises(MyException):
                raise MyException

        exception_should_be_raised()

    def test_crashes_when_another_exception_class_is_raised(self):
        def assert_raises_an_exception_and_raise_another():
            with assertions.assert_raises(MyException):
                raise ValueError

        try:
            assert_raises_an_exception_and_raise_another()
        except ValueError:
            pass
        else:
            raise AssertionError('ValueError should have been raised')


class AssertRaisesAsCallableTestCase(TestCase):

    def test_fails_when_exception_is_not_raised(self):
        raises_nothing = lambda: None
        try:
            assertions.assert_raises(ValueError, raises_nothing)
        except AssertionError:
            pass
        else:
            assert_not_reached('AssertionError should have been raised')

    def test_passes_when_exception_is_raised(self):
        def raises_value_error():
            raise ValueError
        assertions.assert_raises(ValueError, raises_value_error)

    def test_fails_when_wrong_exception_is_raised(self):
        def raises_value_error():
            raise ValueError
        try:
            assertions.assert_raises(MyException, raises_value_error)
        except ValueError:
            pass
        else:
            assert_not_reached('ValueError should have been raised')

    def test_callable_is_called_with_all_arguments(self):
        class GoodArguments(Exception): pass
        arg1, arg2, kwarg = object(), object(), object()
        def check_arguments(*args, **kwargs):
            assert_equal((arg1, arg2), args)
            assert_equal({'kwarg': kwarg}, kwargs)
            raise GoodArguments
        assertions.assert_raises(GoodArguments, check_arguments, arg1, arg2, kwarg=kwarg)


class AssertRaisesSuchThatTestCase(TestCase):

    def test_fails_when_no_exception_is_raised(self):
        """Tests that the assertion fails when no exception is raised."""
        exists = lambda e: True
        with assertions.assert_raises(AssertionError):
            with assertions.assert_raises_such_that(Exception, exists):
                pass

    def test_fails_when_wrong_exception_is_raised(self):
        """Tests that when an unexpected exception is raised, that it is
        passed through and the assertion fails."""
        exists = lambda e: True
        # note: in assert_raises*, if the exception raised is not of the
        # expected type, that exception just falls through
        with assertions.assert_raises(Exception):
            with assertions.assert_raises_such_that(AssertionError, exists):
                raise Exception("the wrong exception")

    def test_fails_when_exception_test_fails(self):
        """Tests that when an exception of the right type that fails the
        passed in exception test is raised, the assertion fails."""
        has_two_args = lambda e: assertions.assert_length(e.args, 2)
        with assertions.assert_raises(AssertionError):
            with assertions.assert_raises_such_that(Exception, has_two_args):
                raise Exception("only one argument")

    def test_passes_when_correct_exception_is_raised(self):
        """Tests that when an exception of the right type that passes the
        exception test is raised, the assertion passes."""
        has_two_args = lambda e: assertions.assert_length(e.args, 2)
        with assertions.assert_raises_such_that(Exception, has_two_args):
            raise Exception("first", "second")

    def test_callable_is_called_with_all_arguments(self):
        """Tests that the callable form works properly, with all arguments
        passed through."""
        message_is_foo = lambda e: assert_equal(str(e), 'foo')
        class GoodArguments(Exception): pass
        arg1, arg2, kwarg = object(), object(), object()
        def check_arguments(*args, **kwargs):
            assert_equal((arg1, arg2), args)
            assert_equal({'kwarg': kwarg}, kwargs)
            raise GoodArguments('foo')
        assertions.assert_raises_such_that(GoodArguments, message_is_foo, check_arguments, arg1, arg2, kwarg=kwarg)


class AssertRaisesAndContainsTestCase(TestCase):

    def test_fails_when_exception_is_not_raised(self):
        raises_nothing = lambda: None
        try:
            assertions.assert_raises_and_contains(ValueError, 'abc', raises_nothing)
        except AssertionError:
            pass
        else:
            assert_not_reached('AssertionError should have been raised')

    def test_fails_when_wrong_exception_is_raised(self):
        def raises_value_error():
            raise ValueError
        try:
            assertions.assert_raises_and_contains(MyException, 'abc', raises_value_error)
        except ValueError:
            pass
        else:
            assert_not_reached('ValueError should have been raised')

    def test_callable_is_called_with_all_arguments(self):
        class GoodArguments(Exception): pass
        arg1, arg2, kwarg = object(), object(), object()
        def check_arguments(*args, **kwargs):
            assert_equal((arg1, arg2), args)
            assert_equal({'kwarg': kwarg}, kwargs)
            raise GoodArguments('abc')
        assertions.assert_raises_and_contains(GoodArguments, 'abc', check_arguments, arg1, arg2, kwarg=kwarg)

    def test_fails_when_exception_does_not_contain_string(self):
        def raises_value_error():
            raise ValueError('abc')
        try:
            assertions.assert_raises_and_contains(ValueError, 'xyz', raises_value_error)
        except AssertionError:
            pass
        else:
            assert_not_reached('AssertionError should have been raised')

    def test_passes_when_exception_contains_string_with_matching_case(self):
        def raises_value_error():
            raise ValueError('abc')
        assertions.assert_raises_and_contains(ValueError, 'abc', raises_value_error)

    def test_passes_when_exception_contains_string_with_non_matching_case(self):
        def raises_value_error():
            raise ValueError('abc')
        assertions.assert_raises_and_contains(ValueError, 'ABC', raises_value_error)

    def test_passes_when_exception_contains_multiple_strings(self):
        def raises_value_error():
            raise ValueError('abc xyz')
        assertions.assert_raises_and_contains(ValueError, ['ABC', 'XYZ'], raises_value_error)

    def test_fails_when_exception_does_not_contains_all_strings(self):
        def raises_value_error():
            raise ValueError('abc xyz')
        try:
            assertions.assert_raises_and_contains(ValueError, ['ABC', '123'], raises_value_error)
        except AssertionError:
            pass
        else:
            assert_not_reached('AssertionError should have been raised')

class AssertDictSubsetTestCase(TestCase):

    def test_passes_with_subset(self):
        superset = {'one': 1, 'two': 2, 'three': 3}
        subset = {'one': 1}

        assert_dict_subset(subset, superset)

    def test_fails_with_wrong_key(self):
        superset = {'one': 1, 'two': 2, 'three': 3}
        subset = {'four': 4}

        assertions.assert_raises(AssertionError, assert_dict_subset, subset, superset)

    def test_fails_with_wrong_value(self):
        superset = {'one': 1, 'two': 2, 'three': 3}
        subset = {'one': 2}

        assertions.assert_raises(AssertionError, assert_dict_subset, superset, subset)

    def test_message_on_fail(self):
        superset = {'one': 1, 'two': 2, 'three': 3}
        subset = {'one': 2, 'two':2}
        expected = "expected [subset has:{'one': 2}, superset has:{'one': 1}]"

        try:
            assert_dict_subset(subset, superset)
        except AssertionError, e:
            assert_equal(expected, e.args[0])
        else:
            assert_not_reached('AssertionError should have been raised')

class AssertEmptyTestCase(TestCase):

    def test_passes_on_empty_list(self):
        """Test that assert_empty passes on an empty list."""
        assertions.assert_empty([])

    def test_passes_on_unyielding_generator(self):
        """Test that assert_empty passes on an 'empty' generator."""
        def yield_nothing():
            if False:
                yield 0

        assertions.assert_empty(yield_nothing())

    def test_fails_on_nonempty_list(self):
        """Test that assert_empty fails on a nonempty list."""
        with assertions.assert_raises(AssertionError):
            assertions.assert_empty([0])

    def test_fails_on_infinite_generator(self):
        """Tests that assert_empty fails on an infinite generator."""
        def yes():
            while True:
                yield 'y'

        with assertions.assert_raises(AssertionError):
            assertions.assert_empty(yes())

    def test_max_elements_to_print_eq_0_means_no_sample_message(self):
        """Tests that when max_elements_to_print is 0, there is no sample in the error message."""
        iterable = [1, 2, 3]
        expected_message = "iterable %s was unexpectedly non-empty." % iterable

        def message_has_no_sample(exception):
            assertions.assert_equal(str(exception), expected_message)

        with assertions.assert_raises_such_that(
                AssertionError, message_has_no_sample):
            assertions.assert_empty(iterable, max_elements_to_print=0)

    def test_max_elements_to_print_gt_len_means_whole_iterable_sample_message(self):
        """
        Tests that when max_elements_to_print is greater than the length of
        the whole iterable, the whole iterable is printed.
        """
        elements = [1, 2, 3, 4, 5]
        iterable = (i for i in elements)
        expected_message = "iterable %s was unexpectedly non-empty. elements: %s" \
                         % (iterable, elements)

        def message_has_whole_iterable_sample(exception):
            assertions.assert_equal(str(exception), expected_message)

        with assertions.assert_raises_such_that(
                AssertionError, message_has_whole_iterable_sample):
            assertions.assert_empty(iterable, max_elements_to_print=len(elements)+1)

    def test_max_elements_to_print_eq_len_means_whole_iterable_sample_message(self):
        """
        Tests that when max_elements_to_print is equal to the length of
        the whole iterable, the whole iterable is printed.
        """
        elements = [1, 2, 3, 4, 5]
        iterable = (i for i in elements)
        expected_message = "iterable %s was unexpectedly non-empty. elements: %s" \
                         % (iterable, elements)

        def message_has_whole_iterable_sample(exception):
            assertions.assert_equal(str(exception), expected_message)

        with assertions.assert_raises_such_that(
                AssertionError, message_has_whole_iterable_sample):
            assertions.assert_empty(iterable, max_elements_to_print=len(elements))

    def test_max_elements_to_print_lt_len_means_partial_iterable_sample_message(self):
        """
        Tests that when max_elements_to_print is less than the length of the
        whole iterable, the first max_elements_to_print elements are printed.
        """
        elements = [1, 2, 3, 4, 5]
        iterable = (i for i in elements)
        max_elements_to_print = len(elements) - 1
        expected_message = "iterable %s was unexpectedly non-empty. first %i elements: %s" \
                         % (iterable, max_elements_to_print, elements[:max_elements_to_print])

        def message_has_whole_iterable_sample(exception):
            assertions.assert_equal(str(exception), expected_message)

        with assertions.assert_raises_such_that(
                AssertionError, message_has_whole_iterable_sample):
            assertions.assert_empty(iterable, max_elements_to_print=max_elements_to_print)

class AssertNotEmptyTestCase(TestCase):

    def test_fails_on_empty_list(self):
        """Test that assert_not_empty fails on an empty list."""
        with assertions.assert_raises(AssertionError):
            assertions.assert_not_empty([])

    def test_fails_on_unyielding_generator(self):
        """Test that assert_not_empty fails on an 'empty' generator."""
        def yield_nothing():
            if False:
                yield 0

        with assertions.assert_raises(AssertionError):
            assertions.assert_not_empty(yield_nothing())

    def test_passes_on_nonempty_list(self):
        """Test that assert_not_empty passes on a nonempty list."""
        assertions.assert_not_empty([0])

    def test_passes_on_infinite_generator(self):
        """Tests that assert_not_empty fails on an infinite generator."""
        def yes():
            while True:
                yield 'y'

        assertions.assert_not_empty(yes())


if __name__ == '__main__':
    run()
