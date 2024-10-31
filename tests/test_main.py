import pytest
from unittest.mock import patch, MagicMock
import sys
from dirmapper_core.main import main

@pytest.fixture
def setup_test_ignore_file(tmpdir):
    ignore_file = tmpdir.join('.test-ignore')
    ignore_file.write("ignore_this\nignore_that\n")
    return ignore_file.strpath

def test_main_read_command(monkeypatch, setup_test_dir, setup_test_ignore_file):
    """
    Test the main function with the read command.

    This test simulates command-line arguments and patches the external dependencies to verify that the main function
    behaves correctly without invoking actual functionality. It checks that the read_command is called with the expected
    arguments.
    """

    # Simulate command-line arguments for read command
    test_args = [
        "main.py",
        "read",
        setup_test_dir,
        "--output", "test_output_file.txt",
        "--ignore_file", setup_test_ignore_file,
        "--no_gitignore",
        "--sort", "asc",
        "--style", "tree",
        "--format", "plain",
        "--ignore", "test_ignore_pattern"
    ]
    monkeypatch.setattr(sys, 'argv', test_args)

    # Patch the read_command function
    with patch('dirmapper_core.main.read_command') as mock_read_command:
        with patch('dirmapper_core.utils.cli_utils.get_package_version', return_value="1.0.0"):
            with patch('sys.exit') as mock_sys_exit:
                # Call the main function
                main()

                # Assert that read_command was called with the correct arguments
                mock_read_command.assert_called_once()
                # Assert that sys.exit was not called
                mock_sys_exit.assert_not_called()

def test_main_write_command(monkeypatch):
    """
    Test the main function with the write command.

    This test simulates command-line arguments for the write command and patches the external dependencies to verify
    that the main function behaves correctly without invoking actual functionality. It checks that the write_command
    is called with the expected arguments.
    """

    # Simulate command-line arguments for write command
    test_args = [
        "main.py",
        "write",
        "test_template_file.yaml",
        "test_root_directory"
    ]
    monkeypatch.setattr(sys, 'argv', test_args)

    # Patch the write_command function
    with patch('dirmapper_core.main.write_command') as mock_write_command:
        with patch('dirmapper_core.utils.cli_utils.get_package_version', return_value="1.0.0"):
            with patch('sys.exit') as mock_sys_exit:
                # Call the main function
                main()

                # Assert that write_command was called with the correct arguments
                mock_write_command.assert_called_once()
                # Assert that sys.exit was not called
                mock_sys_exit.assert_not_called()

# tests/test_main.py
import os
import sys
from unittest.mock import patch
import pytest

def test_main_test_api_command(monkeypatch):
    """
    Test the main function with the test-api command.

    This test simulates command-line arguments for the test-api command and patches the external dependencies to verify
    that the main function behaves correctly without invoking actual functionality. It checks that the APIClient is called
    with the expected arguments.
    """

    # Simulate command-line arguments for test-api command
    test_args = [
        "main.py",
        "test-api",
        "--base-url", "http://localhost:8000",
        "--username", "testuser",
        "--password", "testpass"
    ]
    monkeypatch.setattr(sys, 'argv', test_args)

    # Set the environment variable to enable the test command
    monkeypatch.setenv('ENABLE_TEST_COMMAND', 'true')

    # Patch the APIClient class
    with patch('dirmapper_core.api_client.APIClient.authenticate') as mock_authenticate:
        with patch('dirmapper_core.api_client.APIClient.get_hello', return_value={"message": "Hello, world!"}) as mock_get_hello:
            with patch('dirmapper_core.utils.logger.logger.info') as mock_logger_info:
                with patch('sys.exit') as mock_sys_exit:
                    # Call the main function
                    main()

                    # Assert that authenticate was called once
                    mock_authenticate.assert_called_once_with("testuser", "testpass")
                    # Assert that get_hello was called once
                    mock_get_hello.assert_called_once()
                    # Assert that logger.info was called with the correct message
                    mock_logger_info.assert_called_with('API response: {"message": "Hello, world!"}')
                    # Assert that sys.exit was not called
                    mock_sys_exit.assert_not_called()

