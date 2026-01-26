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
#db dependency

def get_db():
    with SessionLocal() as db:
        try:
            yield db
        except:
            raise
        finally:
            db.close()


#exceptions.py
# catch all exception in a middleware

app.middleware("http")(exceptions.catch_exceptions_middleware)
Description
i noticed that after i've updated Fastapi to a superior version > 0.82.0, i noticed that mu integrations tests are stuck and keeps running in a slow manner, which is not the usual behavior of any version that is less than <= 0.82.0 , Can anyone confirm the same behavior please ? i can not understand why i have a really long latency is my dependency causing this, becuz since the 0.82.0, i have changed it to this after the fix in PR #5122 .

Allow exit code for dependencies with yield to always execute, by removing capacity limiter for them, to e.g. allow closing DB connections without deadlocks. PR #5122 by @adriangb.

Can anybody help me figure out why updalting to any superior > 0.82.0 i have this much latency ?

Thank you guys.

Operating System
Linux

Operating System Details
No response

FastAPI Version
0.82.0

Python Version
3.10

Additional Context
No response