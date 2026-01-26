Is your feature request related to a problem? Please describe.

The system in its current design raises a pydantic.error_wrappers.ValidationError when

using JSON fields on both Pydantic and DB (SQLalchemy) objects,
AND the given value for the JSON field is not a string. (traceback below)
For instance, the following will not work out of the box for oher types than str
(the base structure comes from https://github.com/tiangolo/full-stack-fastapi-postgresql)

# in models/item.py
###
from pydantic import BaseModel, Json

class Item(BaseModel):
    value: Json = None

# in db_models/item.py
###
from sqlalchemy import Column, JSON
from app.db.base_class import Base

class Item(Base):
    value = Column(JSON)

# in crud/item.py
###
from app.db_models.item import Item

def get(db_session: Session, *, item_id: int) -> Optional[Item]:
    return db_session.query(Item).filter(Item.id == item_id).first()

# in endpoints/item.py
###
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.api.utils.db import get_db
from app.models.rule import Item

router = APIRouter()

@router.get("/{item_id}", response_model=Item)
def get_rule(*, db: Session = Depends(get_db), item_id: int):
    return crud.rule.get(db, item_id=item_id)
The following exception will occur:

ERROR: Exception in ASGI application
Traceback (most recent call last):
  File "/usr/local/lib/python3.7/site-packages/uvicorn/protocols/http/httptools_impl.py", line 372, in run_asgi
    result = await asgi(self.receive, self.send)
  File "/usr/local/lib/python3.7/site-packages/starlette/middleware/errors.py", line 125, in asgi
    raise exc from None
  File "/usr/local/lib/python3.7/site-packages/starlette/middleware/errors.py", line 103, in asgi
    await asgi(receive, _send)
  File "/usr/local/lib/python3.7/site-packages/starlette/middleware/base.py", line 27, in asgi
    response = await self.dispatch_func(request, self.call_next)
  File "./app/main.py", line 36, in db_session_middleware
    response = await call_next(request)
  File "/usr/local/lib/python3.7/site-packages/starlette/middleware/base.py", line 44, in call_next
    task.result()
  File "/usr/local/lib/python3.7/site-packages/starlette/middleware/base.py", line 37, in coro
    await inner(request.receive, queue.put)
  File "/usr/local/lib/python3.7/site-packages/starlette/exceptions.py", line 74, in app
    raise exc from None
  File "/usr/local/lib/python3.7/site-packages/starlette/exceptions.py", line 63, in app
    await instance(receive, sender)
  File "/usr/local/lib/python3.7/site-packages/starlette/routing.py", line 41, in awaitable
    response = await func(request)
  File "/usr/local/lib/python3.7/site-packages/fastapi/routing.py", line 84, in app
    field=response_field, response=raw_response
  File "/usr/local/lib/python3.7/site-packages/fastapi/routing.py", line 33, in serialize_response
    raise ValidationError(errors)
pydantic.error_wrappers.ValidationError: 1 validation error
response -> value
  str type expected (type=type_error.str)
Describe the solution you'd like

I would like that the JSON fields from SQL objects are properly casted to their twin field on the pydantic object (i.e, the example above should to work out of the box)

Describe alternatives you've considered
Declare a validator that calls json.dumps on a pydantic level

# in models.py
import json
from pydantic import BaseModel, Json, validator

class Item(BaseModel):
    value: Json = None

    @validator('value', pre=True)
    def decode_json(cls, v):
        if not isinstance(v, str):
            try:
                return json.dumps(v)
            except Exception as err:
                raise ValueError(f'Could not parse value into valid JSON: {err}')

        return v

# all other files keep identical
...
It is a workaround, but requires the developper to implement this same validator for every new class he uses...