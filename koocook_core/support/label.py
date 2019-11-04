import enum


@enum.unique
class Label(enum.Enum):
    WARNING = enum.auto()
    CLEARANCE = enum.auto()
    CUISINE = enum.auto()
    CATEGORY = enum.auto()