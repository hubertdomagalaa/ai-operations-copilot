EDIT: I think I found the issue. Because I installed it through PyCharm, I just installed fastapi and uvicorn as it says here at the bottom: https://fastapi.tiangolo.com/tutorial/intro/ . But this does not seem to install some required packages for the docs. After installing manually with fastapi[all] it now works. It would be good making this clear either on that intro page or here at the first steps or I'm sure others will fall over this.

I've just started the tutorial and am on the first step: https://fastapi.tiangolo.com/tutorial/first-steps/ . Completely clean install of latest FastAPI and uvicorn.

Going to http://127.0.0.1:8000/ works fine.

Going to http://127.0.0.1:8000/docs returns an internal error. It seems get_flat_models_from_fields() expects a known models argument which it didn't get.

Reproduction

From the tutorial at https://fastapi.tiangolo.com/tutorial/first-steps/
Code in main.py:
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
Start uvicorn server: uvicorn main:app --reload
Go to: http://127.0.0.1:8000/docs
Get internal error with stack trace:
INFO: ('127.0.0.1', 55246) - "GET /openapi.json HTTP/1.1" 500
ERROR: Exception in ASGI application
Traceback (most recent call last):
  File "c:\users\user\.virtualenvs\server-xl-s7lqx\lib\site-packages\uvicorn\protocols\http\h11_impl.py", line 369, in run_asgi
    result = await app(self.scope, self.receive, self.send)
  File "c:\users\user\.virtualenvs\server-xl-s7lqx\lib\site-packages\starlette\applications.py", line 133, in __call__
    await self.error_middleware(scope, receive, send)
  File "c:\users\user\.virtualenvs\server-xl-s7lqx\lib\site-packages\starlette\middleware\errors.py", line 122, in __call__
    raise exc from None
  File "c:\users\user\.virtualenvs\server-xl-s7lqx\lib\site-packages\starlette\middleware\errors.py", line 100, in __call__
    await self.app(scope, receive, _send)
  File "c:\users\user\.virtualenvs\server-xl-s7lqx\lib\site-packages\starlette\exceptions.py", line 73, in __call__
    raise exc from None
  File "c:\users\user\.virtualenvs\server-xl-s7lqx\lib\site-packages\starlette\exceptions.py", line 62, in __call__
    await self.app(scope, receive, sender)
  File "c:\users\user\.virtualenvs\server-xl-s7lqx\lib\site-packages\starlette\routing.py", line 585, in __call__
    await route(scope, receive, send)
  File "c:\users\user\.virtualenvs\server-xl-s7lqx\lib\site-packages\starlette\routing.py", line 207, in __call__
    await self.app(scope, receive, send)
  File "c:\users\user\.virtualenvs\server-xl-s7lqx\lib\site-packages\starlette\routing.py", line 40, in app
    response = await func(request)
  File "c:\users\user\.virtualenvs\server-xl-s7lqx\lib\site-packages\fastapi\applications.py", line 87, in openapi
    return JSONResponse(self.openapi())
  File "c:\users\user\.virtualenvs\server-xl-s7lqx\lib\site-packages\fastapi\applications.py", line 79, in openapi
    openapi_prefix=self.openapi_prefix,
  File "c:\users\user\.virtualenvs\server-xl-s7lqx\lib\site-packages\fastapi\openapi\utils.py", line 241, in get_openapi
    flat_models = get_flat_models_from_routes(routes)
  File "c:\users\user\.virtualenvs\server-xl-s7lqx\lib\site-packages\fastapi\utils.py", line 31, in get_flat_models_from_routes
    body_fields_from_routes + responses_from_routes
TypeError: get_flat_models_from_fields() missing 1 required positional argument: 'known_models'
Expected behavior
The API documentation should be showing but it seems FastAPI expects to have at least one model defined.

Environment:

OS: Windows
FastAPI Version: 0.29.0
Python version: 3.7.0