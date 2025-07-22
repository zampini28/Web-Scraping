from abc import ABC, abstractmethod

class BaseFetcher(ABC):
    def __init__(self, owner, repo):
        self.owner = owner
        self.repo = repo

    @abstractmethod
    def fetch(self):
        pass

    def get_error_result(self):
        return {
            "repository": f"{self.owner}/{self.repo}",
            "language": "Erro",
            "stars": "N/A",
            "forks": "N/A"
        }
