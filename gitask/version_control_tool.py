from abc import ABC, abstractmethod

class VCSInterface(ABC):
    @abstractmethod
    def create_merge_request(self, source_branch, target_branch, title, reviewer):
        pass