Issue Content
We have found at least 2 regression in the way forms are handled while trying to migrate to v0.115.11 from version v0.112.4. After investigation we were able to identify 2 commits that introduce 2 separate bugs that break the handling of default values in both x-form-urlencoded and mutlipart froms. Partial fixes have been proposed that also address a CVE, but the PR has been hanging since october 24.

Breaking in the handling of default value in x-url-encoded forms
This bug has been introduced in #12134.

MRE:

app = FastAPI()


@app.post("/")
def root(
    name: Annotated[Optional[str], Form(embed=True)] = None,
):
    print(name)
    return name
with the following request:

❯ http post -v --form localhost:8888 name=""
POST / HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate, br, zstd
Connection: keep-alive
Content-Length: 5
Content-Type: application/x-www-form-urlencoded
Host: localhost:8888
User-Agent: xh/0.24.0

name=

HTTP/1.1 200 OK
Content-Length: 2
Content-Type: application/json
Date: Sun, 23 Mar 2025 21:01:49 GMT
Server: uvicorn

""
The expected result is that None is printed, but instead "" is printed.

this is the offending bit from the linked PR:

diff --git a/fastapi/dependencies/utils.py b/fastapi/dependencies/utils.py
index 6083b731..db7eedba 100644
--- a/fastapi/dependencies/utils.py
+++ b/fastapi/dependencies/utils.py
@@ -789,9 +789,9 @@ async def _extract_form_body(
             value = serialize_sequence_value(field=field, value=results)
         if value is not None:
             values[field.name] = value
-    for key, value in received_body.items():
-        if key not in values:
-            values[key] = value
+    # for key, value in received_body.items():
+    #     if key not in values:
+    #         values[key] = value
     return values
This patch solves the x-form-urlencoded case. So we indeed have two different regressions.
This _get_multi_dict_value gets called for all fields in the schema:

fastapi/fastapi/dependencies/utils.py

Line 765 in 4633b1b

 if ( 

we see here the special case for empty fields:
fastapi/fastapi/dependencies/utils.py

Lines 695 to 700 in 4633b1b

 value is None 
 or ( 
     isinstance(field.field_info, params.Form) 
     and isinstance(value, str)  # For type checks 
     and value == "" 
 ) 

This bit here just blindly re-adds all fields from the body:
fastapi/fastapi/dependencies/utils.py

Lines 794 to 796 in 4633b1b

         values[key] = value 
 return values 
  
This would be partially fixed by https://github.com/fastapi/fastapi/pull/12502/files, but also requires that ignored fields are not re-added to the form.

Breaking in the handling of default value in multipart forms
The breaking of multipart form originates from #12117 where the check for empty field was dropped https://github.com/fastapi/fastapi/pull/12117/files#diff-aef3dac481b68359f4edd6974fa3a047cfde595254a4567a560cebc9ccb0673fR669

MRE:

app = FastAPI()


@app.post("/")
def root(
     file: Annotated[Optional[bytes], File()] = None,
    name: Annotated[Optional[str], Form(embed=True)] = None,
):
    print(name)
    print(file)
    return name
The same request as the previous bug yields name printing an empty string.

Both commits were identified by bisecting using the MREs in this issue

This also solves #13255, but scanning through the issues of the repo it seems that there's a bunch of issue related to handling of default values in forms that I suspect may be linked to this issue.