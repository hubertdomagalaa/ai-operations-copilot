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
NA
Description
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\fastapi_cache\coder.py", line 53, in encode
return json.dumps(value, cls=JsonEncoder)
File "C:\Users\vvaleti\AppData\Local\Programs\Python\Python39\lib\json_init_.py", line 234, in dumps
return cls(
File "C:\Users\vvaleti\AppData\Local\Programs\Python\Python39\lib\json\encoder.py", line 199, in encode
chunks = self.iterencode(o, _one_shot=True)
File "C:\Users\vvaleti\AppData\Local\Programs\Python\Python39\lib\json\encoder.py", line 257, in iterencode
return _iterencode(o, 0)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\fastapi_cache\coder.py", line 26, in default
return jsonable_encoder(obj)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\fastapi\encoders.py", line 145, in jsonable_encoder
return jsonable_encoder(
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\fastapi\encoders.py", line 101, in jsonable_encoder
encoded_value = jsonable_encoder(
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\fastapi\encoders.py", line 130, in jsonable_encoder
return ENCODERS_BY_TYPEtype(obj)
File "pydantic\json.py", line 45, in pydantic.json.lambda
bytes: lambda o: o.decode(),
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
2022-10-19 11:30:20,810 uvicorn.error - ERROR - Exception in ASGI application
Traceback (most recent call last):
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\uvicorn\protocols\http\h11_impl.py", line 366, in run_asgi
result = await app(self.scope, self.receive, self.send)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\uvicorn\middleware\proxy_headers.py", line 75, in call
return await self.app(scope, receive, send)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\fastapi\applications.py", line 269, in call
await super().call(scope, receive, send)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\sentry_sdk\integrations\starlette.py", line 293,
in _sentry_patched_asgi_app
return await middleware(scope, receive, send)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\sentry_sdk\integrations\asgi.py", line 138, in _run_asgi3
return await self._run_app(scope, lambda: self.app(scope, receive, send))
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\sentry_sdk\integrations\asgi.py", line 187, in _run_app
raise exc from None
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\sentry_sdk\integrations\asgi.py", line 182, in _run_app
return await callback()
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\starlette\applications.py", line 124, in call await self.middleware_stack(scope, receive, send)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\sentry_sdk\integrations\starlette.py", line 98, in _create_span_call
await old_call(*args, **kwargs)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\starlette\middleware\errors.py", line 184, in call
raise exc
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\starlette\middleware\errors.py", line 162, in call
await self.app(scope, receive, _send)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\sentry_sdk\integrations\starlette.py", line 98, in _create_span_call
await old_call(*args, **kwargs)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\starlette\middleware\base.py", line 68, in call
response = await self.dispatch_func(request, call_next)
File "C:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.\src\app\trace.py", line 57, in dispatch
response = await call_next(request)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\starlette\middleware\base.py", line 46, in call_next
raise app_exc
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\starlette\middleware\base.py", line 36, in coro
await self.app(scope, request.receive, send_stream.send)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\sentry_sdk\integrations\starlette.py", line 98, in _create_span_call
await old_call(*args, **kwargs)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\starlette\middleware\cors.py", line 84, in call
await self.app(scope, receive, send)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\sentry_sdk\integrations\asgi.py", line 138, in _run_asgi3
return await self._run_app(scope, lambda: self.app(scope, receive, send))
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\sentry_sdk\integrations\asgi.py", line 148, in _run_app
raise exc from None
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\sentry_sdk\integrations\asgi.py", line 145, in _run_app
return await callback()
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\sentry_sdk\integrations\starlette.py", line 191,
in _sentry_exceptionmiddleware_call
await old_call(self, scope, receive, send)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\sentry_sdk\integrations\starlette.py", line 191,
in _sentry_exceptionmiddleware_call
await old_call(self, scope, receive, send)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\sentry_sdk\integrations\starlette.py", line 191,
in _sentry_exceptionmiddleware_call
await old_call(self, scope, receive, send)
[Previous line repeated 3 more times]
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\sentry_sdk\integrations\starlette.py", line 98, in _create_span_call
await old_call(*args, **kwargs)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\starlette\exceptions.py", line 93, in call
raise exc
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\starlette\exceptions.py", line 82, in call
await self.app(scope, receive, sender)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\sentry_sdk\integrations\starlette.py", line 98, in _create_span_call
await old_call(*args, **kwargs)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\fastapi\middleware\asyncexitstack.py", line 21, in call
raise e
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\fastapi\middleware\asyncexitstack.py", line 18, in call
await self.app(scope, receive, send)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\starlette\routing.py", line 670, in call
await route.handle(scope, receive, send)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\starlette\routing.py", line 266, in handle
await self.app(scope, receive, send)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\starlette\routing.py", line 65, in app
response = await func(request)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\sentry_sdk\integrations\fastapi.py", line 106, in sentry_app
return await old_app(*args, **kwargs)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\fastapi\routing.py", line 227, in app
raw_response = await run_endpoint_function(
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\fastapi\routing.py", line 160, in run_endpoint_function
return await dependant.call(**values)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\fastapi_cache\decorator.py", line 58, in inner
await backend.set(cache_key, coder.encode(ret), expire or FastAPICache.get_expire())
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\fastapi_cache\coder.py", line 53, in encode
return json.dumps(value, cls=JsonEncoder)
File "C:\Users\vvaleti\AppData\Local\Programs\Python\Python39\lib\json_init.py", line 234, in dumps
return cls(
File "C:\Users\vvaleti\AppData\Local\Programs\Python\Python39\lib\json\encoder.py", line 199, in encode
chunks = self.iterencode(o, _one_shot=True)
File "C:\Users\vvaleti\AppData\Local\Programs\Python\Python39\lib\json\encoder.py", line 257, in iterencode
return _iterencode(o, 0)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\fastapi_cache\coder.py", line 26, in default
return jsonable_encoder(obj)
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\fastapi\encoders.py", line 145, in jsonable_encoder
return jsonable_encoder(
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\fastapi\encoders.py", line 101, in jsonable_encoder
encoded_value = jsonable_encoder(
File "c:\Users\vvaleti\Documents\GitHub\industry_financial_rbapi.venv\lib\site-packages\fastapi\encoders.py", line 130, in jsonable_encoder
return ENCODERS_BY_TYPEtype(obj)
File "pydantic\json.py", line 45, in pydantic.json.lambda
bytes: lambda o: o.decode(),
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte

Operating System
Windows

Operating System Details
No response

FastAPI Version
0.70.0

Python Version
3.9.8

Additional Context
Please check the logs and let us know if you need any other to debug