First Check

I added a very descriptive title to this issue.

I used the GitHub search to find a similar issue and didn't find it.

I searched the FastAPI documentation, with the integrated search.

I already searched in Google "How to X in FastAPI" and didn't find any information.

I already read and followed all the tutorial in the docs and didn't find an answer.

I already checked if it is not related to FastAPI but to Pydantic.

I already checked if it is not related to FastAPI but to Swagger UI.

I already checked if it is not related to FastAPI but to ReDoc.
Commit to Help

I commit to help with one of those options 👆
Example Code
import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

liveness = True

router = APIRouter()


@router.get(
    "/livez",
    summary="Liveness probe",
    description="Returns 200 if the service is alive",
)
async def get_liveness() -> JSONResponse:
    logging.debug("GET /livez")
    if liveness:
        return JSONResponse(status_code=200, content={"status": "ok"})
    else:
        return JSONResponse(status_code=500, content={"status": "not ok"})
Description
With version 0.88.0, my unit tests run fine, I get no error. With version 0.89.0, I get the following error:

/root/.pyenv/versions/3.8/lib/python3.8/importlib/__init__.py:127: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
<frozen importlib._bootstrap>:1014: in _gcd_import
    ???
<frozen importlib._bootstrap>:991: in _find_and_load
    ???
<frozen importlib._bootstrap>:975: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:671: in _load_unlocked
    ???
/root/.pyenv/versions/3.8/lib/python3.8/site-packages/_pytest/assertion/rewrite.py:168: in exec_module
    exec(co, module.__dict__)
tests/models/conftest.py:7: in <module>
    from my_sample_lib.main import app
my_sample_lib/main.py:10: in <module>
    from my_sample_lib.health.router import router as health_router
my_sample_lib/health/router.py:24: in <module>
    async def get_liveness() -> JSONResponse:
/root/.pyenv/versions/3.8/lib/python3.8/site-packages/fastapi/routing.py:633: in decorator
    self.add_api_route(
/root/.pyenv/versions/3.8/lib/python3.8/site-packages/fastapi/routing.py:572: in add_api_route
    route = route_class(
/root/.pyenv/versions/3.8/lib/python3.8/site-packages/fastapi/routing.py:400: in __init__
    self.response_field = create_response_field(
/root/.pyenv/versions/3.8/lib/python3.8/site-packages/fastapi/utils.py:90: in create_response_field
    raise fastapi.exceptions.FastAPIError(
E   fastapi.exceptions.FastAPIError: Invalid args for response field! Hint: check that <class 'starlette.responses.JSONResponse'> is a valid pydantic field type
The only way I found to get rid of the error is to remove the type hint, which I don't really want. Also, I tried to follow the guidelines provided in your documentation without success.

Interestingly, the whole thing works fine (with the type hint and fastapi 0.89.0) under Windows 10. Under Ubuntu 22.10, it doesn't work at all (i.e. it provides the above message).

Operating System
Linux

Operating System Details
Under Windows 10, it works like a charm. Under Ubuntu 22.10, it fails with the provided error above.

FastAPI Version
0.89.0

Python Version
3.8.12

Additional Context
It is also failing with python 3.9, and 3.10.