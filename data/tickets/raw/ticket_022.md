Description
(by @tiangolo)

The problem is that a "valid JSON Schema" includes a bool (i.e. true and false).

So, additionalProperties doesn't have to be a JSON object, it can be false, to mean no additional properties are allowed.

When I upgraded the JSON Schema models to include the new types and fields for the new JSON Schema 2020-12 I removed bool as a valid JSON Schema.

This is solved in: #9781

Discussed in #9779
Originally posted by jawnsy July 1, 2023

First Check

I added a very descriptive title here.

I used the GitHub search to find a similar question and didn't find it.

I searched the FastAPI documentation, with the integrated search.

I already searched in Google "How to X in FastAPI" and didn't find any information.

I already read and followed all the tutorial in the docs and didn't find an answer.

I already checked if it is not related to FastAPI but to Pydantic.

I already checked if it is not related to FastAPI but to Swagger UI.

I already checked if it is not related to FastAPI but to ReDoc.
Commit to Help

I commit to help with one of those options 👆
Example Code
from fastapi import FastAPI
from pydantic import BaseModel
import json
import sys

class FooBaseModel(BaseModel):
    class Config:
        extra = "forbid"

class Foo(FooBaseModel):
    pass

app = FastAPI()

@app.post("/")
async def post(
    foo: Foo = None,
):
    pass

if __name__ == "__main__":
    oapi = app.openapi()
    json.dump(oapi, sys.stdout, indent=2)
Description
Upgrading from FastAPI 0.98.0 to 0.99.0 causes OpenAPI failures. The error message looks similar to some previous issues (#3782, #383) but I'm unclear whether the issue is the same or different. In both cases, I'm running Pydantic 1.10.10.

On FastAPI 0.98.0, I get the following output when running the above script:

$ pip install fastapi==0.98.0
Requirement already satisfied: fastapi==0.98.0 in /opt/homebrew/Caskroom/miniconda/base/envs/prefect2-dev/lib/python3.10/site-packages (0.98.0)
Requirement already satisfied: pydantic!=1.8,!=1.8.1,<2.0.0,>=1.7.4 in /opt/homebrew/Caskroom/miniconda/base/envs/prefect2-dev/lib/python3.10/site-packages (from fastapi==0.98.0) (1.10.10)
Requirement already satisfied: starlette<0.28.0,>=0.27.0 in /opt/homebrew/Caskroom/miniconda/base/envs/prefect2-dev/lib/python3.10/site-packages (from fastapi==0.98.0) (0.27.0)
Requirement already satisfied: typing-extensions>=4.2.0 in /opt/homebrew/Caskroom/miniconda/base/envs/prefect2-dev/lib/python3.10/site-packages (from pydantic!=1.8,!=1.8.1,<2.0.0,>=1.7.4->fastapi==0.98.0) (4.7.0)
Requirement already satisfied: anyio<5,>=3.4.0 in /opt/homebrew/Caskroom/miniconda/base/envs/prefect2-dev/lib/python3.10/site-packages (from starlette<0.28.0,>=0.27.0->fastapi==0.98.0) (3.7.0)
Requirement already satisfied: idna>=2.8 in /opt/homebrew/Caskroom/miniconda/base/envs/prefect2-dev/lib/python3.10/site-packages (from anyio<5,>=3.4.0->starlette<0.28.0,>=0.27.0->fastapi==0.98.0) (3.4)
Requirement already satisfied: sniffio>=1.1 in /opt/homebrew/Caskroom/miniconda/base/envs/prefect2-dev/lib/python3.10/site-packages (from anyio<5,>=3.4.0->starlette<0.28.0,>=0.27.0->fastapi==0.98.0) (1.3.0)
Requirement already satisfied: exceptiongroup in /opt/homebrew/Caskroom/miniconda/base/envs/prefect2-dev/lib/python3.10/site-packages (from anyio<5,>=3.4.0->starlette<0.28.0,>=0.27.0->fastapi==0.98.0) (1.1.1)

$ python repro.py
{
  "openapi": "3.0.2",
  "info": {
    "title": "FastAPI",
    "version": "0.1.0"
  },
  "paths": {
    "/": {
      "post": {
        "summary": "Post",
        "operationId": "post__post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/Foo"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "Foo": {
        "title": "Foo",
        "type": "object",
        "properties": {},
        "additionalProperties": false
      },
      "HTTPValidationError": {
        "title": "HTTPValidationError",
        "type": "object",
        "properties": {
          "detail": {
            "title": "Detail",
            "type": "array",
            "items": {
              "$ref": "#/components/schemas/ValidationError"
            }
          }
        }
      },
      "ValidationError": {
        "title": "ValidationError",
        "required": [
          "loc",
          "msg",
          "type"
        ],
        "type": "object",
        "properties": {
          "loc": {
            "title": "Location",
            "type": "array",
            "items": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "integer"
                }
              ]
            }
          },
          "msg": {
            "title": "Message",
            "type": "string"
          },
          "type": {
            "title": "Error Type",
            "type": "string"
          }
        }
      }
    }
  }
}
After upgrading to FastAPI 0.99.0, using the same version of Pydantic, I get schema validation failures instead:

