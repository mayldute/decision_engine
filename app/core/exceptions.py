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


class EvaluationNotFoundError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserWrongPasswordError(Exception):
    pass


class UserAlreadyRegisteredError(Exception):
    pass


class TokenInvalidTypeError(Exception):
    pass


class TokenInvalidOrExpiredError(Exception):
    pass


class TokenUserIDMissingError(Exception):
    pass
