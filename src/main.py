from fastapi import FastAPI, Request, Response, APIRouter, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse 
from src.api.routes.todo_routes import router as todos_router
from src.api.routes.user_routes import router as users_router
from sqlalchemy import text

from contextlib import asynccontextmanager
from src.db.database import Base, engine
from src.core.config import DEFAULT_SCHEMA_NAME, FRONTEND_URL

from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager #This will convert the code before yield startup and after yield cleanup
async def lifespan(app: FastAPI):

    print("Starting up the application...")

    # it starts the db machine
    with engine.begin() as conn:

        conn.execute(
            text(f'CREATE SCHEMA IF NOT EXISTS "{DEFAULT_SCHEMA_NAME}"')
        )

        Base.metadata.create_all(bind=conn)

    yield

    engine.dispose()
    print("Shutting down the application...")

# FastAPI App
app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        FRONTEND_URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"message": "Rate limit exceeded"}
    )


app.include_router(todos_router,prefix="/api/v1")
app.include_router(users_router,prefix="/api/v1")























# # POST - Create Todo
# @app.post("/create-todo", response_model=TodoCreateOut)
# def create_todo(todo_data: TodoCreate) -> TodoCreateOut:

#     todo = Todo(
#         title=todo_data.title,
#         description=todo_data.description,
#         completed=todo_data.completed
#     )

#     db.append(todo)

#     return TodoCreateOut(
#         todo=todo,
#         message="Todo created successfully"
#     )


# # GET - Get All Todos
# @app.get("/get-todos", response_model=TodoGetOut)
# def get_todos() -> TodoGetOut:

#     return TodoGetOut(
#         todos=db,
#         message="Fetched All Todos"
#     )


# # GET - Get Todo By ID
# @app.get("/get-todos/{todo_id}",response_model=Union[TodoCreateOut, BaseOut])
# def get_todo_by_id(todo_id: str) -> Union[TodoCreateOut, BaseOut]:

#     # Convert string to UUID
#     try:
#         todo_id = UUID(todo_id)

#     except Exception as ex:
#         return BaseOut(
#             message="Wrong id for Todo",
#             error=str(ex)
#         )

#     for todo in db:

#         if todo.id == todo_id:

#             return TodoCreateOut(
#                 todo=todo,
#                 message="Todo fetched successfully"
#             )

#     raise HTTPException(
#         status_code=404,
#         detail="Todo not found"
#     )


# # PUT - Complete Todo Update
# @app.put("/update-todo/{todo_id}",response_model=Union[TodoCreateOut, BaseOut])
# def update_todo(todo_id: str,todo_data: TodoUpdate) -> Union[TodoCreateOut, BaseOut]:

#     try:
#         todo_id = UUID(todo_id)

#     except Exception as ex:
#         return BaseOut(
#             message="Wrong id for Todo",
#             error=str(ex)
#         )

#     for index, existing_todo in enumerate(db):

#         if existing_todo.id == todo_id:

#             updated_todo = Todo(
#                 id=existing_todo.id,
#                 title=todo_data.title,
#                 description=todo_data.description,
#                 completed=todo_data.completed
#             )

#             db[index] = updated_todo

#             return TodoCreateOut(
#                 todo=updated_todo,
#                 message="Todo updated successfully"
#             )

#     return BaseOut(
#         message="Todo not found"
#     )


# # PATCH - Partial Update Todo
# @app.patch("/update-todo/{todo_id}",response_model=Union[TodoCreateOut, BaseOut])
# def partial_update_todo(todo_id : str, todo_data: TodoPatch) -> Union[TodoCreateOut, BaseOut]:

#     try:
#         todo_id = UUID(todo_id)

#     except Exception as ex:
#         return BaseOut(
#             message="Wrong id for Todo",
#             error=str(ex)
#         )
        
#     for index, existing_todo in enumerate(db):

#         if existing_todo.id == todo_id:

#             if todo_data.title is not None:
#                 existing_todo.title = todo_data.title

#             if todo_data.description is not None:
#                 existing_todo.description = todo_data.description

#             if todo_data.completed is not None:
#                 existing_todo.completed = todo_data.completed

#             db[index] = existing_todo

#             return TodoCreateOut(
#                 todo=existing_todo,
#                 message="Todo updated successfully"
#             )
#     return BaseOut(
#             message="Todo not found"
#         )


# # DELETE - Delete Todo
# @app.delete("/delete-todo/{todo_id}",response_model=Union[TodoCreateOut, BaseOut])
# def delete_todo(todo_id: str) -> Union[TodoCreateOut, BaseOut]:

#     # Convert string to UUID
#     try:
#         todo_id = UUID(todo_id)

#     except Exception as ex:
#         return BaseOut(
#             message="Wrong id for Todo",
#             error=str(ex)
#         )

#     # Find Todo
#     for index, existing_todo in enumerate(db):

#         if existing_todo.id == todo_id:

#             deleted_todo = db.pop(index)

#             return TodoCreateOut(
#                 todo=deleted_todo,
#                 message="Todo Deleted"
#             )

#     return BaseOut(
#         message="Todo not found"
#     )