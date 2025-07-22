import requests
from .base_fetcher import BaseFetcher

class GithubApiFetcher(BaseFetcher):
    def __init__(self, owner, repo):
        super().__init__(owner, repo)
        self.url = f"https://api.github.com/repos/{owner}/{repo}"

    def fetch(self):
        try:
            headers = {"Accept": "application/vnd.github.v3+json"}
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            return {
                "repository": f"{self.owner}/{self.repo}",
                "language": data.get("language", "N/A"),
                "stars": f'{data.get("stargazers_count", 0):,}',
                "forks": f'{data.get("forks_count", 0):,}'
            }
        except requests.exceptions.RequestException as e:
            print(f"[{self.repo}] Um erro ocurreu durante a requisição da API: {e}")
            return self.get_error_result()
