import operator
from functools import reduce
from typing import Tuple, Type
from django.db.models import Q, QuerySet
from django.http import QueryDict
from django.core.exceptions import FieldError


class Rule:
    name: str = ""
    verbose_name: str = ""
    key: str = ""

    def __init__(self):
        self.rule_body = None

    def process(self, request_fields: QueryDict, queryset: QuerySet) -> QuerySet:
        return queryset

    def validate(self, request_fields: QueryDict, queryset: QuerySet) -> QuerySet:
        if self.key not in request_fields:
            return queryset
        elif request_fields.get(self.key) and request_fields.get(self.key) != '':
            self.rule_body = request_fields.get(self.key)
            return self.process(request_fields, queryset)
        else:
            return queryset


class QueryRuleset:
    def __init__(self, *args: Type[Rule]):
        self.rules: Tuple[Type[Rule], ...] = args

    def apply_ruleset(self, request_fields: QueryDict, queryset: QuerySet):
        for rule in self.rules:
            queryset = rule().validate(request_fields, queryset)
        return queryset


class OrderingRule(Rule):
    key = "order"

    def __init__(self):
        super().__init__()
        self.ordering: str = ''

    def process(self, request_fields: QueryDict, queryset: QuerySet) -> QuerySet:
        if request_fields.get('ordering'):
            if request_fields.get('ordering') in ('desc', 'asc'):
                self.ordering = request_fields.get('ordering')
        to_order = self.rule_body.split(',')
        for field in to_order:
            key = field
            if self.ordering == 'desc':
                key = '-' + key
            try:
                list(queryset.order_by(key))
                queryset = queryset.order_by(key)
            except FieldError:
                return queryset
        return queryset


class NameRule(Rule):
    key = "name"

class TagNameContainsRule(Rule):
    key = "tags"
    pass


class IngredientRule(Rule):
    key = "ingredients"

    def process(self, request_fields: QueryDict, queryset: QuerySet) -> QuerySet:
        if not isinstance(self.rule_body, str):
            return queryset
        else:
            terms = self.rule_body.split(",")
            ingredient_terms = [Q(recipeingredient__meta__name__icontains=term) for term in terms]
            query = reduce(operator.and_, ingredient_terms)
            return queryset.filter(query)


class IngredientExclusionRule(Rule):
    key = "exclude"

    def process(self, request_fields: QueryDict, queryset: QuerySet) -> QuerySet:
        if not isinstance(self.rule_body, str):
            return queryset
        else:
            terms = self.rule_body.split(",")
            ingredient_terms = [~Q(recipeingredient__meta__name__icontains=term) for term in terms]
            query = reduce(operator.and_, ingredient_terms)
            return queryset.filter(query)


class CookwareRule(Rule):
    key = "cookware"

    def process(self, request_fields: QueryDict, queryset: QuerySet) -> QuerySet:
        if not isinstance(self.rule_body, str):
            return queryset
        else:
            terms = self.rule_body.split(",")
            ingredient_terms = [Q(equipment_set__name__icontains=term) for term in terms]
            query = reduce(operator.and_, ingredient_terms)
            return queryset.filter(query)


class AuthorNameRule(Rule):
    key = "author"

    def process(self, request_fields: QueryDict, queryset: QuerySet) -> QuerySet:
        if not isinstance(self.rule_body, str):
            return queryset
        else:
            terms = self.rule_body.split(",")
            ingredient_terms = [Q(author__name__icontains=term) for term in terms]
            query = reduce(operator.or_, ingredient_terms)
            return queryset.filter(query)

# class ListContainsRule(Rule):
#     key = "contains"
#     pass


# class TagJSONRulesetParser:
#     json_str = ""
#     registered_rules = (OrderingRule, ListContainsRule)
#     pass


# class TagFilters:
#     def to_json(self):
#         pass
