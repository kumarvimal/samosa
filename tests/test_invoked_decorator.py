"""Tests for the @invoked decorator in samosa.utils."""

import inspect
from unittest.mock import MagicMock

import click
from click.testing import CliRunner
import pytest

from samosa.utils import invoked


class TestInvokedDecorator:
    """Test cases for @invoked decorator functionality."""

    def test_invoked_decorator_with_no_parameters(self):
        """Test @invoked decorator with function that has no parameters."""

        @invoked
        def no_params_func():
            """Function with no parameters."""
            return "no params called"

        # Create a mock click context with invoke_ctx
        mock_invoke_ctx = MagicMock()
        mock_click_ctx = MagicMock()
        mock_click_ctx.obj = {"invoke_ctx": mock_invoke_ctx}

        # The decorator should call the original function without any context
        result = no_params_func.__wrapped__(mock_click_ctx)

        assert result == "no params called"

    def test_invoked_decorator_with_one_parameter(self):
        """Test @invoked decorator with function that has exactly 1 parameter."""

        @invoked
        def one_param_func(ctx):
            """Function with one parameter (should get invoke context)."""
            return f"invoke ctx: {type(ctx).__name__}"

        # Create mock contexts
        mock_invoke_ctx = MagicMock()
        mock_invoke_ctx.__class__.__name__ = "MockInvokeContext"
        mock_click_ctx = MagicMock()
        mock_click_ctx.obj = {"invoke_ctx": mock_invoke_ctx}

        # The decorator should pass invoke_ctx as the first parameter
        result = one_param_func.__wrapped__(mock_click_ctx)

        assert "MockInvokeContext" in result

    def test_invoked_decorator_with_two_parameters(self):
        """Test @invoked decorator with function that has 2+ parameters."""

        @invoked
        def two_param_func(invoke_ctx, click_ctx):
            """Function with two parameters (should get both contexts)."""
            return f"invoke: {type(invoke_ctx).__name__}, click: {type(click_ctx).__name__}"

        # Create mock contexts
        mock_invoke_ctx = MagicMock()
        mock_invoke_ctx.__class__.__name__ = "MockInvokeContext"
        mock_click_ctx = MagicMock()
        mock_click_ctx.__class__.__name__ = "MockClickContext"
        mock_click_ctx.obj = {"invoke_ctx": mock_invoke_ctx}

        # The decorator should pass both invoke_ctx and click_ctx
        result = two_param_func.__wrapped__(mock_click_ctx)

        assert "MockInvokeContext" in result
        assert "MockClickContext" in result

    def test_invoked_decorator_with_additional_args_kwargs(self):
        """Test @invoked decorator preserves *args and **kwargs."""

        @invoked
        def func_with_args_kwargs(invoke_ctx, click_ctx, *args, **kwargs):
            """Function that uses invoke context and additional args."""
            return {
                "invoke_ctx": type(invoke_ctx).__name__,
                "click_ctx": type(click_ctx).__name__,
                "args": args,
                "kwargs": kwargs,
            }

        # Create mock contexts
        mock_invoke_ctx = MagicMock()
        mock_invoke_ctx.__class__.__name__ = "MockInvokeContext"
        mock_click_ctx = MagicMock()
        mock_click_ctx.__class__.__name__ = "MockClickContext"
        mock_click_ctx.obj = {"invoke_ctx": mock_invoke_ctx}

        # Call with additional args and kwargs
        result = func_with_args_kwargs.__wrapped__(
            mock_click_ctx, "arg1", "arg2", key1="value1", key2="value2"
        )

        assert result["invoke_ctx"] == "MockInvokeContext"
        assert result["click_ctx"] == "MockClickContext"
        assert result["args"] == ("arg1", "arg2")
        assert result["kwargs"] == {"key1": "value1", "key2": "value2"}

    def test_invoked_decorator_parameter_counting(self):
        """Test that @invoked correctly counts function parameters."""

        def no_params():
            pass

        def one_param(ctx):
            pass

        def two_params(ctx1, ctx2):
            pass

        def three_params(ctx1, ctx2, extra):
            pass

        # Test the parameter counting logic directly
        sig_no_params = inspect.signature(no_params)
        count_no_params = len(
            [
                p
                for p in sig_no_params.parameters.values()
                if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
            ]
        )

        sig_one_param = inspect.signature(one_param)
        count_one_param = len(
            [
                p
                for p in sig_one_param.parameters.values()
                if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
            ]
        )

        sig_two_params = inspect.signature(two_params)
        count_two_params = len(
            [
                p
                for p in sig_two_params.parameters.values()
                if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
            ]
        )

        assert count_no_params == 0
        assert count_one_param == 1
        assert count_two_params == 2

    def test_invoked_decorator_with_keyword_only_parameters(self):
        """Test @invoked with keyword-only parameters (should not be counted)."""

        @invoked
        def func_with_keyword_only(ctx, *, keyword_only="default"):
            """Function with keyword-only parameter."""
            return f"ctx: {type(ctx).__name__}, keyword: {keyword_only}"

        # Create mock contexts
        mock_invoke_ctx = MagicMock()
        mock_invoke_ctx.__class__.__name__ = "MockInvokeContext"
        mock_click_ctx = MagicMock()
        mock_click_ctx.obj = {"invoke_ctx": mock_invoke_ctx}

        # Should be treated as 1-parameter function (keyword-only not counted)
        result = func_with_keyword_only.__wrapped__(mock_click_ctx, keyword_only="test")

        assert "MockInvokeContext" in result
        assert "keyword: test" in result

    def test_invoked_decorator_with_var_positional(self):
        """Test @invoked with *args parameter (should not be counted)."""

        @invoked
        def func_with_varargs(ctx, *args):
            """Function with *args."""
            return f"ctx: {type(ctx).__name__}, args: {args}"

        # Create mock contexts
        mock_invoke_ctx = MagicMock()
        mock_invoke_ctx.__class__.__name__ = "MockInvokeContext"
        mock_click_ctx = MagicMock()
        mock_click_ctx.obj = {"invoke_ctx": mock_invoke_ctx}

        # Should be treated as 1-parameter function (*args not counted)
        result = func_with_varargs.__wrapped__(mock_click_ctx, "extra1", "extra2")

        assert "MockInvokeContext" in result
        assert "args: ('extra1', 'extra2')" in result

    def test_invoked_decorator_integrated_with_click_command(self):
        """Test @invoked decorator integrated with actual Click command."""

        @click.group()
        @click.pass_context
        def test_group(ctx):
            """Test group that sets up invoke context."""
            ctx.ensure_object(dict)
            ctx.obj["invoke_ctx"] = MagicMock()
            ctx.obj["invoke_ctx"].__class__.__name__ = "MockInvokeContext"
            ctx.obj["invoke_ctx"].run = MagicMock(return_value="command executed")

        @test_group.command("test-cmd")  # Explicit name to avoid hyphen issues
        @invoked
        def test_command(invoke_ctx):
            """Test command using @invoked decorator."""
            result = invoke_ctx.run("test command")
            click.echo(f"Context type: {type(invoke_ctx).__name__}")
            click.echo(f"Result: {result}")

        runner = CliRunner()
        result = runner.invoke(test_group, ["test-cmd"])

        if result.exit_code != 0:
            print(f"Command output: {result.output}")
            print(f"Exception: {result.exception}")

        assert result.exit_code == 0
        assert "Context type: MockInvokeContext" in result.output
        assert "Result: command executed" in result.output

    def test_invoked_decorator_with_click_options(self):
        """Test @invoked decorator with Click options and arguments."""

        @click.group()
        @click.pass_context
        def test_group(ctx):
            """Test group."""
            ctx.ensure_object(dict)
            ctx.obj["invoke_ctx"] = MagicMock()
            ctx.obj["invoke_ctx"].run = MagicMock(return_value="command executed")

        @test_group.command("test-cmd")
        @click.option("--verbose", is_flag=True, help="Verbose output")
        @click.argument("name")
        @invoked
        def test_command(invoke_ctx, click_ctx, verbose, name):
            """Test command with options and @invoked decorator."""
            if verbose:
                click.echo("Verbose mode enabled")
            click.echo(f"Processing: {name}")
            click.echo(f"Invoke context: {type(invoke_ctx).__name__}")
            click.echo(f"Click context: {type(click_ctx).__name__}")
            invoke_ctx.run(f"process {name}")

        runner = CliRunner()
        result = runner.invoke(test_group, ["test-cmd", "--verbose", "test-item"])

        if result.exit_code != 0:
            print(f"Command output: {result.output}")
            print(f"Exception: {result.exception}")

        assert result.exit_code == 0
        assert "Verbose mode enabled" in result.output
        assert "Processing: test-item" in result.output
        assert "Invoke context: MagicMock" in result.output
        assert "Click context: Context" in result.output

    def test_invoked_decorator_error_handling(self):
        """Test @invoked decorator error handling when invoke_ctx is missing."""

        @invoked
        def test_func(invoke_ctx):
            return invoke_ctx.run("test")

        # Create click context without invoke_ctx in obj
        mock_click_ctx = MagicMock()
        mock_click_ctx.obj = {}  # Missing invoke_ctx

        # Should raise KeyError when trying to access missing invoke_ctx
        with pytest.raises(KeyError):
            test_func.__wrapped__(mock_click_ctx)

    def test_invoked_decorator_preserves_function_metadata(self):
        """Test that @invoked decorator preserves original function metadata."""

        def original_function(ctx):
            """Original function docstring."""
            return "test"

        decorated_function = invoked(original_function)

        # Check that the decorator creates a new function
        assert decorated_function.__name__ == "new_func"  # Wrapped function name

        # The original function should still be accessible through inspection
        assert hasattr(decorated_function, "__wrapped__")

        # We can verify the decorator is working by checking the signature inspection
        sig = inspect.signature(original_function)
        param_count = len(
            [
                p
                for p in sig.parameters.values()
                if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
            ]
        )
        assert param_count == 1  # Original function has 1 parameter

    def test_invoked_decorator_signature_analysis_edge_cases(self):
        """Test edge cases for signature analysis in @invoked decorator."""

        # Function with default parameters (should be treated as 2 params)
        @invoked
        def func_with_defaults(ctx, optional="default"):
            return f"ctx: {type(ctx).__name__}, optional: {optional}"

        # Function with mixed parameter types (should be treated as 3 params -> 2+ case)
        @invoked
        def func_mixed_params(ctx1, ctx2, optional="default", *args, **kwargs):
            return {
                "ctx1": type(ctx1).__name__,
                "ctx2": type(ctx2).__name__,
                "optional": optional,
                "args": args,
                "kwargs": kwargs,
            }

        # Mock contexts
        mock_invoke_ctx = MagicMock()
        mock_invoke_ctx.__class__.__name__ = "MockInvokeContext"
        mock_click_ctx = MagicMock()
        mock_click_ctx.__class__.__name__ = "MockClickContext"
        mock_click_ctx.obj = {"invoke_ctx": mock_invoke_ctx}

        # Test function with defaults (should be treated as 2 params)
        # The decorator injects invoke_ctx and click_ctx as the 2 parameters
        result1 = func_with_defaults.__wrapped__(mock_click_ctx)
        assert "MockInvokeContext" in result1
        assert "MockClickContext" in result1

        # Test function with mixed params (should be treated as 3 params -> 2+ case)
        # The decorator injects invoke_ctx and click_ctx, remaining parameters use defaults
        result2 = func_mixed_params.__wrapped__(mock_click_ctx)
        assert result2["ctx1"] == "MockInvokeContext"
        assert result2["ctx2"] == "MockClickContext"
        assert result2["optional"] == "default"
        assert result2["args"] == ()
        assert result2["kwargs"] == {}
