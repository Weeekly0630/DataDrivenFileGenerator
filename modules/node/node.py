"""
Basic NodeList 模块
"""

from enum import Enum
from typing import Optional, List, Dict
from dataclasses import dataclass


class ListNode:

    def __init__(self):
        self.prev = self
        self.next = self

    def insert_after(self, node: "ListNode") -> None:
        """在当前节点后插入新节点"""
        node.next = self.next
        node.prev = self
        self.next.prev = node
        self.next = node
        
    def insert_before(self, node: "ListNode") -> None:
        """在当前节点前插入新节点"""
        node.prev = self.prev
        node.next = self
        self.prev.next = node
        self.prev = node
        
    def remove(self) -> None:
        """从链表中移除当前节点"""
        self.prev.next = self.next
        self.next.prev = self.prev
        self.next = self
        self.prev = self
        
    def is_single(self) -> bool:
        """检查是否是单独的节点"""
        return self.prev == self and self.next == self