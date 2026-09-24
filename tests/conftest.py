import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.security import hash_password
from app.core.tokens import create_access_token
from app.database.dependencies import get_db
from app.database.models.user import User
from app.main import app
from app.modules.actions.schemas import ActionCreate
from app.modules.actions.services import create_action_service
from app.modules.conditions.schemas import ConditionCreate
from app.modules.conditions.services import create_condition_service
from app.modules.rules.schemas import RuleCreate
from app.modules.rules.services import create_rule_service
from app.modules.evaluations.schemas import EvaluationCreate, EvaluationRuleCreate
from app.modules.evaluations.services import create_evaluation_service

test_engine = create_async_engine(
    settings.database.test_database_url,
    poolclass=NullPool,
)

test_session_maker = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture
async def db_session():
    async with test_engine.connect() as connection:
        transaction = await connection.begin()

        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
        )

        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


@pytest_asyncio.fixture(autouse=True)
async def clean_database():
    async with test_engine.connect() as connection:
        await connection.execute(
            text(
                """
                TRUNCATE TABLE
                    conditions,
                    actions,
                    rules,
                    evaluations,
                    users
                CASCADE
                """
            )
        )
        await connection.commit()


@pytest_asyncio.fixture
async def authenticated_client(user, db_session):
    access_token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
        }
    )

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    ) as authenticated_client:
        yield authenticated_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user(db_session):
    user = User(
        nickname="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def another_user(db_session):
    another_user = User(
        nickname="anothertestuser",
        email="anothertest@example.com",
        hashed_password="another_hashed_password",
    )

    db_session.add(another_user)
    await db_session.commit()
    await db_session.refresh(another_user)

    return another_user


@pytest_asyncio.fixture
async def condition(user, db_session):
    payload = ConditionCreate(
        field="temperature",
        operator=">",
        value=25,
    )

    return await create_condition_service(
        payload=payload,
        current_user=user,
        db=db_session,
    )


@pytest_asyncio.fixture
async def condition_data(authenticated_client):
    payload = {
        "field": "temperature",
        "operator": ">",
        "value": 25,
    }

    response = await authenticated_client.post(
        "/api/v1/conditions/",
        json=payload,
    )

    assert response.status_code == 201

    return response.json()


@pytest_asyncio.fixture
async def action(user, db_session):
    payload = ActionCreate(
        field="temperature",
        value=15.5,
    )

    return await create_action_service(
        payload=payload,
        current_user=user,
        db=db_session,
    )


@pytest_asyncio.fixture
async def action_data(authenticated_client):
    payload = {
        "field": "temperature",
        "value": 15.5,
    }

    response = await authenticated_client.post(
        "/api/v1/actions/",
        json=payload,
    )

    assert response.status_code == 201

    return response.json()


@pytest_asyncio.fixture
async def rule(action, user, db_session):
    condition_ids = []

    for i in range(3):
        payload = ConditionCreate(
            field=f"temperature_{i}",
            operator="==",
            value=i,
        )

        condition = await create_condition_service(payload, user, db_session)
        condition_ids.append(condition.id)

    payload = RuleCreate(
        name="test_rule",
        description="test_rule_description",
        logical_operator="AND",
        priority=99,
        is_active=True,
        condition_ids=condition_ids,
        action_id=action.id,
    )

    return await create_rule_service(
        payload=payload,
        current_user=user,
        db=db_session,
    )


@pytest_asyncio.fixture
async def rule_data(condition_data, action_data, authenticated_client):
    payload = {
        "name": "test_rule",
        "description": "test_rule_description",
        "logical_operator": None,
        "priority": 99,
        "is_active": True,
        "condition_ids": [condition_data["id"]],
        "action_id": action_data["id"],
    }

    response = await authenticated_client.post(
        "/api/v1/rules/",
        json=payload,
    )

    assert response.status_code == 201

    return response.json()


@pytest_asyncio.fixture
async def evaluation(rule, user, db_session):
    payload = EvaluationCreate(
        input={"age": 25, "country": "US", "amount": 1500},
    )

    evaluation_result = EvaluationRuleCreate(
        rule_id=rule.id,
        is_matched=True,
        resulting_input={"age": 10, "country": "US", "amount": 1500},
    )

    return await create_evaluation_service(
        payload=payload,
        evaluation_results=[evaluation_result],
        current_user=user,
        db=db_session,
    )  
