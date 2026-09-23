import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    RuleMustHaveConditionError,
    RuleNoLogicalOperator,
    RuleNotFoundError,
)
from app.database.models import Action, Condition, Rule, User
from app.modules.actions.services import get_action_or_raise
from app.modules.conditions.services import get_condition_or_raise
from app.modules.rules.schemas import (
    RuleCreate,
    RuleDeleteResponse,
    RuleResponse,
    RuleUpdate,
)


def get_rules_query():
    return select(Rule).options(
        selectinload(Rule.conditions),
        selectinload(Rule.action),
    )


async def get_rule_or_raise(
    rule_id: uuid.UUID, current_user: User, db: AsyncSession
) -> Rule:
    result = await db.execute(
        get_rules_query().where(Rule.id == rule_id, Rule.user_id == current_user.id)
    )

    rule = result.scalar_one_or_none()

    if rule is None:
        raise RuleNotFoundError(
            f"Rule with id {rule_id} for user with id {current_user.id} not found."
        )

    return rule


async def create_rule_service(
    payload: RuleCreate,
    current_user: User,
    db: AsyncSession,
) -> RuleResponse:

    conditions = []

    if payload.condition_ids is not None:
        for condition_id in payload.condition_ids:
            condition = await get_condition_or_raise(condition_id, db)
            conditions.append(condition)
    else:
        for new_condition in payload.new_conditions:
            condition = Condition(**new_condition.model_dump())
            db.add(condition)
            conditions.append(condition)

    if payload.action_id is not None:
        action = await get_action_or_raise(payload.action_id, db)
    else:
        action = Action(**payload.new_action.model_dump())
        db.add(action)

    rule = Rule(
        name=payload.name,
        description=payload.description,
        logical_operator=payload.logical_operator,
        priority=payload.priority,
        is_active=payload.is_active,
        conditions=conditions,
        action=action,
        user_id=current_user.id,
    )

    db.add(rule)
    await db.commit()

    result = await db.execute(get_rules_query().where(Rule.id == rule.id))

    rule = result.scalar_one()

    return RuleResponse.model_validate(rule)


async def get_all_rules_service(
    skip: int, limit: int, current_user: User, db: AsyncSession
) -> list[RuleResponse]:
    result = await db.execute(
        get_rules_query()
        .where(Rule.user_id == current_user.id)
        .order_by(Rule.id)
        .offset(skip)
        .limit(limit)
    )

    rules = result.scalars().all()

    return [RuleResponse.model_validate(rule) for rule in rules]


async def get_rule_service(
    rule_id: uuid.UUID, current_user: User, db: AsyncSession
) -> RuleResponse:
    rule = await get_rule_or_raise(rule_id, current_user, db)

    return RuleResponse.model_validate(rule)


async def update_rule_service(
    rule_id: uuid.UUID, payload: RuleUpdate, current_user: User, db: AsyncSession
) -> RuleResponse:
    rule = await get_rule_or_raise(rule_id, current_user, db)

    data = payload.model_dump(exclude_unset=True)

    condition_ids_data = data.pop("condition_ids", None)
    new_conditions_data = data.pop("new_conditions", None)
    action_id_data = data.pop("action_id", None)
    new_action_data = data.pop("new_action", None)

    if condition_ids_data is not None and not condition_ids_data:
        raise RuleMustHaveConditionError("At least one condition must be provided.")

    if new_conditions_data is not None and not new_conditions_data:
        raise RuleMustHaveConditionError("At least one condition must be provided.")

    # Replace conditions from existing IDs or create new ones.
    # Otherwise, keep the current conditions.
    if condition_ids_data is not None:
        conditions = []

        for condition_id in condition_ids_data:
            condition = await get_condition_or_raise(condition_id, db)
            conditions.append(condition)

        rule.conditions = conditions
    elif new_conditions_data is not None:
        conditions = []

        for new_condition in new_conditions_data:
            condition = Condition(**new_condition)
            db.add(condition)
            conditions.append(condition)

        rule.conditions = conditions
    else:
        conditions = rule.conditions

    # Replace the action with an existing one or create and assign a new action.
    if action_id_data is not None:
        rule.action = await get_action_or_raise(action_id_data, db)
    elif new_action_data is not None:
        action = Action(**new_action_data)
        db.add(action)
        rule.action = action

    # Clear the operator for a single condition; otherwise require one.
    if len(conditions) == 1:
        rule.logical_operator = None
    elif len(conditions) > 1:
        logical_operator = data.get(
            "logical_operator",
            rule.logical_operator,
        )

        if logical_operator is None:
            raise RuleNoLogicalOperator(
                "Rule must contain a logical operator if it contains "
                "more than one condition."
            )

    # Apply the remaining rule fields.
    for key, value in data.items():
        setattr(rule, key, value)

    await db.commit()

    result = await db.execute(get_rules_query().where(Rule.id == rule.id))

    rule = result.scalar_one()

    return RuleResponse.model_validate(rule)


async def delete_rule_service(
    rule_id: uuid.UUID, current_user: User, db: AsyncSession
) -> RuleDeleteResponse:
    rule = await get_rule_or_raise(rule_id, current_user, db)

    await db.delete(rule)
    await db.commit()

    return RuleDeleteResponse(
        message="Rule successfully deleted.",
        rule_id=rule_id,
    )