$ pip install fastapi==0.99.0
Requirement already satisfied: fastapi==0.99.0 in /opt/homebrew/Caskroom/miniconda/base/envs/prefect2-dev/lib/python3.10/site-packages (0.99.0)
Requirement already satisfied: pydantic!=1.8,!=1.8.1,<2.0.0,>=1.7.4 in /opt/homebrew/Caskroom/miniconda/base/envs/prefect2-dev/lib/python3.10/site-packages (from fastapi==0.99.0) (1.10.10)
Requirement already satisfied: starlette<0.28.0,>=0.27.0 in /opt/homebrew/Caskroom/miniconda/base/envs/prefect2-dev/lib/python3.10/site-packages (from fastapi==0.99.0) (0.27.0)
Requirement already satisfied: typing-extensions>=4.5.0 in /opt/homebrew/Caskroom/miniconda/base/envs/prefect2-dev/lib/python3.10/site-packages (from fastapi==0.99.0) (4.7.0)
Requirement already satisfied: anyio<5,>=3.4.0 in /opt/homebrew/Caskroom/miniconda/base/envs/prefect2-dev/lib/python3.10/site-packages (from starlette<0.28.0,>=0.27.0->fastapi==0.99.0) (3.7.0)
Requirement already satisfied: idna>=2.8 in /opt/homebrew/Caskroom/miniconda/base/envs/prefect2-dev/lib/python3.10/site-packages (from anyio<5,>=3.4.0->starlette<0.28.0,>=0.27.0->fastapi==0.99.0) (3.4)
Requirement already satisfied: sniffio>=1.1 in /opt/homebrew/Caskroom/miniconda/base/envs/prefect2-dev/lib/python3.10/site-packages (from anyio<5,>=3.4.0->starlette<0.28.0,>=0.27.0->fastapi==0.99.0) (1.3.0)
Requirement already satisfied: exceptiongroup in /opt/homebrew/Caskroom/miniconda/base/envs/prefect2-dev/lib/python3.10/site-packages (from anyio<5,>=3.4.0->starlette<0.28.0,>=0.27.0->fastapi==0.99.0) (1.1.1)

$ python repro.py 
Traceback (most recent call last):
  File "/Users/jawnsy/projects/work/prefect/repro.py", line 22, in <module>
    oapi = app.openapi()
  File "/opt/homebrew/Caskroom/miniconda/base/envs/prefect2-dev/lib/python3.10/site-packages/fastapi/applications.py", line 218, in openapi
    self.openapi_schema = get_openapi(
  File "/opt/homebrew/Caskroom/miniconda/base/envs/prefect2-dev/lib/python3.10/site-packages/fastapi/openapi/utils.py", line 466, in get_openapi
    return jsonable_encoder(OpenAPI(**output), by_alias=True, exclude_none=True)  # type: ignore
  File "pydantic/main.py", line 341, in pydantic.main.BaseModel.__init__
pydantic.error_wrappers.ValidationError: 2 validation errors for OpenAPI
components -> schemas -> Foo -> additionalProperties
  value is not a valid dict (type=type_error.dict)
components -> schemas -> Foo -> $ref
  field required (type=value_error.missing)
The problem seems related to the base class config setting, as removing it results in valid output:

class FooBaseModel(BaseModel):
    class Config:
        extra = "forbid"
So I think my question is: should we be adding additionalProperties and $ref to our base schema?

Operating System
macOS

Operating System Details
No response

FastAPI Version
0.99.0

Python Version
Python 3.10.6

Additional Context
We have some other debug information here. Since our project is open source, the straightforward way to reproduce it is:

$ git clone git@github.com:PrefectHQ/prefect.git
$ pip install -e '.[dev]'
$ prefect dev build-docs
You can see the before/after by upgrading or downgrading FastAPI. It may be related to FastAPI's recent addition of OpenAPI 3.1.0 support, as that was the headline feature of this release: https://github.com/tiangolo/fastapi/releases/tag/0.99.0 from pull request: #9770

This is the generated OpenAPI spec from FastAPI 0.98.0:

{
  "openapi": "3.0.2",
  "info": {
    "title": "FastAPI",
    "version": "0.1.0"
  },
  "paths": {
    "/": {
      "post": {
        "summary": "Post",
        "operationId": "post__post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/Foo"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "Foo": {
        "title": "Foo",
        "type": "object",
        "properties": {}
      },
      "HTTPValidationError": {
        "title": "HTTPValidationError",
        "type": "object",
        "properties": {
          "detail": {
            "title": "Detail",
            "type": "array",
            "items": {
              "$ref": "#/components/schemas/ValidationError"
            }
          }
        }
      },
      "ValidationError": {
        "title": "ValidationError",
        "required": [
          "loc",
          "msg",
          "type"
        ],
        "type": "object",
        "properties": {
          "loc": {
            "title": "Location",
            "type": "array",
            "items": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "integer"
                }
              ]
            }
          },
          "msg": {
            "title": "Message",
            "type": "string"
          },
          "type": {
            "title": "Error Type",
            "type": "string"
          }
        }
      }
    }
  }
}
This is the generated OpenAPI spec from FastAPI 0.99.0:

