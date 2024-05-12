import abc


class Report:

    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def report(self):
        return
