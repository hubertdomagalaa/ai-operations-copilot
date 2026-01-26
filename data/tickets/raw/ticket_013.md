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
import multiprocessing
import os
import time

import uvicorn
from fastapi import FastAPI

app = FastAPI()
processes = []


def keep_alive_process():
    while True:
        print(f"process {os.getpid()} is alive")
        time.sleep(1)


@app.post("/start")
async def start_processes():

    for i in range(4):
        process = multiprocessing.Process(target=keep_alive_process,
                                          args=())
        processes.append(process)
        process.start()

    return {'status': 'started'}


@app.post("/stop")
async def stop_processes():

    for process in processes:
        process.kill()
    processes.clear()

    return {'status': 'stopped'}


if __name__ == '__main__':
    uvicorn.run('main:app', timeout_keep_alive=10, log_level='trace')
Description
I don't really understand what's going on with http requests. When I started child processes and uvicorn timeout_keep_alive timed out, I tried hitting "stop" in the browser and got infinite loading and no HTTP connection log. But if I try to click other buttons or refresh the page, it works and I get two responses.

Netstat shows that socket bind on port 60862 is opened, but uvicorn log:

TRACE:    127.0.0.1:60862 - HTTP connection lost.
https://stackoverflow.com/questions/73940652/http-request-infinite-loading-unclosed-socket-due-to-spawn-child-processes-usi

Operating System
Linux

Operating System Details
No response

FastAPI Version
0.85

Python Version
3.10

Additional Context
No response