class ConditionNotFoundError(Exception):
    pass


class ActionNotFoundError(Exception):
    pass


class RuleNotFoundError(Exception):
    pass


class RuleMustHaveConditionError(Exception):
    pass


class RuleNoLogicalOperator(Exception):
    pass
