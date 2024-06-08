#!/usr/bin/python3

from typing import Union

from graphviz import Digraph
from termcolor import colored


class FSM:
    def __init__(self, regexp: str):
        self.regexp = regexp
        self.start = FSM.State(is_start=True)
        self.end = FSM.State(is_end=True)
        self.split_and_compile()

    class Token:
        def __init__(
            self,
            range: Union[str, tuple[str, str]],
            negated: bool = False,
            escaped: bool = False,
        ):
            if isinstance(range, tuple):
                start, end = range
            else:
                start, end = range, range
            self.start = start
            self.end = end
            self.length = ord(end) - ord(start) + 1
            self.negated = negated
            self.escaped = escaped

        def __contains__(self, char: str) -> bool:
            return (self.start <= char <= self.end) ^ self.negated

        def __repr__(self) -> str:
            if "END" == self.start:
                return "END"
            if "\\" == self.start:
                return r"\\"
            pre = "^" if self.negated else "" + r"\\" if self.escaped else ""
            if self.length == 1:
                return f"{pre}{self.start}"
            return f"{pre}[{self.start}-{self.end}]"

    state_counter = 1

    class State:
        def __init__(self, is_start: bool = False, is_end: bool = False):
            self.id = FSM.state_counter
            FSM.state_counter += 0 if is_start or is_end else 1
            self.transitions = {}
            self.is_start = is_start
            self.is_end = is_end

        def __repr__(self) -> str:
            return "Start" if self.is_start else "End" if self.is_end else f"S{self.id}"

        def link(self, token: Union["FSM.Token", str], target: "FSM.State"):
            self.transitions[token] = target

    def split_and_compile(self):
        split_idxs = []
        for i, char in enumerate(self.regexp):
            if char == "|":
                if i > 0 and self.regexp[i - 1] == "\\":
                    continue
                split_idxs.append(i)

        prev = 0
        for split_idx in split_idxs:
            subexpr = self.regexp[prev:split_idx]
            prev = split_idx + 1
            self.compile(subexpr, self.start, self.end)

        subexpr = self.regexp[prev:]
        self.compile(subexpr, self.start, self.end)

    def compile(self, regexp: str, start: "FSM.State", end: "FSM.State"):
        current = start
        parents = []
        i = 0

        def build(
            tokens: Union["FSM.Token", set["FSM.Token"]],
            next_char: str,
            target: Union["FSM.State", None],
        ):
            nonlocal current, parents
            if next_char == "*":
                current, parent = link(tokens, current, current, parents)
                parents.append(parent)
            elif next_char == "+":
                current, _ = link(tokens, current, target, parents)
                link(tokens, target, target, parents)
                parents = []
            elif next_char == "?":
                current, parent = link(tokens, current, target, parents)
                parents.append(parent)
            else:
                current, _ = link(tokens, current, target, parents)
                parents = []

        def link(
            tokens: Union["FSM.Token", set["FSM.Token"], str],
            current: "FSM.State",
            target: "FSM.State",
            parents: list["FSM.State"],
        ):
            if isinstance(tokens, FSM.Token) or isinstance(tokens, str):
                tokens = {tokens}
            for token in tokens:
                current.link(token, target)
                for parent in parents:
                    parent.link(token, target)

            return target, current

        while i < len(regexp):
            char = regexp[i]
            if char in ("*", "+", "?"):
                i += 1
                continue

            if char == "[":
                i += 1
                negated = regexp[i] == "^"
                i += 1 if negated else 0
                tokens = set()
                while regexp[i] != "]":
                    escaped = False
                    if regexp[i] == "\\":
                        escaped = True
                        i += 1
                    if (
                        regexp[i + 1] == "-"
                        and regexp[i + 2] != "]"
                        and ord(regexp[i]) < ord(regexp[i + 2])
                    ):
                        tokens.add(
                            FSM.Token((regexp[i], regexp[i + 2]), negated, False)
                        )
                        i += 2
                    else:
                        tokens.add(FSM.Token(regexp[i], negated, escaped))
                    i += 1

                next_char = regexp[i + 1] if i < len(regexp) - 1 else None
                target = FSM.State() if next_char != "*" else None
                build(tokens, next_char, target)
            else:
                escaped = False
                if char == "\\":
                    escaped = True
                    i += 1
                    char = regexp[i]
                next_char = regexp[i + 1] if i < len(regexp) - 1 else None
                target = FSM.State() if next_char != "*" else None
                build(FSM.Token(char, escaped=escaped), next_char, target)
            i += 1

        for parent in parents:
            parent.link("END", end)
        parents = []
        link("END", current, end, parents)

    def match(self, string: str) -> set[int]:
        matched_chars = set()

        def transition(string, ptr, idx, start):
            nonlocal matched_chars
            char = string[idx] if idx < len(string) else None
            if idx in matched_chars:
                return
            for token in ptr.transitions:
                if "END" == token:
                    matched_chars.update(list(range(start, idx)))
                    continue

                if idx == len(string):
                    if "$" == token.start:
                        transition(string, ptr.transitions[token], idx, start)
                else:
                    if token.escaped:
                        if token.start in (
                            *("w", "W", "d", "D", "s", "S"),
                            *("t", "n", "v", "f", "r"),
                        ):
                            if (
                                ("w" == token.start and char.isalnum() or char == "_")
                                or (
                                    "W" == token.start
                                    and not char.isalnum()
                                    and char != "_"
                                )
                                or ("d" == token.start and char.isdigit())
                                or ("D" == token.start and not char.isdigit())
                                or ("s" == token.start and char.isspace())
                                or ("S" == token.start and not char.isspace())
                                or ("t" == token.start and ord(char) == 9)
                                or ("n" == token.start and ord(char) == 10)
                                or ("v" == token.start and ord(char) == 11)
                                or ("f" == token.start and ord(char) == 12)
                                or ("r" == token.start and ord(char) == 13)
                            ):
                                transition(
                                    string, ptr.transitions[token], idx + 1, start
                                )
                        elif token.start in ("b", "B"):
                            if (
                                (
                                    "b" == token.start
                                    and (idx == 0 or string[idx - 1].isspace())
                                    and string[idx].isalnum()
                                )
                                or (
                                    "b" == token.start
                                    and (
                                        idx == len(string) - 1
                                        or string[idx + 1].isspace()
                                    )
                                    and string[idx].isalnum()
                                )
                                or (
                                    "B" == token.start
                                    and not (idx == 0 or string[idx - 1].isspace())
                                    and string[idx].isalnum()
                                )
                                or (
                                    "B" == token.start
                                    and not (
                                        idx == len(string) - 1
                                        or string[idx + 1].isspace()
                                    )
                                    and string[idx].isalnum()
                                )
                            ):
                                transition(string, ptr.transitions[token], idx, start)
                        elif char in token:
                            transition(string, ptr.transitions[token], idx + 1, start)
                    else:
                        if idx == 0 and "^" == token.start:
                            transition(string, ptr.transitions[token], idx, start)

                        if char in token or "." == token.start:
                            transition(string, ptr.transitions[token], idx + 1, start)

        for idx, char in enumerate(string):
            transition(string, self.start, idx, idx)

        return matched_chars

    def plot(self, filename=None, view: bool = False):
        g = Digraph(format="png")
        g.attr(rankdir="LR", compound="true", concentrate="true")

        state_counter = 1
        states = [(self.start, "Start")]
        names = {id(self.start): "Start"}

        while states:
            ptr, ptr_name = states.pop()
            for token, target in ptr.transitions.items():
                if id(target) not in names:
                    target_name = target.__repr__()
                    names[id(target)] = target_name
                    state_counter += 1
                    states.append((target, target_name))
                else:
                    target_name = names[id(target)]

                g.edge(ptr_name, target_name, label=token.__repr__(), arrowhead="vee")

            if ptr.is_end:
                g.node(ptr_name, shape="doublecircle", color="red")
            elif ptr.is_start:
                g.node(ptr_name, shape="doublecircle", color="green")
            else:
                g.node(ptr_name, color="blue")

        if filename is None:
            filename = self.regexp.replace("*", "8")

        if view:
            g.view(cleanup=True)
        else:
            g.render(
                filename=rf"data/images/{filename}",
                format="png",
                cleanup=True,
            )


def highlight(string: str, matched_chars: set[int]) -> str:
    highlighted = list(string)

    highlighted = [
        colored(char, "red") if idx in matched_chars else char
        for idx, char in enumerate(highlighted)
    ]

    return "".join(highlighted)


regexp = input("Regular Expression: ")
fsm = FSM(regexp)

string = input("Sample string: ")
matched_chars = fsm.match(string)
highlighted = highlight(string, matched_chars)

print(highlighted)
