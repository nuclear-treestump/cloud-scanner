import json
from .decorator import autolog
from .database_ops import fetch_entry_by_id


class RuleEngine:
    def __init__(self, rules):
        self.rules = rules

    def tokenize(self, condition):
        """
        Break evaluation condition strings into operators for parsing.
        """
