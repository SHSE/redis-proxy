from time import time
from typing import Optional


class Node:
    key: any
    value: any
    expires: float
    prev: Optional[any]
    next: Optional[any]

    def __init__(self):
        self.prev = None
        self.next = None


class Cache:
    """
    LRU cache with expiration.
    """

    def __init__(self, capacity: int, ttl: float):
        self.ttl = ttl
        self.capacity = capacity
        self.map = dict()
        self.head = None
        self.tail = None

    def __setitem__(self, key, value):
        node = self.map.get(key)

        if node is None:
            node = Node()
            node.key = key
            self.map[key] = node
            self._append(node)

        node.value = value
        node.expires = time() + self.ttl

        self._touch(node)

        if len(self.map) > self.capacity:
            self._delete(self.tail)

    def __len__(self) -> int:
        return len(self.map)

    def get(self, key) -> Optional[any]:
        node = self.map.get(key)

        if node is None:
            return None

        if node.expires < time():
            self._delete(node)
            return None

        self._touch(node)

        return node.value

    def _delete(self, node: Node):
        del self.map[node.key]
        self._evict(node)

    def _append(self, node: Node):
        if self.head:
            node.next = self.head
            self.head.prev = node

        self.head = node

        if not self.tail:
            self.tail = node

    def _evict(self, node: Node):
        prev = node.prev
        next = node.next

        node.prev = None
        node.next = None

        if prev:
            prev.next = next

        if next:
            next.prev = prev

        if self.head == node:
            self.head = next

        if self.tail == node:
            self.tail = prev

    def _touch(self, node: Node):
        if self.head == node:
            return

        self._evict(node)
        self._append(node)
