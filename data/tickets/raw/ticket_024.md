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
Instruction on how to fix the problem is in additional context but I don't know what is causing it so I cannot create a short program that shows the problem and the code I am working on is proprietary so I cannot post it here.
Description
Browse to /docs

Operating System
macOS

Operating System Details
Also appear in a linux docker environment

FastAPI Version
0.76.0

Python Version
3.8.13

Additional Context
From openapi/utils.py line 261

261 status_code_param = response_signature.parameters.get("status_code")
262 if status_code_param is not None:
263 if isinstance(status_code_param.default, int):
264 status_code = str(status_code_param.default)
else:
status_code = None
265 operation.setdefault("responses", {}).setdefault(status_code, {})[
266 "description"
267 ] = route.response_description

The doc load successully if I added the bold text between line 264-265

The following is the error trace:
2022-11-15 17:04:04,518 - uvicorn.access - INFO - 127.0.0.1:61081 - "GET /openapi.json HTTP/1.1" 500
2022-11-15 17:04:04,519 - uvicorn.error - ERROR - Exception in ASGI application
Traceback (most recent call last):
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/uvicorn/protocols/http/h11_impl.py", line 366, in run_asgi
result = await app(self.scope, self.receive, self.send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/uvicorn/middleware/proxy_headers.py", line 75, in call
return await self.app(scope, receive, send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/uvicorn/middleware/message_logger.py", line 82, in call
raise exc from None
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/uvicorn/middleware/message_logger.py", line 78, in call
await self.app(scope, inner_receive, inner_send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/fastapi/applications.py", line 261, in call
await super().call(scope, receive, send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/starlette/applications.py", line 119, in call
await self.middleware_stack(scope, receive, send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/starlette/middleware/errors.py", line 181, in call
raise exc
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/starlette/middleware/errors.py", line 159, in call
await self.app(scope, receive, _send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/starlette/middleware/cors.py", line 84, in call
await self.app(scope, receive, send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/starlette/exceptions.py", line 87, in call
raise exc
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/starlette/exceptions.py", line 76, in call
await self.app(scope, receive, sender)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/fastapi/middleware/asyncexitstack.py", line 21, in call
raise e
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in call
await self.app(scope, receive, send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/starlette/routing.py", line 659, in call
await route.handle(scope, receive, send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/starlette/routing.py", line 259, in handle
await self.app(scope, receive, send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/starlette/routing.py", line 61, in app
response = await func(request)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/fastapi/applications.py", line 216, in openapi
return JSONResponse(self.openapi())
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/fastapi/applications.py", line 191, in openapi
self.openapi_schema = get_openapi(
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/fastapi/openapi/utils.py", line 425, in get_openapi
result = get_openapi_path(
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/fastapi/openapi/utils.py", line 267, in get_openapi_path
operation.setdefault("responses", {}).setdefault(status_code, {})[
UnboundLocalError: local variable 'status_code' referenced before assignment
2022-11-15 17:05:16,098 - uvicorn.access - INFO - 127.0.0.1:61094 - "GET /docs HTTP/1.1" 200
2022-11-15 17:05:16,195 - uvicorn.access - INFO - 127.0.0.1:61094 - "GET /openapi.json HTTP/1.1" 500
2022-11-15 17:05:16,196 - uvicorn.error - ERROR - Exception in ASGI application
Traceback (most recent call last):
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/uvicorn/protocols/http/h11_impl.py", line 366, in run_asgi
result = await app(self.scope, self.receive, self.send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/uvicorn/middleware/proxy_headers.py", line 75, in call
return await self.app(scope, receive, send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/uvicorn/middleware/message_logger.py", line 82, in call
raise exc from None
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/uvicorn/middleware/message_logger.py", line 78, in call
await self.app(scope, inner_receive, inner_send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/fastapi/applications.py", line 261, in call
await super().call(scope, receive, send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/starlette/applications.py", line 119, in call
await self.middleware_stack(scope, receive, send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/starlette/middleware/errors.py", line 181, in call
raise exc
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/starlette/middleware/errors.py", line 159, in call
await self.app(scope, receive, _send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/starlette/middleware/cors.py", line 84, in call
await self.app(scope, receive, send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/starlette/exceptions.py", line 87, in call
raise exc
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/starlette/exceptions.py", line 76, in call
await self.app(scope, receive, sender)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/fastapi/middleware/asyncexitstack.py", line 21, in call
raise e
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in call
await self.app(scope, receive, send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/starlette/routing.py", line 659, in call
await route.handle(scope, receive, send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/starlette/routing.py", line 259, in handle
await self.app(scope, receive, send)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/starlette/routing.py", line 61, in app
response = await func(request)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/fastapi/applications.py", line 216, in openapi
return JSONResponse(self.openapi())
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/fastapi/applications.py", line 191, in openapi
self.openapi_schema = get_openapi(
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/fastapi/openapi/utils.py", line 425, in get_openapi
)
File "/Users/karenlaw/.conda/envs/livecheck/lib/python3.8/site-packages/fastapi/openapi/utils.py", line 267, in get_openapi_path
] = route.response_description
UnboundLocalError: local variable 'status_code' referenced before assignment