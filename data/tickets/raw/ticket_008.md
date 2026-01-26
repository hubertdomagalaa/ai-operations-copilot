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
from fastapi import FastAPI, status

app = FastAPI()


@app.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def read_root():
    return None
Description
Upon requesting above code I got expected response but my logs shows that there is an error in uvicorn. The problem exists for DELETE method and NoContent response status code (for HEAD there is no such problem)

ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "/home/user/PycharmProjects/sample_app/venv/lib/python3.9/site-packages/uvicorn/protocols/http/httptools_impl.py", line 372, in run_asgi
    result = await app(self.scope, self.receive, self.send)
  File "/home/user/PycharmProjects/sample_app/venv/lib/python3.9/site-packages/uvicorn/middleware/proxy_headers.py", line 75, in __call__
    return await self.app(scope, receive, send)
  File "/home/user/PycharmProjects/sample_app/venv/lib/python3.9/site-packages/fastapi/applications.py", line 269, in __call__
    await super().__call__(scope, receive, send)
  File "/home/user/PycharmProjects/sample_app/venv/lib/python3.9/site-packages/starlette/applications.py", line 124, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/home/user/PycharmProjects/sample_app/venv/lib/python3.9/site-packages/starlette/middleware/errors.py", line 184, in __call__
    raise exc
  File "/home/user/PycharmProjects/sample_app/venv/lib/python3.9/site-packages/starlette/middleware/errors.py", line 162, in __call__
    await self.app(scope, receive, _send)
  File "/home/user/PycharmProjects/sample_app/venv/lib/python3.9/site-packages/starlette/exceptions.py", line 93, in __call__
    raise exc
  File "/home/user/PycharmProjects/sample_app/venv/lib/python3.9/site-packages/starlette/exceptions.py", line 82, in __call__
    await self.app(scope, receive, sender)
  File "/home/user/PycharmProjects/sample_app/venv/lib/python3.9/site-packages/fastapi/middleware/asyncexitstack.py", line 21, in __call__
    raise e
  File "/home/user/PycharmProjects/sample_app/venv/lib/python3.9/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
    await self.app(scope, receive, send)
  File "/home/user/PycharmProjects/sample_app/venv/lib/python3.9/site-packages/starlette/routing.py", line 670, in __call__
    await route.handle(scope, receive, send)
  File "/home/user/PycharmProjects/sample_app/venv/lib/python3.9/site-packages/starlette/routing.py", line 266, in handle
    await self.app(scope, receive, send)
  File "/home/user/PycharmProjects/sample_app/venv/lib/python3.9/site-packages/starlette/routing.py", line 68, in app
    await response(scope, receive, send)
  File "/home/user/PycharmProjects/sample_app/venv/lib/python3.9/site-packages/starlette/responses.py", line 162, in __call__
    await send({"type": "http.response.body", "body": self.body})
  File "/home/user/PycharmProjects/sample_app/venv/lib/python3.9/site-packages/starlette/exceptions.py", line 79, in sender
    await send(message)
  File "/home/user/PycharmProjects/sample_app/venv/lib/python3.9/site-packages/starlette/middleware/errors.py", line 159, in _send
    await send(message)
  File "/home/user/PycharmProjects/sample_app/venv/lib/python3.9/site-packages/uvicorn/protocols/http/httptools_impl.py", line 501, in send
    raise RuntimeError("Response content longer than Content-Length")
RuntimeError: Response content longer than Content-Length```

### Operating System

Linux

### Operating System Details

_No response_

### FastAPI Version

0.78.0

### Python Version

3.10

### Additional Context

_No response_