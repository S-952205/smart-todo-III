"""
Test suite for agent MCP tools to verify schema compatibility
"""
import pytest
from datetime import datetime
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from models import Task
from tools.mcp_tools import MCPTaskTools


@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_add_task_with_all_fields(session: Session):
    """Test adding a task with status, priority, and due_date"""
    tools = MCPTaskTools(session, "test-user-123")

    due_date = datetime(2026, 2, 20, 10, 0, 0)
    result = tools.add_task(
        title="Test Task",
        description="Test Description",
        status="in-progress",
        priority="high",
        due_date=due_date
    )

    assert result["title"] == "Test Task"
    assert result["description"] == "Test Description"
    assert result["status"] == "in-progress"
    assert result["priority"] == "high"
    assert result["due_date"] == due_date.isoformat()
    assert result["user_id"] == "test-user-123"
    assert "id" in result
    assert "created_at" in result
    assert "updated_at" in result


def test_add_task_with_defaults(session: Session):
    """Test adding a task with default status and priority"""
    tools = MCPTaskTools(session, "test-user-123")

    result = tools.add_task(
        title="Simple Task",
        description="Simple Description"
    )

    assert result["title"] == "Simple Task"
    assert result["status"] == "todo"
    assert result["priority"] == "medium"
    assert result["due_date"] is None


def test_update_task_status(session: Session):
    """Test updating task status"""
    tools = MCPTaskTools(session, "test-user-123")

    # Create a task
    task_result = tools.add_task(title="Task to Update", status="todo")
    task_id = task_result["id"]

    # Update status
    updated = tools.update_task(task_id, status="in-progress")

    assert updated["id"] == task_id
    assert updated["status"] == "in-progress"
    assert updated["title"] == "Task to Update"


def test_update_task_priority_and_due_date(session: Session):
    """Test updating task priority and due date"""
    tools = MCPTaskTools(session, "test-user-123")

    # Create a task
    task_result = tools.add_task(title="Task to Update")
    task_id = task_result["id"]

    # Update priority and due date
    due_date = datetime(2026, 3, 1, 12, 0, 0)
    updated = tools.update_task(
        task_id,
        priority="high",
        due_date=due_date
    )

    assert updated["id"] == task_id
    assert updated["priority"] == "high"
    assert updated["due_date"] == due_date.isoformat()


def test_update_task_multiple_fields(session: Session):
    """Test updating multiple fields at once"""
    tools = MCPTaskTools(session, "test-user-123")

    # Create a task
    task_result = tools.add_task(title="Original Title")
    task_id = task_result["id"]

    # Update multiple fields
    due_date = datetime(2026, 2, 25, 15, 30, 0)
    updated = tools.update_task(
        task_id,
        title="Updated Title",
        description="Updated Description",
        status="in-progress",
        priority="low",
        due_date=due_date
    )

    assert updated["id"] == task_id
    assert updated["title"] == "Updated Title"
    assert updated["description"] == "Updated Description"
    assert updated["status"] == "in-progress"
    assert updated["priority"] == "low"
    assert updated["due_date"] == due_date.isoformat()


def test_complete_task_sets_status_to_done(session: Session):
    """Test that complete_task sets status to 'done'"""
    tools = MCPTaskTools(session, "test-user-123")

    # Create a task
    task_result = tools.add_task(title="Task to Complete", status="in-progress")
    task_id = task_result["id"]

    # Complete the task
    completed = tools.complete_task(task_id)

    assert completed["id"] == task_id
    assert completed["status"] == "done"
    assert completed["title"] == "Task to Complete"


def test_list_tasks_returns_all_fields(session: Session):
    """Test that list_tasks returns all fields including status, priority, due_date"""
    tools = MCPTaskTools(session, "test-user-123")

    # Create tasks with different fields
    due_date = datetime(2026, 2, 28, 9, 0, 0)
    tools.add_task(
        title="Task 1",
        status="todo",
        priority="high",
        due_date=due_date
    )
    tools.add_task(
        title="Task 2",
        status="in-progress",
        priority="low"
    )

    # List tasks
    tasks = tools.list_tasks()

    assert len(tasks) == 2

    # Verify all fields are present
    for task in tasks:
        assert "id" in task
        assert "title" in task
        assert "description" in task
        assert "status" in task
        assert "priority" in task
        assert "due_date" in task
        assert "user_id" in task
        assert "created_at" in task
        assert "updated_at" in task

        # Verify no 'completed' field exists
        assert "completed" not in task


def test_user_isolation(session: Session):
    """Test that users can only access their own tasks"""
    tools_user1 = MCPTaskTools(session, "user-1")
    tools_user2 = MCPTaskTools(session, "user-2")

    # User 1 creates a task
    task1 = tools_user1.add_task(title="User 1 Task")

    # User 2 creates a task
    task2 = tools_user2.add_task(title="User 2 Task")

    # User 1 should only see their task
    user1_tasks = tools_user1.list_tasks()
    assert len(user1_tasks) == 1
    assert user1_tasks[0]["title"] == "User 1 Task"

    # User 2 should only see their task
    user2_tasks = tools_user2.list_tasks()
    assert len(user2_tasks) == 1
    assert user2_tasks[0]["title"] == "User 2 Task"

    # User 2 should not be able to update User 1's task
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        tools_user2.update_task(task1["id"], title="Hacked")
    assert exc_info.value.status_code == 404
