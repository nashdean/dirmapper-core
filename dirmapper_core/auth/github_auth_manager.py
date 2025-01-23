import requests
from requests.auth import AuthBase
from typing import Optional
from dirmapper_core.utils.logger import logger

class GitHubAuthManager(AuthBase):
    """
    GitHubAuthManager handles authentication with the GitHub API using an OAuth token.
    """
    def __init__(self, oauth_token: str):
        """
        Initialize the GitHubAuthManager with an OAuth token.

        Args:
            oauth_token (str): The OAuth token provided by the user.
        """
        self.oauth_token = oauth_token

    def __call__(self, r):
        """
        Attach the OAuth token to the request headers.

        Args:
            r (requests.PreparedRequest): The request to modify.

        Returns:
            requests.PreparedRequest: The modified request with the OAuth token.
        """
        r.headers['Authorization'] = f'token {self.oauth_token}'
        return r

    def validate_token(self) -> bool:
        """
        Validate the OAuth token by making a request to the GitHub API.

        Returns:
            bool: True if the token is valid, False otherwise.
        """
        try:
            response = requests.get('https://api.github.com/user', auth=self)
            if response.status_code == 200:
                logger.info("OAuth token is valid.")
                return True
            else:
                logger.error(f"OAuth token validation failed: {response.status_code} {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error validating OAuth token: {str(e)}")
            return False

    def get_user_details(self) -> Optional[dict]:
        """
        Get the authenticated user's details from the GitHub API.

        Returns:
            Optional[dict]: The user's details if the token is valid, None otherwise.
        """
        try:
            response = requests.get('https://api.github.com/user', auth=self)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get user details: {response.status_code} {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting user details: {str(e)}")
            return None

    def get_repository_details(self, owner: str, repo: str) -> Optional[dict]:
        """
        Get the details of a repository from the GitHub API.

        Args:
            owner (str): The owner of the repository.
            repo (str): The name of the repository.

        Returns:
            Optional[dict]: The repository details if the token is valid, None otherwise.
        """
        try:
            url = f'https://api.github.com/repos/{owner}/{repo}'
            response = requests.get(url, auth=self)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get repository details: {response.status_code} {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting repository details: {str(e)}")
            return None
