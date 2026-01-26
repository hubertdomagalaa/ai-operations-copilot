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
from fastapi import FastAPI, Request, Depends, APIRouter
from starlette_graphene3 import GraphQLApp, make_playground_handler
from shortest_path.schema import schema
from shortest_path.utils.security import get_api_key

graphql_app = GraphQLApp(
    schema=schema,
    on_get=make_playground_handler()
)


async def wrapper(req: Request) -> None:
    await graphql_app(req.scope, req.receive, req._send)

app = FastAPI()
router = APIRouter(tags=["graphql"])

router.add_api_route(
    "/graphql", wrapper, dependencies=[Depends(get_api_key)], include_in_schema=True, methods=["POST"]
)

router.add_api_route(
    "/graphql", wrapper, include_in_schema=True, methods=["GET"]
)

router.add_api_websocket_route("/graphql", graphql_app)
app.include_router(router)
Description
Dependencies are as follows:

fastapi = "==0.75.2"
uvicorn = {version = "==0.17.6", extras = ["standard"]}
gunicorn = "==20.1.0"
Executing in Dockerfile with following entry point:

CMD exec gunicorn --bind :8080 --workers 1 --worker-class uvicorn.workers.UvicornWorker --timeout 0 app.main:app
Calling my graphql endpoint doesn't result in any erroneous behaviour on the client side, but I end up with these logs.

[2022-05-03 05:49:08 +0000] [9] [ERROR] Exception in ASGI application
Traceback (most recent call last):
  File "/usr/local/lib/python3.8/site-packages/uvicorn/protocols/http/httptools_impl.py", line 372, in run_asgi
    result = await app(self.scope, self.receive, self.send)
  File "/usr/local/lib/python3.8/site-packages/uvicorn/middleware/proxy_headers.py", line 75, in __call__
    return await self.app(scope, receive, send)
  File "/usr/local/lib/python3.8/site-packages/fastapi/applications.py", line 261, in __call__
    await super().__call__(scope, receive, send)
  File "/usr/local/lib/python3.8/site-packages/starlette/applications.py", line 112, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.8/site-packages/starlette/middleware/errors.py", line 181, in __call__
    raise exc
  File "/usr/local/lib/python3.8/site-packages/starlette/middleware/errors.py", line 159, in __call__
    await self.app(scope, receive, _send)
  File "/usr/local/lib/python3.8/site-packages/starlette/exceptions.py", line 82, in __call__
    raise exc
  File "/usr/local/lib/python3.8/site-packages/starlette/exceptions.py", line 71, in __call__
    await self.app(scope, receive, sender)
  File "/usr/local/lib/python3.8/site-packages/fastapi/middleware/asyncexitstack.py", line 21, in __call__
    raise e
  File "/usr/local/lib/python3.8/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.8/site-packages/starlette/routing.py", line 656, in __call__
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.8/site-packages/starlette/routing.py", line 259, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.8/site-packages/starlette/routing.py", line 64, in app
    await response(scope, receive, send)
  File "/usr/local/lib/python3.8/site-packages/starlette/responses.py", line 149, in __call__
    await send(
  File "/usr/local/lib/python3.8/site-packages/starlette/exceptions.py", line 68, in sender
    await send(message)
  File "/usr/local/lib/python3.8/site-packages/starlette/middleware/errors.py", line 156, in _send
    await send(message)
  File "/usr/local/lib/python3.8/site-packages/uvicorn/protocols/http/httptools_impl.py", line 519, in send
    raise RuntimeError(msg % message_type)
RuntimeError: Unexpected ASGI message 'http.response.start' sent, after response already completed.
I can't pinpoint the exact cause of these logs or why exactly the ASGI server is emitting a message after the response has been sent.

Operating System
Linux

Operating System Details
Linux 5.10.60.1-microsoft-standard-WSL2 #1 SMP Wed Aug 25 23:20:18 UTC 2021 x86_64 x86_64 x86_64 GNU/Linux

FastAPI Version
0.75.2

Python Version
3.8

Additional Context
I have some I/O tasks in as part of my processing, e.g. where I do:
    results = await asyncio.gather(*[run_query(query) for query in queries], return_exceptions=True)
I also use starlette background tasks to perform after-response logging to other sinks, e.g.
    background.add_task(log_route_metrics, df, aisle_bay_pairs, optimal_route, totes)