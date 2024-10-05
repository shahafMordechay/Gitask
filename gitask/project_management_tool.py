from abc import ABC, abstractmethod

class PMToolInterface(ABC):
    @abstractmethod
    def move_to_in_progress(self):
        pass

    @abstractmethod
    def move_to_in_review(self, target_branch, reviewer):
        pass