import base64
import requests
from typing import Optional, List, Dict
from dirmapper_core.auth.github_auth_manager import GitHubAuthManager
from dirmapper_core.models.directory_item import DirectoryItem
from dirmapper_core.models.directory_structure import DirectoryStructure
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
                    return base64.b64decode(content).decode('utf-8')
                else:
                    logger.error("File content is empty.")
                    return None
            else:
                logger.error(f"Failed to get file content: {response.status_code} {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting file content: {str(e)}")
            return None

    def fetch_directory_structure(self, owner: str, repo: str, path: str = "") -> DirectoryStructure:
        """
        Fetch the directory structure of a GitHub repository and convert it to DirectoryStructure and DirectoryItem objects.

        Args:
            owner (str): The owner of the repository.
            repo (str): The name of the repository.
            path (str): The path to the directory within the repository.

        Returns:
            DirectoryStructure: The directory structure of the repository.
        """
        directory_structure = DirectoryStructure()
        self._fetch_directory_contents(owner, repo, path, directory_structure, level=0)
        return directory_structure

    def _fetch_directory_contents(self, owner: str, repo: str, path: str, directory_structure: DirectoryStructure, level: int):
        """
        Recursively fetch the contents of a directory and add them to the DirectoryStructure.

        Args:
            owner (str): The owner of the repository.
            repo (str): The name of the repository.
            path (str): The path to the directory within the repository.
            directory_structure (DirectoryStructure): The directory structure to add items to.
            level (int): The current level of the directory.
        """
        contents = self.get_repository_contents(owner, repo, path)
        if contents is None:
            return

        for item in contents:
            item_path = item['path']
            item_name = item['name']
            item_type = item['type']
            directory_item = DirectoryItem(path=item_path, level=level, name=item_name, metadata={'type': item_type})

            if item_type == 'file':
                file_content = self.get_file_content(owner, repo, item_path)
                if file_content:
                    directory_item.metadata['content'] = file_content
                    directory_item.metadata['content_hash'] = directory_item._hash_content(file_content)

            directory_structure.add_item(directory_item)

            if item_type == 'dir':
                self._fetch_directory_contents(owner, repo, item_path, directory_structure, level + 1)
