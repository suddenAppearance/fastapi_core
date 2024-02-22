## Fastapi Core

`fastapi_core` is a Python package providing reusable components for building MVC applications
consisting of controllers layer, services layer and repositories level. 
It is fully type-hinted and brings a nice experience in developing FastAPI app. 

### Installation

`fastapi_core` is not available from [PyPI](https://pypi.org) yet, you can install it via poetry:

```bash
poetry add git+ssh://git@github.com:suddenAppearance/fastapi_core.git
```

### Documentation

Documentation is in progress

### Usage Example

If your project uses SQLAlchemy, you can add transactions middleware to your project:

```python
from fastapi import FastAPI
from fastapi_core.middleware.database import transactional_middleware_factory
from fastapi_core.database.sessions import get_session_factories, get_engines
from fastapi_core.settings.database import DatabaseSettings

# DatabaseSettings are Pydantic BaseSettings object, DATABASE_URL env variable is required to initialize it
settings = DatabaseSettings()
# creating engines. In this example database url scheme is postgresql+asyncpg://
engine, async_engine = get_engines(settings.DATABASE_URL.replace("+asyncpg", ""), settings.DATABASE_URL)
# creating sessions via created engines
create_session, create_async_session = get_session_factories(engine, async_engine)


app = FastAPI(title="Transactions middleware example")

# sessions are lazy and won't be acquired from connection pool until the first call to .session from repositories
app.middleware("http")(transactional_middleware_factory(create_async_session=create_async_session))
```

You can use `BaseRepository` as base class for repositories layer classes. It comes with helpful methods
```python
from fastapi_core.repositories.base import BaseRepository
from fastapi_core.database.models import ExtendedBase
from sqlalchemy.orm import declarative_base
from sqlalchemy import select, update

from typing import Any

Base = declarative_base()
class ExampleModel(Base, ExtendedBase):
    # ExtendedBase adds incremental id field and created_at, updated_at timezone aware datetime fields
    __tablename__ = "example"
    ...

class RepositoryExample(BaseRepository[ExampleModel]):
    async def get_all_examples(self):
        statement = select(ExampleModel)
        
        # wrapper for (await session.execute()).scalars().all()
        return await self.all(statement)
    
    async def get_by_id(self, id: int):
        statement = select(ExampleModel).where(ExampleModel.id == id)

        # wrapper for (await session.execute()).scalars().one_or_none()
        return await self.one_or_none(statement)
    
    async def update_by_id(self, id: int, **fields: Any):
        statement = update(ExampleModel).values(...).where(ExampleModel.id == id)
    
        # wrapper for await session.execute() for convenience
        return await self.execute(statement)
```
Commit is done right before the request is returned. If transaction fails - it rolls back, releases connection
and returns 500.

Service layer classes can also optionally use transactions:

```python
from fastapi_core.services.base import BaseServiceWithSession as BaseService
# if you don't want to use transactions, use BaseServiceWithoutSession instead

# from previous steps
class RepositoryExample:
    ...

class ServiceWithSessionExample(BaseService):
    @property
    def repository(self):
        # all BaseService*.*factory(...) methods are lazy initilizers for objects.
        # That means that RepositoryExample will only initialize once
        # for ServiceWithSessionExample object (note: object, not class)
        return self.repo_factory(RepositoryExample)
    
```
You can also create gateways (external API callers). They should be paired with `httpx.AsyncClient`:

```python
from fastapi_core.gateways.base import BaseGateway, get_async_client

# this will configure client timeouts with fastapi_core.settings.httpx.HTTPXConfig
gateway_example_client = get_async_client('https://example.com/')

class GatewayExample(BaseGateway):
    async def example_call(self):
        return await self.get(...)

gateway_example = GatewayExample(gateway_example_client, {})
```

`BaseGateway.__init__()` requires `httpx.AsyncClient` and headers mapping as arguments.
Headers are usually passed from fastapi request to subsequent requests (authorization, tracing, etc.)
Initialization could be done via `BaseService.gateway_factory()`, e.g:

```python
from fastapi_core.services.base import BaseService

# from previous steps
gateway_example_client = ...
class GatewayExample(...):
    ...

class ServiceExample(BaseService):
    @property
    def gateway_example(self):
        return self.gateway_factory(GatewayExample, gateway_example_client)

```
This will create `GatewayExample` object and will pass `BaseService._container.headers` on every gateway request.

You can also use FastAPI dependency injection to initiate services inside controllers:

```python
from fastapi import APIRouter, Depends
from fastapi_core.controllers.dependencies import get_service

router = APIRouter()

# from previous steps:
class ServiceExample:
    ...

@router.get("/")
async def example(
    service: ServiceExample = Depends(get_service(ServiceExample))
):
    return await service.do_smth()
```

`get_service()` will automatically create container from `request.state`, detect whether `*WithSession` or `*WithoutSession` base is used
and will pass session, create logger with `api.{service.__name__}` name, accessible via `service.logger`, 
and will pass request headers to `service._container.headers`. 

### Contribution, Bug Reports

Report bugs and feature proposals at `Issues` tab, or feel free to open PR and discuss

### Few more words

This project is in active development and is aiming to speed up writing code for complex python Apps

### Testing

Testing and coverage are planned to be soon. Until that, please freeze the version you are using by setting revision tag