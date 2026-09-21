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
from app.database.dependencies import get_db
from app.main import app
from app.models import Rule, User
from app.modules.actions.schemas import ActionCreate
from app.modules.actions.services import create_action_service
from app.modules.conditions.schemas import ConditionCreate
from app.modules.conditions.services import create_condition_service

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
async def clean_conditions():
    async with test_engine.connect() as connection:
        await connection.execute(text("TRUNCATE TABLE conditions CASCADE"))
        await connection.commit()


@pytest_asyncio.fixture
async def client():
    async def override_get_db():
        async with test_session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def condition(db_session):
    payload = ConditionCreate(
        field="temperature",
        operator=">",
        value=25,
    )

    return await create_condition_service(payload, db_session)


@pytest_asyncio.fixture
async def condition_data(client):
    payload = {
        "field": "temperature",
        "operator": ">",
        "value": 25,
    }

    response = await client.post(
        "/api/v1/conditions/",
        json=payload,
    )

    assert response.status_code == 201

    return response.json()


@pytest_asyncio.fixture
async def user(db_session):
    user = User(
        nickname="testuser",
        email="test@example.com",
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def rule(db_session, user):
    rule = Rule(
        user_id=user.id,
        name="Test rule",
        description="Test rule description",
        logical_operator=None,
        priority=1,
        is_active=True,
    )

    db_session.add(rule)
    await db_session.commit()
    await db_session.refresh(rule)

    return rule


@pytest_asyncio.fixture
async def rules(db_session, user):
    result = []

    for i in range(5):
        rule = Rule(
            user_id=user.id,
            name=f"Test rule {i}",
            description=f"Test rule {i}",
            logical_operator=None,
            priority=i + 1,
            is_active=True,
        )

        db_session.add(rule)
        result.append(rule)

    await db_session.commit()

    for rule in result:
        await db_session.refresh(rule)

    return result


@pytest_asyncio.fixture
async def action(db_session, rule):
    payload = ActionCreate(
        field="temperature",
        value=15.5,
    )

    return await create_action_service(
        rule_id=rule.id,
        payload=payload,
        db=db_session,
    )


@pytest_asyncio.fixture
async def actions(db_session, rules):
    result = []

    for i, rule in enumerate(rules):
        payload = ActionCreate(
            field=f"temperature_{i}",
            value=i,
        )

        action = await create_action_service(
            rule_id=rule.id,
            payload=payload,
            db=db_session,
        )

        result.append(action)

    return result
