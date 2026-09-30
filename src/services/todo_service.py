from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.db.models.todo_model import TodoModel
from src.schemas.todo_schema import TodoCreate, TodoUpdate, TodoPatch

class TodoService:

    # Create Todo Service method 
    @staticmethod
    def create_todo(todo_data : TodoCreate, user_id: UUID, db: Session) -> TodoModel:

        # Convert the todo pydantic model(validation only model) to postgreSql model(db model)
        todo_model = TodoModel(
            title=todo_data.title,
            description=todo_data.description,
            completed=todo_data.completed,
            user_id=user_id
        )
        
        # Add to db
        db.add(todo_model)
        
        # Commit the todo data in the db
        db.commit()
        
        #Refresh the db to show the data in the db
        db.refresh(todo_model) 

        return todo_model



    @staticmethod
    def get_all_todos(user_id: UUID, db: Session) -> list[TodoModel]:

        todo_db_result = db.execute(select(TodoModel).where(TodoModel.user_id == user_id))

        return list(todo_db_result.scalars().all())



    @staticmethod
    def get_todo_by_id(todo_id : UUID, user_id: UUID, db : Session) -> Optional[TodoModel]:

        todo_db_result = db.execute(select(TodoModel).where(TodoModel.id == todo_id,TodoModel.user_id == user_id))

        return todo_db_result.scalar_one_or_none()



    @staticmethod
    def update_todo(todo_model: TodoModel, todo_data: TodoUpdate, db: Session) -> TodoModel:

        todo_model.title = todo_data.title

        todo_model.description = todo_data.description
        
        todo_model.completed = todo_data.completed

        db.commit()

        db.refresh(todo_model)

        return todo_model



    @staticmethod
    def patch_todo(todo_model: TodoModel, todo_data: TodoPatch, db: Session) -> TodoModel:

        if todo_data.title is not None:
            todo_model.title = todo_data.title


        if todo_data.description is not None:
            todo_model.description = todo_data.description


        if todo_data.completed is not None:
            todo_model.completed = todo_data.completed

        # Save the changes in db
        db.commit()

        # Reload the updated Todo from PostgreSQL
        db.refresh(todo_model)

        return todo_model



    @staticmethod
    def delete_todo(todo_model: TodoModel, db: Session) -> None:

        db.delete(todo_model)

        db.commit()
