# matcher.py

import heapq
from kdtree import KDTree, distance


class MatchingEngine:

    def __init__(self):
        self.tree = KDTree()
        self.drivers = {}

    def rebuild_tree(self):
        self.tree = KDTree()
        for d in self.drivers.values():
            if d.available:
                self.tree.insert(d)

    def add_driver(self, driver):
        self.drivers[driver.id] = driver
        self.rebuild_tree()

    def update_location(self, driver_id, x, y):
        self.drivers[driver_id].update_location(x, y)
        self.rebuild_tree()

    def request_ride(self, passenger):

        candidates = self.tree.k_nearest(passenger.location, 5)

        heap = []

        for driver in candidates:
            if driver.available:
                score = (
                    0.7 * distance(passenger.location, driver.location)
                    + 0.3 * (1 / driver.rating)
                )
                heapq.heappush(heap, (score, driver))

        if not heap:
            return None, "No drivers available"

        _, best = heapq.heappop(heap)
        best.available = False
        self.rebuild_tree()

        message = f'Driver "{best.id}" has been assigned to User "{passenger.id}"'
        return best, message