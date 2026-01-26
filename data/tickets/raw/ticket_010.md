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
import time
from typing import Callable, Awaitable

import uvicorn
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from starlette.requests import Request
from starlette.responses import Response



SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base(bind=engine)

app = FastAPI()

class ExceptionHandlerMiddleware:
    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            print(exc)


app.middleware('http')(ExceptionHandlerMiddleware())


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


@app.get('/')
def test():
    time.sleep(2)
    return {'message': 'hello'}


if __name__ == '__main__':
    uvicorn.run(
        'example:app',
        reload=True,
    )
Description
We are using the db session middleware exactly as described here in combination with a custom http exception middleware. When a client is disconnecting from us early we get spammed with a bunch of No response returned errors from starlette.

How to reproduce:

Open browser and call the endpoint /
Close the window before the request completes.
You will see that AnyIO raises a EndOfStream error which ends up being propogated as a Runtime Error with the message as No response returned

Operating System
Linux, macOS

Operating System Details
No response

FastAPI Version
0.73.0

Python Version
Python 3.9.6

Additional Context
SQLAlchemy==1.4.31