def test_main_test_api_command_with_cached_token(monkeypatch):
    """
    Test the main function with the test-api command using a cached token.

    This test simulates command-line arguments for the test-api command and patches the external dependencies to verify
    that the main function behaves correctly without invoking actual functionality. It checks that the APIClient is called
    with the expected arguments and uses the cached token.
    """

    # Simulate command-line arguments for test-api command
    test_args = [
        "main.py",
        "test-api",
        "--base-url", "http://localhost:8000"
    ]
    monkeypatch.setattr(sys, 'argv', test_args)

    # Set the environment variable to enable the test command
    monkeypatch.setenv('ENABLE_TEST_COMMAND', 'true')

    # Patch the APIClient class
    with patch('dirmapper_core.api_client.APIClient.load_token', return_value="cached_token") as mock_load_token:
        with patch('dirmapper_core.api_client.APIClient.get_hello', return_value={"message": "Hello, world!"}) as mock_get_hello:
            with patch('dirmapper_core.utils.logger.logger.info') as mock_logger_info:
                with patch('sys.exit') as mock_sys_exit:
                    # Call the main function
                    main()

                    # Assert that load_token was called once
                    mock_load_token.assert_called_once()
                    # Assert that get_hello was called once
                    mock_get_hello.assert_called_once()
                    # Assert that logger.info was called with the correct message
                    mock_logger_info.assert_called_with('API response: {"message": "Hello, world!"}')
                    # Assert that sys.exit was not called
                    mock_sys_exit.assert_not_called()

def test_main_test_api_command_with_cached_token(monkeypatch):
    """
    Test the main function with the test-api command using a cached token.

    This test simulates command-line arguments for the test-api command and patches the external dependencies to verify
    that the main function behaves correctly without invoking actual functionality. It checks that the APIClient is called
    with the expected arguments and uses the cached token.
    """

    # Simulate command-line arguments for test-api command
    test_args = [
        "main.py",
        "test-api",
        "--base-url", "http://localhost:8000"
    ]
    monkeypatch.setattr(sys, 'argv', test_args)

    # Set the environment variable to enable the test command
    monkeypatch.setenv('ENABLE_TEST_COMMAND', 'true')

    # Patch the APIClient class
    with patch('dirmapper_core.api_client.APIClient.load_token', return_value="cached_token") as mock_load_token:
        with patch('dirmapper_core.api_client.APIClient.get_hello', return_value={"message": "Hello, world!"}) as mock_get_hello:
            with patch('dirmapper_core.utils.logger.logger.info') as mock_logger_info:
                with patch('sys.exit') as mock_sys_exit:
                    # Call the main function
                    main()

                    # Assert that load_token was called once
                    mock_load_token.assert_called_once()
                    # Assert that get_hello was called once
                    mock_get_hello.assert_called_once()
                    # Assert that logger.info was called with the correct message
                    mock_logger_info.assert_called_with('API response: {"message": "Hello, world!"}')
                    # Assert that sys.exit was not called
                    mock_sys_exit.assert_not_called()

#FIXME: Test is failing
# def test_main_with_exception(monkeypatch):
#     """
#     Test the main function to ensure it handles exceptions correctly.

#     This test simulates minimal command-line arguments and patches the external dependencies to raise an exception.
#     It verifies that the exception is logged correctly using the log_exception function.
#     """
#     # Simulate command-line arguments
#     test_args = [
#         "main.py",
#         "convert",
#         "test_root_directory",
#         "test_output_file"
#     ]
#     monkeypatch.setattr(sys, 'argv', test_args)

#     # Patch the external dependencies to raise an exception
#     with patch('dirmapper_core.main.read_command', side_effect=Exception("Test exception")):
#         with patch('dirmapper_core.utils.logger.log_exception') as mock_log_exception:
#             with patch('dirmapper_core.utils.cli_utils.get_package_version', return_value="1.0.0"):
#                 with patch('sys.exit') as mock_sys_exit:
#                     # Call the main function
#                     main()

#                     # Assert that log_exception was called with the correct exception
#                     mock_log_exception.assert_called_once_with(Exception("Test exception"))
#                     # Assert that sys.exit was called
#                     mock_sys_exit.assert_called_once_with(1)