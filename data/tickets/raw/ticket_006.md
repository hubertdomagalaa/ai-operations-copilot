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
class RoleChecker:
    def __init__(self, allowed_roles: List):
        self.allowed_roles = allowed_roles #utils.get_roles(Role)

    def __call__(self, user: User = Depends(oauth2.require_user)):
        print("user=======>", user)
        if user['role'] not in self.allowed_roles:
            logger.debug(f"User with role {user['role']} not in {self.allowed_roles}")
            raise HTTPException(status_code=403, detail="You have not a permission to performe action.")
        


allow_create_resource = RoleChecker(["admin"])
@router.post('/assign_roles', dependencies=[Depends(allow_create_resource)])
def assign_roles(assign_role: schemas.AssignRole ,user_id: str = Depends(oauth2.require_user)):
    
    roles = utils.get_roles(Role)
    
    
    email = assign_role.dict()['email']
    desired_role = assign_role.dict()['role']
    
    count = User.count_documents({"email": str(email)})
    
    role_count = Role.count_documents({"role": str(desired_role)})
    
    if count == 0:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=f"User for email {email} does not exist")
    
    if role_count == 0:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=f"please used only given roles => {','.join(role if role != 'admin' else '' for role in roles)} ")
    
    res = userResponseEntity(User.find_one({"email": str(email)}))
    
    user_id = user_id["id"]
    
    user = userResponseEntity(User.find_one(ObjectId(str(user_id))))
    
    if user['role'] != res['role']:
        dict = assign_role.dict(exclude_none=True)
        User.update_one(
            {'_id': ObjectId(str(res['id']))}, {'$set': dict})

        return {
            "message": f"user email {email} role {res['role']} updated to {desired_role}",
            "loged_in_user": user
        }
    
    return {
        "user": user
    }
Description
I research a lot but not find any good way to manage roles and permission dynamically using FastApi. if you guys have any idea please let me know.Thanks in advance

Operating System
Linux

Operating System Details
No response

FastAPI Version
0.87.0

Python Version
3.10.8

Additional Context
No response