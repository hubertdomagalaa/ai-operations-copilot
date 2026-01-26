Discussed in #11577
Originally posted by pat-lasswell May 14, 2024

First Check

I added a very descriptive title here.

I used the GitHub search to find a similar question and didn't find it.

I searched the FastAPI documentation, with the integrated search.

I already searched in Google "How to X in FastAPI" and didn't find any information.

I already read and followed all the tutorial in the docs and didn't find an answer.

I already checked if it is not related to FastAPI but to Pydantic.

I already checked if it is not related to FastAPI but to Swagger UI.

I already checked if it is not related to FastAPI but to ReDoc.
Commit to Help

I commit to help with one of those options 👆
Example Code
import aiohttp
import asyncio
import math
import uvicorn

from fastapi import FastAPI, Query, Request, Response
from http import HTTPStatus
from typing import Annotated

app = FastAPI()

@app.get('/')
async def get(
        x: Annotated[float | None, Query(gt=0,                description='x')] = 1,
        y: Annotated[float | None, Query(allow_inf_nan=False, description='y')] = 0) -> str:

    assert x > 0
    assert not math.isnan(y) and not math.isinf(y)

    return 'OK'


async def main():

    config = uvicorn.Config(app, host='127.0.0.1', port=8001)
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())
    
    await asyncio.sleep(.1)

    async with aiohttp.ClientSession() as session:

        async with session.get('http://127.0.0.1:8001/?x=-1') as response:

            assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    
        async with session.get('http://127.0.0.1:8001/?y=inf') as response:

            assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    
    await server.shutdown()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
Description
I would expect the allow_inf_nan parameter to Query to restrict valid values in the same way that gt, etc do, resulting in a HTTP 422 status code when the constraint is violated. Instead, inf and nan values are passed to the route handler.

To reproduce, save the example code above in the current directory in a file named bug.py, then

docker run -it --rm -w `pwd` -v `pwd`:`pwd` python:3.10 bash
and in the bash prompt inside the container

pip install aiohttp==3.9.5 fastapi==0.111.0 uvicorn==0.29.0
python bug.py
The output will be similar to

INFO:     Started server process [4301]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     127.0.0.1:58094 - "GET /?x=-1 HTTP/1.1" 422 Unprocessable Entity
INFO:     127.0.0.1:58094 - "GET /?y=inf HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "/layer_svc/test/env/lib/python3.10/site-packages/uvicorn/protocols/http/httptools_impl.py", line 411, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
  File "/layer_svc/test/env/lib/python3.10/site-packages/uvicorn/middleware/proxy_headers.py", line 69, in __call__
    return await self.app(scope, receive, send)
  File "/layer_svc/test/env/lib/python3.10/site-packages/fastapi/applications.py", line 1054, in __call__
    await super().__call__(scope, receive, send)
  File "/layer_svc/test/env/lib/python3.10/site-packages/starlette/applications.py", line 123, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/layer_svc/test/env/lib/python3.10/site-packages/starlette/middleware/errors.py", line 186, in __call__
    raise exc
  File "/layer_svc/test/env/lib/python3.10/site-packages/starlette/middleware/errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "/layer_svc/test/env/lib/python3.10/site-packages/starlette/middleware/exceptions.py", line 65, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/layer_svc/test/env/lib/python3.10/site-packages/starlette/_exception_handler.py", line 64, in wrapped_app
    raise exc
  File "/layer_svc/test/env/lib/python3.10/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    await app(scope, receive, sender)
  File "/layer_svc/test/env/lib/python3.10/site-packages/starlette/routing.py", line 756, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/layer_svc/test/env/lib/python3.10/site-packages/starlette/routing.py", line 776, in app
    await route.handle(scope, receive, send)
  File "/layer_svc/test/env/lib/python3.10/site-packages/starlette/routing.py", line 297, in handle
    await self.app(scope, receive, send)
  File "/layer_svc/test/env/lib/python3.10/site-packages/starlette/routing.py", line 77, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/layer_svc/test/env/lib/python3.10/site-packages/starlette/_exception_handler.py", line 64, in wrapped_app
    raise exc
  File "/layer_svc/test/env/lib/python3.10/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    await app(scope, receive, sender)
  File "/layer_svc/test/env/lib/python3.10/site-packages/starlette/routing.py", line 72, in app
    response = await func(request)
  File "/layer_svc/test/env/lib/python3.10/site-packages/fastapi/routing.py", line 278, in app
    raw_response = await run_endpoint_function(
  File "/layer_svc/test/env/lib/python3.10/site-packages/fastapi/routing.py", line 191, in run_endpoint_function
    return await dependant.call(**values)
  File "/layer_svc/app/bug.py", line 85, in get
    assert not math.isnan(y) and not math.isinf(y)
AssertionError
Traceback (most recent call last):
  File "/layer_svc/app/bug.py", line 111, in <module>
    asyncio.get_event_loop().run_until_complete(main())
  File "/usr/lib/python3.10/asyncio/base_events.py", line 649, in run_until_complete
    return future.result()
  File "/layer_svc/app/bug.py", line 106, in main
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
AssertionError
The expected response is

INFO:     Started server process [4301]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     127.0.0.1:58094 - "GET /?x=-1 HTTP/1.1" 422 Unprocessable Entity
INFO:     127.0.0.1:58094 - "GET /?y=inf HTTP/1.1" 422 Unprocessable Entity
Operating System
Linux

Operating System Details
No response

FastAPI Version
0.111.0

Pydantic Version
2.7.1

Python Version
3.10.14

Additional Context
No response