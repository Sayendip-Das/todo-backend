from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from uuid import UUID
from typing import Union
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.schemas.todo_schema import TodoCreate, Todo, TodoUpdate, TodoPatch, BaseOut, TodoCreateOut, TodoGetOut
from src.db.database import get_db
from src.db.models.user_model import UserModel
from sqlalchemy.orm import Session
from src.services.jwt_service import JWTService
from src.services.todo_service import TodoService
from src.services.user_service import UserService

router = APIRouter(prefix="/todo",tags=["Todo"])

# Trace the number of API calls made by the user using IP address 
limiter = Limiter(key_func=get_remote_address)

bearer_schema = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_schema),
    db: Session = Depends(get_db)
) -> UserModel:

    access_token = credentials.credentials

    payload = JWTService().decode(token=access_token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token"
        )

    if payload.get("token_type") != "access":
        raise HTTPException(
            status_code=401,
            detail="Invalid token type"
        )

    email = payload.get("email")

    if email is None:
        raise HTTPException(
            status_code=401,
            detail="Email not found in token"
        )

    user_model = UserService.get_user_by_email(email=email, db=db)

    if user_model is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    if not user_model.active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    return user_model

# Temporary DB
# db: list[Todo] = []

# Use of Depends functionality for comman task we are doing inside these api everytime we do request
def check_correct_id(todo_id: str) -> UUID:

    try:
        todo_id = UUID(todo_id)

    except Exception as ex:
        raise HTTPException(

            detail=BaseOut(
                message="Wrong ID for Todo",
                error=str(ex)
            ).model_dump(),
            status_code=400
        )
    return todo_id



# POST - Create Todo
@router.post("/create-todo", response_model=TodoCreateOut)
# @limiter.limit("2/minute")
def create_todo(request: Request, todo_data: TodoCreate, db : Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)) -> TodoCreateOut:

    todo_model = TodoService.create_todo(
        todo_data=todo_data,
        user_id=current_user.id,
        db=db
    )

    todo = Todo.model_validate(todo_model)

    return TodoCreateOut(
        todo=todo,
        message="Todo created successfully"
    )



# GET - Get All Todos
@router.get("/get-todos", response_model=TodoGetOut)
# @limiter.limit("5/minute")
def get_todos(request: Request, db : Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)) -> TodoGetOut:

    todo_models = TodoService.get_all_todos(
        user_id=current_user.id,
        db=db
    )

    todo_list = []

    for todo_model in todo_models:
        todo = Todo.model_validate(todo_model)
        todo_list.append(todo)

    return TodoGetOut(
        todos=todo_list,
        message="Fetched all Todos successfully"
    )


# GET - Get Todo By ID
@router.get("/get-todos/{todo_id}",response_model=Union[TodoCreateOut, BaseOut])
def get_todo_by_id(todo_id: UUID = Depends(check_correct_id), db : Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)) -> Union[TodoCreateOut, BaseOut]:

    todo_model = TodoService.get_todo_by_id(
        todo_id=todo_id,
        user_id=current_user.id,
        db=db,
    )

    if todo_model is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found",
        )

    todo = Todo.model_validate(todo_model)

    return TodoCreateOut(
        todo=todo,
        message="Todo fetched successfully",
    )


# PUT - Complete Todo Update
@router.put("/update-todo/{todo_id}",response_model=Union[TodoCreateOut, BaseOut])
def update_todo(todo_data: TodoUpdate, todo_id: UUID = Depends(check_correct_id), db : Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)) -> Union[TodoCreateOut, BaseOut]:

    todo_model = TodoService.get_todo_by_id(
            todo_id=todo_id,
            user_id=current_user.id,
            db=db,
        )

    if todo_model is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found",
        )

    updated_todo_model = TodoService.update_todo(
        todo_model=todo_model,
        todo_data=todo_data,
        db=db,
    )

    todo = Todo.model_validate(updated_todo_model)

    return TodoCreateOut(
        todo=todo,
        message="Todo updated successfully",
    )


# PATCH - Partial Update Todo
@router.patch("/update-todo/{todo_id}",response_model=Union[TodoCreateOut, BaseOut])
def partial_update_todo(todo_data: TodoPatch, todo_id: UUID = Depends(check_correct_id), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)) -> Union[TodoCreateOut, BaseOut]:

    todo_model = TodoService.get_todo_by_id(
        todo_id=todo_id,
        user_id=current_user.id,
        db=db,
    )

    if todo_model is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found",
        )

    partial_updated_todo_model = TodoService.patch_todo(
        todo_model=todo_model,
        todo_data=todo_data,
        db=db,
    )

    todo = Todo.model_validate(partial_updated_todo_model)
        
    return TodoCreateOut(
        todo=todo,
        message="Todo updated successfully",
    )


# DELETE - Delete Todo
@router.delete("/delete-todo/{todo_id}",response_model=Union[TodoCreateOut, BaseOut])
def delete_todo(todo_id: UUID = Depends(check_correct_id), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)) -> Union[TodoCreateOut, BaseOut]:

    todo_model = TodoService.get_todo_by_id(
        todo_id=todo_id,
        user_id=current_user.id,
        db=db,
    )

    if todo_model is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found",
        )

    Todo.model_validate(todo_model)

    TodoService.delete_todo(
        todo_model=todo_model,
        db=db,
    )

    return BaseOut(
        message="Todo deleted successfully",
    )
