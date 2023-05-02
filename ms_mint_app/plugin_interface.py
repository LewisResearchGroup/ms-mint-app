from abc import ABC, abstractmethod

class PluginInterface(ABC):
    @abstractmethod
    def callbacks(self, app, fsc, cache):
        pass

    @abstractmethod
    def layout(self):
        pass

    @property
    def label(self):
        return self._label

    @property
    @abstractmethod
    def outputs(self):
        pass
    
    @property
    def order(self):
        return self._order
    
        