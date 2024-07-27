from rUtils import Checker
import time

class LinkChecker:
    def __init__(self, links: list[str]) -> None:
        assert len(links) <= 10
        self.links = links
        checker = Checker()

        for link in links:
            checker.startAnother(link)
            time.sleep(7) # to prevent multiple threads from producing to kafka at the same time. (to some degree)
        