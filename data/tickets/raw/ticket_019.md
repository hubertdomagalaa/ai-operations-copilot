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
from typing import Union
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

if __name__ == '__main__':
    uvicorn.run(app, port=8080, host='0.0.0.0')
Description
Deploy above code on GCP Cloud run
Invoke GET API from apache JMeter
1000 request/sec for 180 sec duration
Operating System
Windows

Operating System Details
Intel Core i7, 16GB RAM

FastAPI Version
0.68.0

Python Version
3.8

Additional Context
I tried above simple API in Flask & FastAPI and observed that performance was almost similar. I expect better performance in FastAPI as mentioned in their documentation.

My throughput in apache jMeter for Flask & fastAPI was similar like 200 req/sec if run on 1 instance in cloud run.

Anyone did similar kind of exercise or comparision?