import os
import json

from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

from llm import LLM
from settings import OUTPUTS_DIR, RECENT_QUERY_DIR, get_next_recent_query_counter
from typing import List


class TreeNode(ABC):
    def __init__(self, doc, model, task_name, task):
        self.doc = doc
        self.model = model
        self.task_name = task_name
        self.task = task
        self.children = []

    @abstractmethod
    def expand(self) -> List["TreeNode"]:
        raise NotImplemented

    def name(self):
        return f"{self.model}_{self.task_name}.json"

    def make_request_and_log(self, llm: LLM, prompt, stop):
        response = llm.get_completion(prompt=prompt, stop=stop)
        filename = os.path.join(RECENT_QUERY_DIR, str(get_next_recent_query_counter()))
        with open(filename, "w") as fp:
            data = {"prompt": prompt, "stop": stop, "response": response}
            json.dump(data, fp)
        return response

    def log(self, data):
        filename = os.path.join(OUTPUTS_DIR, self.name())
        with open(filename, "w") as fp:
            json.dump(data, fp)
            print(self.name(), 'saved')

    def get_children_votes(self):
        votes = {"True": 0, "False": 0, "Uncertain": 0, "Error": 0}
        for child in self.children:
            for vote, number in child.get_children_votes():
                votes[vote] += number
        return votes
