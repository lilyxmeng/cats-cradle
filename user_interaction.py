"""CSC111 Winter 2023 Project: Cat's Cradle

This module contains classes and methods to represent the dialogue generator and related aspects needed for dialogue.

This file is copyright (c) 2023 by Edric Liu, Janet Fu, Nancy Hu, and Lily Meng.
"""
from __future__ import annotations
import discord
from dataclasses import dataclass
from typing import Optional
from constants import Biome, Context
import csv
from pathlib import Path


class Dialogue:
    """Generic display of text and image.

    Instance Attributes:
    - message: the text content, or None. Supports same text formatting as Discord.
    - image_path: the url for the image, or None. Direct image links (e.g. Imgur) are preferred.

    Representation Invariants:
    - self.message is a valid line of dialogue from dialogues.csv.
    """

    title: Optional[str]
    message: Optional[str]
    image_path: Optional[str] = None

    def __init__(self, title: Optional[str], message: Optional[str], image_path: Optional[str]) -> None:
        self.title = title
        self.message = message
        self.image_path = image_path

    def __eq__(self, __value: object) -> bool:
        """Returns True if two Dialogue objects are identical. Returns false if ___value is not a Dialogue object or is
        not equal.
        """
        if isinstance(__value, Dialogue):
            return self.title == __value.title and \
                self.message == __value.message and \
                self.image_path == __value.image_path
        return False

    def _is_pointer(self) -> bool:
        """Returns True if self.message is a pointer (begins with @).
        """
        return self.message[0] == "@"

    def embeddify(self, colour: Optional[discord.Colour] = None) -> discord.Embed:
        """Returns the dialogue in the form of an embedded message.
        """
        embed = discord.Embed(
            colour=colour,
            description=self.message,
            title=self.title
        )
        if self.image_path is not None:
            embed.set_image(url=self.image_path)
        return embed


@dataclass
class _CountedMessage:
    """An object representing the number of times a message has appeared in the gameplay.
    Used to balance out message occurances.

    Instance Attributes:
    - occurances: the number of times a message has appeared.
    - message: the corresponding message.
    """
    occurrences: int
    message: str


class DialogueGenerator:
    """A class that generates and returns the dialogue for a quest gameplay.

    Instance Attributes:
    - _entry: a mapping of the entry dialogues to how many times each has appeared in the gameplay.
    - _investigate: a mapping of the investigate dialogues to how many times each has appeared in the gameplay.
    - _previw: a mapping of the preview dialogues to how many times each has appeared in the gameplay.
    - _exit: a mapping of the exit dialogues to how many times each has appeared in the gameplay.
    """
    _entry: dict[str, list[_CountedMessage]]
    _investigate: dict[str, list[_CountedMessage]]
    _preview: dict[str, list[_CountedMessage]]
    _exit: dict[str, list[_CountedMessage]]

    def __init__(self, entry: dict[str, list[str]],
                investigate: dict[str, list[str]],
                preview: dict[str, list[str]],
                exit: dict[str, list[str]]) -> None:

        self._entry = {biome: self._get_initial_messages(entry[biome]) for biome in entry}
        self._investigate = {b: self._get_initial_messages(investigate[b]) for b in investigate}
        self._preview = {b: self._get_initial_messages(preview[b]) for b in preview}
        self._exit = {b: self._get_initial_messages(exit[b]) for b in exit}

    def get_random_message(self, biome: Biome, context: Context) -> str:
        """Returns a random message depending on the biome and context.

        Preconditions:
        - len(self._entry) > 0
        - len(self._investigate) > 0
        - len(self._preview) > 0
        - len(self._exit) > 0
        """
        biome_str = str(biome)[6:].lower()

        if context == Context.ENTER:
            pointers = self._entry[biome_str]
        elif context == Context.INVESTIGATE:
            pointers = self._investigate[biome_str]
        elif context == Context.PREVIEW:
            pointers = self._preview[biome_str]
        else:
            pointers = self._exit[biome_str]

        return self._get_random_message_helper(pointers)

    def _get_random_message_helper(self, messages: list[_CountedMessage]) -> str:
        """Helper function for self.get_random_message(). Returns a random message from the list of messages based on
        how many times each has shown up during gameplay.
        """
        least = min(messages, key=lambda m: m.occurrences)
        least.occurrences += 1
        return least.message

    def _get_initial_messages(self, messages: list[str]) -> list[_CountedMessage]:
        """Helper function for self.__init__. Returns the initial messages in the form of _CountedMessage objects.
        """
        return [_CountedMessage(0, message) for message in messages]


def load_dialogue_generator(file_paths: list[str]) -> DialogueGenerator:
    """Loads and returns the dialogue for the given paths.
    """

    dialogues_so_far = [{}, {}, {}, {}]

    for file_path in file_paths:
        biome = Path(file_path).stem

        dialogues = _read_dialogue(file_path)

        for i in range(0, 4):
            dialogues_so_far[i][biome] = dialogues[i]

    return DialogueGenerator(*dialogues_so_far)


def _read_dialogue(file_path: str) -> list[list[str], list[str], list[str], list[str]]:
    """Helper function for load_dialogue_generator(). Reads a csv file and returns a list corresponding to
    scenarios and their given dialogues.
    """

    with open(file_path, "r") as file:
        reader = csv.reader(file)
        next(reader)

        dialogue_per_biome = [[], [], [], []]

        for line in reader:
            for i in range(0, 4):
                dialogue_per_biome[i].append(line[i])

        return dialogue_per_biome
