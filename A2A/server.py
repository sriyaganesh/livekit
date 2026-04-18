from python_a2a import A2AServer, agent, skill, run_server
from python_a2a import TaskStatus, TaskState


@agent(
    name="Hello Agent",
    description="Says hello",
    version="1.0.0",
    url="http://127.0.0.1:5000"  # required for agent card
)
class HelloAgent(A2AServer):

    @skill(
        name="greet",
        description="Greets the user by name",
        tags=["greeting"]
    )
    def greet(self, name: str = "World") -> str:
        return f"Hello, {name}!"

    def handle_task(self, task):
        msg = task.message or {}

        # handle both string + structured input safely
        if isinstance(msg, dict):
            content = msg.get("content", {})
            if isinstance(content, dict):
                text = content.get("text", "")
            else:
                text = str(msg)
        else:
            text = str(msg)

        name = text.strip() or "World"
        greeting = self.greet(name)

        task.artifacts = [{
            "parts": [{"type": "text", "text": greeting}]
        }]
        task.status = TaskStatus(state=TaskState.COMPLETED)
        return task


if __name__ == "__main__":
    run_server(
        HelloAgent(url="http://127.0.0.1:5000"),  # 👈 REQUIRED in your version
        host="127.0.0.1",
        port=5000
    )