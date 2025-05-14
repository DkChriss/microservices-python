from pydantic import BaseModel


class RoleStore(BaseModel):
    name: str
    description: str

class RoleUpdate(BaseModel):
    id: int | None
    name: str | None
    description: str | None

class RoleResponse(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True

class RoleUsers(BaseModel):
    role_id: int
    users_ids: list[int]

class RolePermissions(BaseModel):
    role_id: int
    permissions_ids: list[int]