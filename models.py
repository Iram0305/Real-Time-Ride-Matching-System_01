# models.py

class Driver:
    def __init__(self, driver_id, x, y, rating=4.5):
        self.id = driver_id
        self.location = (x, y)
        self.rating = rating
        self.available = True

    def update_location(self, x, y):
        self.location = (x, y)


class Passenger:
    def __init__(self, pid, x, y):
        self.id = pid
        self.location = (x, y)