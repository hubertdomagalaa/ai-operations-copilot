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
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(GZipMiddleware)


csv_file(path: str):
    with open(path) as f:
        yield f.readline()

@app.get("/receivings")
def receivings(start: str = start_date, end: str = now) -> StreamingResponse:
    return StreamingResponse(csv_file(path), media_type='text/csv')



app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.website.com"],
    allow_methods=["POST"],
    allow_headers=["*"]
)


if __name__ == '__main__':
    uvicorn.run("middleserver:app", host="0.0.0.0", port=8080, log_level='trace')
Description
Create a regular app with an endpoint that returns a StreamingResponse
Have GZip as a middleware
Result is not compressed even though it should be
Try again with FileResponse
Result is now compressed properly
Operating System
Windows

Operating System Details
No response

FastAPI Version
0.75

Python Version
3.10.3

Additional Context
No response