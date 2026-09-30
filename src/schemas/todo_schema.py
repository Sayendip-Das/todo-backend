from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4
from typing import Optional

# Pydantic Models
class TodoCreate(BaseModel):
    title: str
    description: str
    completed: bool = False


# This is used for creating a Todo 
class Todo(TodoCreate):
   id: UUID = Field(default_factory=uuid4)

   model_config = ConfigDict(
        from_attributes=True
    )


# This is used for updating a Todo 
class TodoUpdate(BaseModel):
    title: str
    description: str
    completed: bool

# This is used for partial updating a Todo
class TodoPatch(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class BaseOut(BaseModel):
    message: str
    error: Optional[str] = None


class TodoCreateOut(BaseOut):
    todo: Todo


class TodoGetOut(BaseOut):
    todos: list[Todo]
