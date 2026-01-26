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
from fastapi import FastAPI()

app = FastAPI()

async def run(cmd):
    proc = await asyncio.create_subprocess_exec(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        return stdout.decode()
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')


#Fails when run from `uvicorn.run` and navigating to this endpoint
@app.get("/sub/test")
async def try_subprocess():
    sub_process_result = await run('ping')
    print(sub_process_result)
    return {"response": sub_process_result}


# when executed from here, runs correctly.
if __name__ == '__main__':
    output = asyncio.run(run('ping'))
    print(output)
Description
Open the browser and call endpoint /sub/test
Should return stdout of command ping and print it on console like this:
['ping' exited with 1]

Usage: ping [-t] [-a] [-n count] [-l size] [-f] [-i TTL] [-v TOS]
            [-r count] [-s count] [[-j host-list] | [-k host-list]]
            [-w timeout] [-R] [-S srcaddr] [-c compartment] [-p]
            [-4] [-6] target_name

Options:
    -t             Ping the specified host until stopped.
                   To see statistics and continue - type Control-Break;
                   To stop - type Control-C.
    -a             Resolve addresses to hostnames.
    -n count       Number of echo requests to send.
    -l size        Send buffer size.
    -f             Set Don't Fragment flag in packet (IPv4-only).
    -i TTL         Time To Live.
    -v TOS         Type Of Service (IPv4-only. This setting has been deprecated
                   and has no effect on the type of service field in the IP
                   Header).
    -r count       Record route for count hops (IPv4-only).
    -s count       Timestamp for count hops (IPv4-only).
    -j host-list   Loose source route along host-list (IPv4-only).
    -k host-list   Strict source route along host-list (IPv4-only).
    -w timeout     Timeout in milliseconds to wait for each reply.
    -R             Use routing header to test reverse route also (IPv6-only).
                   Per RFC 5095 the use of this routing header has been
                   deprecated. Some systems may drop echo requests if
                   this header is used.
    -S srcaddr     Source address to use.
    -c compartment Routing compartment identifier.
    -p             Ping a Hyper-V Network Virtualization provider address.
    -4             Force using IPv4.
    -6             Force using IPv6.

When executed with

if __name__ == '__main__':
    uvicorn.run("api.api:app", host="0.0.0.0", port=8000, reload=True)
But instead, returns Internal Server Error. With the following traceback:

INFO:     127.0.0.1:49903 - "GET /sub/test HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "E:\pycharm\my_project\venv\lib\site-packages\uvicorn\protocols\http\httptools_impl.py", line 375, in run_asgi
    result = await app(self.scope, self.receive, self.send)
  File "E:\pycharm\my_project\venv\lib\site-packages\uvicorn\middleware\proxy_headers.py", line 75, in __call__
    return await self.app(scope, receive, send)
  File "E:\pycharm\my_project\venv\lib\site-packages\fastapi\applications.py", line 208, in __call__
    await super().__call__(scope, receive, send)
  File "E:\pycharm\my_project\venv\lib\site-packages\starlette\applications.py", line 112, in __call__
    await self.middleware_stack(scope, receive, send)
  File "E:\pycharm\my_project\venv\lib\site-packages\starlette\middleware\errors.py", line 181, in __call__
    raise exc
  File "E:\pycharm\my_project\venv\lib\site-packages\starlette\middleware\errors.py", line 159, in __call__
    await self.app(scope, receive, _send)
  File "E:\pycharm\my_project\venv\lib\site-packages\starlette\middleware\cors.py", line 84, in __call__
    await self.app(scope, receive, send)
  File "E:\pycharm\my_project\venv\lib\site-packages\starlette\exceptions.py", line 82, in __call__
    raise exc
  File "E:\pycharm\my_project\venv\lib\site-packages\starlette\exceptions.py", line 71, in __call__
    await self.app(scope, receive, sender)
  File "E:\pycharm\my_project\venv\lib\site-packages\starlette\routing.py", line 656, in __call__
    await route.handle(scope, receive, send)
  File "E:\pycharm\my_project\venv\lib\site-packages\starlette\routing.py", line 259, in handle
    await self.app(scope, receive, send)
  File "E:\pycharm\my_project\venv\lib\site-packages\starlette\routing.py", line 61, in app
    response = await func(request)
  File "E:\pycharm\my_project\venv\lib\site-packages\fastapi\routing.py", line 226, in app
    raw_response = await run_endpoint_function(
  File "E:\pycharm\my_project\venv\lib\site-packages\fastapi\routing.py", line 159, in run_endpoint_function
    return await dependant.call(**values)
  File "E:\pycharm\my_project\src\backend\app\api\api.py", line 230, in try_subprocess
    sub_process_result = await run('ping')
  File "E:\pycharm\my_project\src\backend\app\api\api.py", line 214, in run
    proc = await asyncio.create_subprocess_exec(
  File "C:\Users\user\AppData\Local\Programs\Python\Python310\lib\asyncio\subprocess.py", line 218, in create_subprocess_exec
    transport, protocol = await loop.subprocess_exec(
  File "C:\Users\user\AppData\Local\Programs\Python\Python310\lib\asyncio\base_events.py", line 1652, in subprocess_exec
    transport = await self._make_subprocess_transport(
  File "C:\Users\user\AppData\Local\Programs\Python\Python310\lib\asyncio\base_events.py", line 493, in _make_subprocess_transport
    raise NotImplementedError
NotImplementedError

When just executing the subprocess like this:

if __name__ == '__main__':
    output = asyncio.run(run('ping'))
    print(output)
The correct output is printed.

Operating System
Windows

Operating System Details
No response

FastAPI Version
0.70.1

Python Version
Python 3.10.1

Additional Context
As far as I understand the default event loop doesn't support doing this. So the answer should be to use the default Asyncio event loop, which works. But I have no idea how to tell FastApi to use a different event loop.

I've tried setting the event loop like this:

if __name__ == '__main__':
    # noinspection PyTypeChecker
    loop = asyncio.ProactorEventLoop()
    config = Config(app="api.api:app", host="localhost", port=8000, reload=True, loop=loop)
    server = Server(config=config)
    server.run()
Like @dmontagu eluded to here: #825 (comment)
Sadly the loop key argument expects a string, one of the following: ["none","auto","asyncio","uvloop"]