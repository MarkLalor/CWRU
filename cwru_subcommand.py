from abc import ABC, abstractmethod

class CwruSubcommand(ABC):
    @abstractmethod
    def handle(self):
        pass
    