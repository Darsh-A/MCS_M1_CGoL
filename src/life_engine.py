import collections

class Life:

    def __init__(self):
        self.alive = set()

    def add(self, cells, offset=(0,0)):
        ox, oy = offset
        for x, y in cells:
            self.alive.add((x+ox, y+oy))

    def step(self):
        neighbor_count = collections.Counter()

        for x, y in self.alive:
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    if dx != 0 or dy != 0:
                        neighbor_count[(x+dx, y+dy)] += 1

        new_alive = set()

        for cell, count in neighbor_count.items():
            if count == 3 or (count == 2 and cell in self.alive):
                new_alive.add(cell)

        self.alive = new_alive

    def run(self, steps, callback=None):
        for t in range(steps):
            self.step()
            if callback:
                callback(self, t)


    def bounding_box(self):
        if not self.alive:
            return None
        xs, ys = zip(*self.alive)
        return min(xs), max(xs), min(ys), max(ys)
    
    def region_contains_live(self, xmin, xmax, ymin, ymax):
        for x, y in self.alive:
            if xmin <= x <= xmax and ymin <= y <= ymax:
                return True
        return False
    
    def region_count(self, xmin, xmax, ymin, ymax):
        return sum(
            1 for x, y in self.alive
            if xmin <= x <= xmax and ymin <= y <= ymax
        )
    
    def region_has_live(self, xmin, xmax, ymin, ymax):
        return any(
            xmin <= x <= xmax and ymin <= y <= ymax
            for x, y in self.alive
        )

