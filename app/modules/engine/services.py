from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models.rule import Rule
from app.database.models.user import User
from app.modules.evaluations.schemas import EvaluationCreate, EvaluationRuleCreate
from app.modules.evaluations.services import create_evaluation_service


async def engine_service(
    input_data: dict, current_user: User, db: AsyncSession
) -> dict:
    query_result = await db.execute(
        select(Rule)
        .options(
            selectinload(Rule.conditions),
            selectinload(Rule.action),
        )
        .where(
            Rule.user_id == current_user.id,
            Rule.is_active.is_(True),
        )
        .order_by(Rule.priority.desc())
    )

    rules = query_result.scalars().all()
    evaluation_input = input_data.copy()
    results: list[EvaluationRuleCreate] = []

    for rule in rules:
        condition_results = []

        for condition in rule.conditions:
            input_value = input_data.get(condition.field)

            result = condition.operator.evaluate(
                input_value,
                condition.value,
            )

            condition_results.append(result)

        rule_result = condition_results[0]

        if len(condition_results) > 1 and rule.logical_operator is not None:
            for idx in range(1, len(condition_results)):
                rule_result = rule.logical_operator.evaluate(
                    rule_result,
                    condition_results[idx],
                )

        if rule_result:
            input_data[rule.action.field] = rule.action.value

        results.append(
            EvaluationRuleCreate(
                rule_id=rule.id,
                is_matched=rule_result,
                resulting_input=input_data.copy(),
            )
        )

    payload = EvaluationCreate(input=evaluation_input)

    await create_evaluation_service(payload, results, current_user, db)

    return input_data
