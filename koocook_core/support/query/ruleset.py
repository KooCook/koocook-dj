class Rule:
    name: str = ""
    verbose_name: str = ""
    key: str = ""
    pass


class Ruleset:
    def __init__(self):
        self.rules = []

    def add_rule(self, rule: Rule):
        self.rules.append(rule)


class OrderingRule(Rule):
    key = "order"
    pass


class ListContainsRule(Rule):
    key = "contains"
    pass


class TagNameContainsRule(Rule):
    key = "tags"
    pass


class TagJSONRulesetParser:
    json_str = ""
    registered_rules = (OrderingRule, ListContainsRule)
    pass


class TagFilters:
    def to_json(self):
        pass
