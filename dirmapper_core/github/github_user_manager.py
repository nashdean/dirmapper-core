import requests
from typing import Optional
from dirmapper_core.auth.github_auth_manager import GitHubAuthManager
from dirmapper_core.utils.logger import logger

class GitHubUserManager:
    """
    GitHubUserManager handles fetching user details from the GitHub API.
    """
    def __init__(self, auth_manager: GitHubAuthManager):
        """
        Initialize the GitHubUserManager with an authentication manager.

        Args:
            auth_manager (GitHubAuthManager): The authentication manager to use for GitHub API requests.
        """
        self.auth_manager = auth_manager

    def get_user_details(self) -> Optional[dict]:
        """
        Get the authenticated user's details from the GitHub API.

        Returns:
            Optional[dict]: The user's details if the token is valid, None otherwise.
        """
        try:
            response = self.auth_manager.make_request_with_retry('https://api.github.com/user', auth=self.auth_manager)
            self.auth_manager._check_rate_limit(response)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get user details: {response.status_code} {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting user details: {str(e)}")
            return None
