import datetime
import time
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

    def _check_rate_limit(self, response: requests.Response) -> None:
        """
        Check if the rate limit has been reached and log the error if needed.

        Args:
            response (requests.Response): The response from the GitHub API.

        Raises:
            Exception: If the rate limit has been exceeded.
        """
        if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers:
            reset_time = response.headers.get('X-RateLimit-Reset')
            if reset_time:
                reset_time = datetime.datetime.fromtimestamp(int(reset_time)).strftime('%Y-%m-%d %H:%M:%S')
            logger.error(f"Rate limit exceeded. Reset time: {reset_time}")
            raise Exception("GitHub API rate limit exceeded.")

    def make_request_with_retry(self, url: str, max_retries: int = 3, backoff_factor: int = 2, **kwargs) -> requests.Response:
        """
        Make a request with retry and exponential backoff in case of transient server errors.

        Args:
            url (str): The URL to make the request to.
            max_retries (int): The maximum number of retries.
            backoff_factor (int): The backoff factor for exponential backoff.
            **kwargs: Additional arguments to pass to the requests.get method.

        Returns:
            requests.Response: The response from the server.

        Raises:
            Exception: If the maximum number of retries is exceeded.
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(url, **kwargs)
                if response.status_code == 200:
                    return response
                elif response.status_code in {502, 503, 504}:  # Transient server errors
                    logger.warning(f"Retrying due to transient error: {response.status_code}")
                    time.sleep(backoff_factor ** attempt)
                else:
                    return response
            except requests.RequestException as e:
                logger.error(f"Request failed: {str(e)}")
                time.sleep(backoff_factor ** attempt)
        raise Exception("Max retries exceeded.")

    def validate_token(self) -> bool:
        """
        Validate the OAuth token by making a request to the GitHub API.

        Returns:
            bool: True if the token is valid, False otherwise.
        """
        try:
            response = self.make_request_with_retry('https://api.github.com/user', auth=self)
            self._check_rate_limit(response)
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
            response = self.make_request_with_retry('https://api.github.com/user', auth=self)
            self._check_rate_limit(response)
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
            response = self.make_request_with_retry(url, auth=self)
            self._check_rate_limit(response)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get repository details: {response.status_code} {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting repository details: {str(e)}")
            return None
