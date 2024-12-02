import argparse
import itertools
import logging
import math

logger = logging.getLogger(__name__)

RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"


# https://stackoverflow.com/questions/15675261/displaying-a-tree-in-ascii
def block_width(block):
    """Returns width of first line in a text block."""
    try:
        return block.index("\n")
    except ValueError:
        return len(block)


def stack_str_blocks(blocks):
    """Stacks multiple text blocks horizontally with spacing."""
    builder = []
    block_lens = [block_width(bl) for bl in blocks]
    split_blocks = [bl.split("\n") for bl in blocks]

    for line_list in itertools.zip_longest(*split_blocks, fillvalue=None):
        for i, line in enumerate(line_list):
            if line is None:
                builder.append(" " * block_lens[i])
            else:
                builder.append(line)
            if i != len(line_list) - 1:
                builder.append(" ")  # Padding
        builder.append("\n")

    return "".join(builder[:-1])


class BPlusTreeNode:
    """Node in B+ Tree. Can be non-leaf or leaf node."""

    def __init__(
        self,
        order: int,
        leaf: bool,
        keys: list[int] | None = None,
        values: list['BPlusTreeNode | list[int]'] | None = None,
        parent: 'BPlusTreeNode | None' = None,
    ) -> None:
        """Initialize node with order, leaf status, keys, values and parent."""
        self.order = order
        self.leaf = leaf
        self.keys = keys or []
        self.values = values or []
        self.parent = parent
        self.prev = None
        self.next = None

    def __str__(self) -> str:
        return f"BPlusTreeNode(keys: {self.keys}, values: {self.values})"

    def __repr__(self) -> str:
        return self.__str__()

    def is_underflow(self) -> bool:
        """Check if node has fewer than minimum required keys."""
        return len(self.keys) < math.ceil(self.order / 2)

    def is_overflow(self) -> bool:
        """Check if node has more than maximum allowed keys."""
        return len(self.keys) > self.order

    def add(self, data: int) -> None:
        """Insert data into leaf node, maintaining sorted order."""

        # simply insert a pair if node is empty
        if not self.keys:
            self.keys.append(data)
            self.values.append([data])
            return

        # insert key-value pair into right position
        for i, key in enumerate(self.keys):
            if data == key:
                logger.info(f"{RED}Data already exists: {data}{RESET}")
                return
            elif data < key:
                # insert data to the left child of existing key
                self.keys = self.keys[:i] + [data] + self.keys[i:]
                self.values = self.values[:i] + [[data]] + self.values[i:]
                return

        # if data is greater than every keys, insert into rightmost position
        self.keys.append(data)
        self.values.append([data])

    def remove(self, data: int) -> tuple["BPlusTreeNode", int, int]:
        """Remove data from leaf node. Returns (parent, old_min_key, new_min_key)."""
        try:
            idx = self.keys.index(data)
        except ValueError:
            logger.info(f"{RED}Data not found: {data}{RESET}")
            raise TypeError("Data not found")

        old_min_key = self.keys[0]
        self.keys.pop(idx)
        self.values.pop(idx)

        new_min_key = self.keys[0] if self.keys else old_min_key
        return self.parent, old_min_key, new_min_key

    def split(self) -> None:
        """Split node into two when overflow occurs."""
        logger.debug(
            f"{BLUE}Split and grow, keys: {self.keys}, values: {self.values}{RESET}"
        )

        # non-leaf node: k + 1 values, leaf node: k values
        key_mid_idx = math.ceil(self.order / 2)
        value_mid_idx = key_mid_idx if self.leaf else key_mid_idx + 1

        left = BPlusTreeNode(
            self.order,
            self.leaf,
            self.keys[:key_mid_idx],
            self.values[:value_mid_idx],
            self,
        )
        right = BPlusTreeNode(
            self.order,
            self.leaf,
            self.keys[key_mid_idx:],
            self.values[value_mid_idx:],
            self,
        )

        # if it's an non-leaf node, update grandchild's parents
        if not self.leaf:
            for child in left.values:
                child.parent = left
            for child in right.values:
                child.parent = right

        # convert itself into a new parent node
        # for non-leaf nodes, push up instead of copy up
        self.keys = [right.keys[0]] if self.leaf else [right.keys.pop(0)]
        self.values = [left, right]
        self.leaf = False

        self._update_doubly_linked_list(left, right)

    def _update_doubly_linked_list(
        self, left: "BPlusTreeNode", right: "BPlusTreeNode"
    ) -> None:
        """Update links between nodes after a split."""
        # cousin <- left  right -> cousin
        left.prev = self.prev
        right.next = self.next

        # cousin -> left  right <- cousin
        if self.prev:
            self.prev.next = left
        if self.next:
            self.next.prev = right

        # cousin left <-> right cousin
        left.next = right
        right.prev = left

    def show(self):
        """Print node structure in ASCII tree format."""
        if not self.values or all(
            not isinstance(child, BPlusTreeNode) for child in self.values
        ):
            if PLAIN_DISPLAY:
                return ",".join(str(k) for k in self.keys)
            return "[" + ",".join(str(k) for k in self.keys) + "]"

        child_strs = [
            child.show() for child in self.values if isinstance(child, BPlusTreeNode)
        ]
        if PLAIN_DISPLAY:
            return ",".join(child_strs)
        
        child_widths = [block_width(s) for s in child_strs]

        display_width = max(
            len(str(self.keys[0])), sum(child_widths) + len(child_widths) - 1
        )

        # determines midpoints of child blocks
        child_midpoints = []
        child_end = 0
        for width in child_widths:
            child_midpoints.append(child_end + (width // 2))
            child_end += width + 1

        # builds up the brace, using the child midpoints
        brace_builder = []
        for i in range(display_width):
            if i < child_midpoints[0] or i > child_midpoints[-1]:
                brace_builder.append(" ")
            elif i in child_midpoints:
                brace_builder.append("+")
            else:
                brace_builder.append("-")
        brace = "".join(brace_builder)

        keys = "(" + ",".join(str(k) for k in self.keys) + ")"
        name_str = "{:^{}}".format(keys, display_width)
        below = stack_str_blocks(child_strs)

        return name_str + "\n" + brace + "\n" + below


class BPlusTree:
    """B+ Tree implementation with search, insert, and delete operations."""

    order = 4
    root: BPlusTreeNode

    def __init__(self, order: int) -> None:
        """Initialize B+ tree as a root with given order."""
        self.order = order
        self.root = BPlusTreeNode(self.order, leaf=True)

    def _display_bplus_tree(func):
        """Display B+ tree after performing an operation."""

        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            if DISPLAY_AFTER_OPERATION:
                self.display()

        return wrapper

    def _search_min_key_in_subtree(self, node: BPlusTreeNode | int) -> int:
        """Find minimum key in subtree rooted at node."""
        if isinstance(node, list):
            return node[0]

        while not node.leaf:
            node = node.values[0]
        return node.keys[0]

    def _search_position_in_child(
        self, node: BPlusTreeNode, data: int
    ) -> tuple[BPlusTreeNode, int]:
        """Find child node where data should be inserted."""
        for i, key in enumerate(node.keys):
            if data < key:
                return node.values[i], i  # left child of the key of greater value
        return node.values[i + 1], i + 1  # rightmost child

    def _merge_into_parent(self, node: BPlusTreeNode, idx: int) -> None:
        """Merge split node into its parent."""
        logger.debug(
            f"{BLUE}Merge into parent, keys: {node.keys}, values: {node.values}{RESET}"
        )

        # remove node from parent's child
        parent = node.parent
        parent.values.pop(idx)

        # update parents of current node's child before inserting them into parent
        for child in node.values:
            child.parent = parent

        # linear search and insertion
        pivot = node.keys[0]
        for i, key in enumerate(parent.keys):
            if pivot < key:
                parent.keys = parent.keys[:i] + [pivot] + parent.keys[i:]
                parent.values = parent.values[:i] + node.values + parent.values[i:]
                return

        parent.keys.append(pivot)
        parent.values.extend(node.values)

    def _left_rotate(self, node: BPlusTreeNode) -> tuple[BPlusTreeNode, int, int]:
        """Move leftmost key/child from node to left sibling."""
        logger.debug(
            f"{BLUE}Rotate to left, keys: {node.prev.keys} <- {node.keys}{RESET}"
        )
        left_node = node.prev

        if len(node.keys) - 1 < math.ceil(self.order / 2):
            logger.debug(
                f"{RED}Left rotate not possible. len(keys): {len(node.keys)}{RESET}"
            )
            raise TypeError("Left rotate not possible")

        # old and new minimum key of current node
        old_min_key = self._search_min_key_in_subtree(node.values[0])
        new_min_key = self._search_min_key_in_subtree(node.values[1])

        # insert current subtree's minimum key and child into left sibling
        left_node.keys.append(old_min_key)
        left_node.values.append(node.values[0])

        node.keys.pop(0)
        node.values.pop(0)

        if not left_node.leaf:
            left_node.values[-1].parent = left_node
        return node.parent, old_min_key, new_min_key

    def _right_rotate(self, node: BPlusTreeNode) -> tuple[BPlusTreeNode, int, int]:
        """Move rightmost key/child from node to right sibling."""
        logger.debug(
            f"{BLUE}Rotate to right, keys: {node.keys} -> {node.next.keys}{RESET}"
        )
        right_node = node.next

        if len(node.keys) - 1 < math.ceil(self.order / 2):
            logger.debug(
                f"{RED}Right rotate not possible. len(keys): {len(node.keys)}{RESET}"
            )
            raise TypeError("Right rotate not possible")

        # old and new minimum key of right sibling
        old_min_key = self._search_min_key_in_subtree(right_node.values[0])
        new_min_key = self._search_min_key_in_subtree(node.values[-1])

        # if it's a non-leaf node, move only the rightmost child because it will be
        # in the leftmost position in right sibling, otherwise, also move the key
        # because key = value in leaf nodes.
        right_node.keys.insert(0, new_min_key if node.leaf else old_min_key)
        right_node.values.insert(0, node.values[-1])

        node.keys.pop()
        node.values.pop()

        if not right_node.leaf:
            right_node.values[0].parent = right_node
        return right_node.parent, old_min_key, new_min_key

    def _left_redistribute(
        self, node: BPlusTreeNode, idx: int
    ) -> tuple[BPlusTreeNode, int, int]:
        """Borrow from or merge with left sibling."""
        left_node = node.prev
        if left_node is None:
            raise TypeError("Left sibling not found")

        if len(node.keys) + len(left_node.keys) > self.order:
            raise TypeError("Left redistribute not possible")

        # merge
        logger.debug(f"{BLUE}Left merge, keys: {node.keys} + {left_node.keys}{RESET}")
        old_min_key = self._search_min_key_in_subtree(node.values[0])
        if idx == 0:
            new_min_key = self._search_min_key_in_subtree(node.next.values[0])
        else:
            new_min_key = old_min_key
        merged_keys = node.keys if node.leaf else [old_min_key] + node.keys
        left_node.keys.extend(merged_keys)
        left_node.values.extend(node.values)

        # remove key and child from direct parent
        key_idx = idx if idx == 0 else idx - 1
        node.parent.keys.pop(key_idx)
        node.parent.values.pop(idx)

        if not node.leaf:
            for child in left_node.values:
                child.parent = left_node

        # concatenate the doubly linked list
        left_node.next = node.next
        if node.next:
            node.next.prev = left_node
        return node.parent, old_min_key, new_min_key

    def _right_redistribute(
        self, node: BPlusTreeNode
    ) -> tuple[BPlusTreeNode, int, int]:
        """Borrow from or merge with right sibling."""
        right_node = node.next

        # merge, only happend at left most node
        # if len(node.keys) + len(right_node.keys) <= self.order:
        logger.debug(f"{BLUE}Right merge, keys: {node.keys} + {right_node.keys}{RESET}")
        new_min_key = self._search_min_key_in_subtree(right_node.values[0])
        merged_keys = node.keys if node.leaf else node.keys + [new_min_key]
        right_node.keys = merged_keys + right_node.keys
        right_node.values = node.values + right_node.values

        node.parent.keys.pop(0)
        node.parent.values.pop(0)

        if not node.leaf:
            for child in right_node.values:
                child.parent = right_node

        right_node.prev = None
        return None, -1, -1

    def _update_parents(
        self, node: BPlusTreeNode, old_min_key: int, new_min_key: int
    ) -> None:
        """Update minimum keys in ancestors after changes."""
        while node:
            try:
                node.keys[node.keys.index(old_min_key)] = new_min_key
            except ValueError:
                pass
            node = node.parent

    @_display_bplus_tree
    def insert(self, data: int) -> None:
        """Insert data into tree, maintaining B+ tree properties."""
        logger.info(f"{GREEN}>> Insert: {data}{RESET}")

        # insert into leaf node
        path = []
        curr_node = self.root
        while not curr_node.leaf:
            curr_node, idx = self._search_position_in_child(curr_node, data)
            path.append(idx)
        curr_node.add(data)

        while curr_node is not None and curr_node.is_overflow():
            curr_node.split()
            if curr_node.parent is not None:
                self._merge_into_parent(curr_node, path.pop())

            curr_node = curr_node.parent

    @_display_bplus_tree
    def delete(self, data: int) -> None:
        """Delete data from tree, maintaining B+ tree properties."""
        logger.info(f"{GREEN}>> Delete: {data}{RESET}")

        path = []
        curr_node = self.root
        while not curr_node.leaf:
            curr_node, idx = self._search_position_in_child(curr_node, data)
            path.append(idx)

        try:
            base, old_min_key, new_min_key = curr_node.remove(data)
        except TypeError:
            return  # lazy return
        self._update_parents(base, old_min_key, new_min_key)

        # loop because current node's parent may underflow if merge happend
        while (
            curr_node is not None
            and curr_node.parent is not None
            and curr_node.is_underflow()
        ):
            # try rotate first
            if curr_node.next:
                try:
                    self._update_parents(*self._left_rotate(curr_node.next))
                    return
                except TypeError:
                    pass
            if curr_node.prev:
                try:
                    self._update_parents(*self._right_rotate(curr_node.prev))
                    return
                except TypeError:
                    pass

            try:
                self._update_parents(*self._left_redistribute(curr_node, path.pop()))
            except TypeError:
                self._update_parents(*self._right_redistribute(curr_node))

            curr_node = curr_node.parent

        # there may be only one non-leaf and one leaf node after redistribution
        # if so, promote the only leaf node to root
        if not self.root.leaf and len(self.root.values) <= 1:
            self.root = self.root.values[0]
            self.root.parent = None

    def display(self) -> None:
        """Print tree structure."""
        logger.info(f">> Display")
        print(self.root.show())

    def find(self, data: int) -> None:
        """Search for data in tree."""
        curr_node = self.root
        while not curr_node.leaf:
            curr_node, _ = self._search_position_in_child(curr_node, data)

        try:
            curr_node.keys.index(data)
            print(f">> Key found: {data}")
        except ValueError:
            print(f">> Key not found: {data}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--display", action="store_true", help="display after operation"
    )
    parser.add_argument("--logging", action="store_true", help="enable logging")
    parser.add_argument("--debug", action="store_true", help="enable debug logging")
    parser.add_argument(
        "--plain",
        action="store_true",
        help="display without ASCII tree format",
    )
    args = parser.parse_args()

    # ===================== Settings ===================== #
    DISPLAY_AFTER_OPERATION = args.display or args.debug
    LOGGING_ENABLED = args.logging or args.debug
    LOG_LEVEL = logging.DEBUG if args.debug else logging.INFO
    PLAIN_DISPLAY = args.plain

    # ===================== Logging ===================== #
    handler = logging.StreamHandler()
    logger.setLevel(LOG_LEVEL)
    if LOGGING_ENABLED:
        logger.addHandler(handler)

    # ===================== Test ===================== #
    print("========== Example 1 in Lecture 8 ==========")
    tree1 = BPlusTree(3)
    values = [1, 3, 5, 9, 10, 12, 13]
    for value in values:
        tree1.insert(value)
    tree1.delete(10)
    tree1.insert(10)
    tree1.find(10)
    tree1.display()
    print("========== Insert 6 ==========")
    tree1.insert(6)
    tree1.display()
    print("========== Try delete 1 twice ==========")
    tree1.delete(1)
    tree1.delete(1)
    tree1.display()
    print("========== Try insert 6 again ==========")
    tree1.insert(6)
    tree1.display()

    print("\n\n========== Example 2 in Lecture 8 ==========")
    tree2 = BPlusTree(4)
    values = [
        1,
        3,
        5,
        7,
        9,
        11,
        13,
        14,
        20,
        21,
        23,
        15,
    ]
    for value in values:
        tree2.insert(value)
    tree2.insert(17)
    tree2.display()
    tree2.insert(16)
    tree2.display()

    print("\n\n========== Example 3 in Lecture 8 ==========")
    tree3 = BPlusTree(3)
    values = [1, 3, 5, 6, 9, 10, 12]
    for value in values:
        tree3.insert(value)
    tree3.display()
    tree3.delete(6)
    tree3.delete(1)
    tree3.delete(10)
    tree3.delete(9)
    tree3.find(10)
    tree3.display()

    print("\n\n========== Example 4 in Lecture 8 ==========")
    tree4 = BPlusTree(4)
    values = [1, 3, 5, 7, 9, 11, 13, 15, 17, 20, 21, 23, 19]
    for value in values:
        tree4.insert(value)
    tree4.delete(20)
    tree4.insert(20)
    tree4.display()
    tree4.delete(15)
    tree4.delete(19)
    tree4.display()

    print("\n\n========== Basic Operations ==========")
    # Create a B+ Tree with order 4
    tree = BPlusTree(4)

    # Insert values
    tree.insert(10)
    tree.insert(20)
    tree.insert(5)

    # Search for a value
    tree.find(10)  # Outputs: ">> Key found: 10"

    # Delete a value
    tree.delete(20)

    # Display the tree
    tree.display()
