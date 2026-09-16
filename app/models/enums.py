import enum
import operator


class ComparisonOperator(enum.StrEnum):
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_OR_EQUALS = ">="
    LESS_OR_EQUALS = "<="

    def evaluate(self, left_value, right_value) -> bool:
        operators = {
            ComparisonOperator.EQUALS: operator.eq,
            ComparisonOperator.NOT_EQUALS: operator.ne,
            ComparisonOperator.GREATER_THAN: operator.gt,
            ComparisonOperator.LESS_THAN: operator.lt,
            ComparisonOperator.GREATER_OR_EQUALS: operator.ge,
            ComparisonOperator.LESS_OR_EQUALS: operator.le,
        }

        return operators[self](left_value, right_value)


class LogicalOperator(enum.StrEnum):
    AND = "AND"
    OR = "OR"

    def evaluate(self, left_condition, right_condition) -> bool:
        operators = {
            LogicalOperator.AND: operator.and_,
            LogicalOperator.OR: operator.or_,
        }

        return operators[self](left_condition, right_condition)
