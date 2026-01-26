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
import asyncio
from fastapi import Request, BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def test_sleep():
    print('test')
    await asyncio.sleep(9999)


@app.post("/test")
async def test(background_tasks: BackgroundTasks):
    background_tasks.add_task(test_sleep)
    return 'test'


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    return response
Description
When use middleware, the second request to 'http://127.0.0.1:8000/test' will be pending. If I remove middleware, everything works fine.
I know it's the middleware problem, but I don't known how to fix it.

Operating System
Linux

Operating System Details
Ubuntu 20.04

FastAPI Version
0.66.1

Python Version
3.9.5

Additional Context
No response