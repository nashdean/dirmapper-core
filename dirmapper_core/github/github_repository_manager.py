import requests
from typing import Optional, List, Dict
from dirmapper_core.auth.github_auth_manager import GitHubAuthManager
from dirmapper_core.utils.logger import logger

class GitHubRepositoryManager:
    """
    GitHubRepositoryManager handles fetching files and directories from a GitHub repository.
    """
    def __init__(self, auth_manager: GitHubAuthManager):
        """
        Initialize the GitHubRepositoryManager with an authentication manager.

        Args:
            auth_manager (GitHubAuthManager): The authentication manager to use for GitHub API requests.
        """
        self.auth_manager = auth_manager

    def get_repository_contents(self, owner: str, repo: str, path: str = "") -> Optional[List[Dict]]:
        """
        Get the contents of a repository or a specific directory from the GitHub API.

        Args:
            owner (str): The owner of the repository.
            repo (str): The name of the repository.
            path (str): The path to the directory or file within the repository.

        Returns:
            Optional[List[Dict]]: The contents of the repository or directory if the request is successful, None otherwise.
        """
        try:
            url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
            response = self.auth_manager.make_request_with_retry(url, auth=self.auth_manager)
            self.auth_manager._check_rate_limit(response)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get repository contents: {response.status_code} {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting repository contents: {str(e)}")
            return None

    def get_file_content(self, owner: str, repo: str, path: str) -> Optional[str]:
        """
        Get the content of a file from the GitHub API.

        Args:
            owner (str): The owner of the repository.
            repo (str): The name of the repository.
            path (str): The path to the file within the repository.

        Returns:
            Optional[str]: The content of the file if the request is successful, None otherwise.
        """
        try:
            url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
            response = self.auth_manager.make_request_with_retry(url, auth=self.auth_manager)
            self.auth_manager._check_rate_limit(response)
            if response.status_code == 200:
                content = response.json().get('content')
                if content:
                    return content
                else:
                    logger.error("File content is empty.")
                    return None
            else:
                logger.error(f"Failed to get file content: {response.status_code} {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting file content: {str(e)}")
            return None
