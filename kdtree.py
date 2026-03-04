# kdtree.py

def distance(a, b):
    return (a[0]-b[0])**2 + (a[1]-b[1])**2


class KDNode:
    def __init__(self, driver, axis):
        self.driver = driver
        self.axis = axis
        self.left = None
        self.right = None


class KDTree:

    def __init__(self):
        self.root = None

    def insert(self, driver):

        def _insert(node, driver, depth):
            if node is None:
                return KDNode(driver, depth % 2)

            axis = node.axis
            if driver.location[axis] < node.driver.location[axis]:
                node.left = _insert(node.left, driver, depth+1)
            else:
                node.right = _insert(node.right, driver, depth+1)

            return node

        self.root = _insert(self.root, driver, 0)

    def k_nearest(self, target, k=5):

        result = []

        def search(node):
            if node is None:
                return

            d = distance(target, node.driver.location)
            result.append((d, node.driver))

            axis = node.axis
            diff = target[axis] - node.driver.location[axis]

            search(node.left if diff < 0 else node.right)
            search(node.right if diff < 0 else node.left)

        search(self.root)
        result.sort(key=lambda x: x[0])

        return [d for _, d in result[:k]]