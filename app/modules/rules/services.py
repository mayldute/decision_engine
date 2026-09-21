from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select, selectinload

from app.models import Action, Condition, Rule
from app.modules.rules.schemas import RuleCreate, RuleResponse


async def create_rule_service(
    payload: RuleCreate,
    db: AsyncSession,
) -> RuleResponse:

    rule = Rule(
        name=payload.name,
        description=payload.description,
        logical_operator=payload.logical_operator,
        priority=payload.priority,
        is_active=payload.is_active,
    )

    for condition_data in payload.conditions:
        condition = Condition(**condition_data.model_dump())
        rule.conditions.append(condition)

    action = Action(
        field=payload.action.field,
        value=payload.action.value,
        rule=rule,
    )

    db.add(rule)
    db.add(action)

    await db.commit()

    result = await db.execute(
        select(Rule)
        .options(
            selectinload(Rule.conditions),
            selectinload(Rule.action),
        )
        .where(Rule.id == rule.id)
    )

    rule = result.scalar_one()

    return RuleResponse.model_validate(rule)