{
  "openapi": "3.1.0",
  "info": {
    "title": "FastAPI",
    "version": "0.1.0"
  },
  "paths": {
    "/": {
      "post": {
        "summary": "Post",
        "operationId": "post__post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/Foo"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "Foo": {
        "properties": {},
        "type": "object",
        "title": "Foo"
      },
      "HTTPValidationError": {
        "properties": {
          "detail": {
            "items": {
              "$ref": "#/components/schemas/ValidationError"
            },
            "type": "array",
            "title": "Detail"
          }
        },
        "type": "object",
        "title": "HTTPValidationError"
      },
      "ValidationError": {
        "properties": {
          "loc": {
            "items": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "integer"
                }
              ]
            },
            "type": "array",
            "title": "Location"
          },
          "msg": {
            "type": "string",
            "title": "Message"
          },
          "type": {
            "type": "string",
            "title": "Error Type"
          }
        },
        "type": "object",
        "required": [
          "loc",
          "msg",
          "type"
        ],
        "title": "ValidationError"
      }
    }
  }
}
This is the diff:

--- fastapi-0.98.0.json 2023-07-01 12:34:12
+++ fastapi-0.99.0.json 2023-07-01 12:34:20
@@ -1,5 +1,5 @@
 {
-  "openapi": "3.0.2",
+  "openapi": "3.1.0",
   "info": {
     "title": "FastAPI",
     "version": "0.1.0"
\ No newline at end of file
@@ -44,35 +44,26 @@
   "components": {
     "schemas": {
       "Foo": {
-        "title": "Foo",
+        "properties": {},
         "type": "object",
-        "properties": {}
+        "title": "Foo"
       },
       "HTTPValidationError": {
-        "title": "HTTPValidationError",
-        "type": "object",
         "properties": {
           "detail": {
-            "title": "Detail",
-            "type": "array",
             "items": {
               "$ref": "#/components/schemas/ValidationError"
-            }
+            },
+            "type": "array",
+            "title": "Detail"
           }
-        }
+        },
+        "type": "object",
+        "title": "HTTPValidationError"
       },
       "ValidationError": {
-        "title": "ValidationError",
-        "required": [
-          "loc",
-          "msg",
-          "type"
-        ],
-        "type": "object",
         "properties": {
           "loc": {
-            "title": "Location",
-            "type": "array",
             "items": {
               "anyOf": [
                 {
\ No newline at end of file
@@ -82,17 +73,26 @@
                   "type": "integer"
                 }
               ]
-            }
+            },
+            "type": "array",
+            "title": "Location"
           },
           "msg": {
-            "title": "Message",
-            "type": "string"
+            "type": "string",
+            "title": "Message"
           },
           "type": {
-            "title": "Error Type",
-            "type": "string"
+            "type": "string",
+            "title": "Error Type"
           }
-        }
+        },
+        "type": "object",
+        "required": [
+          "loc",
+          "msg",
+          "type"
+        ],
+        "title": "ValidationError"
       }
     }
   }
```</div>