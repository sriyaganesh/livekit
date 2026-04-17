print("🚀 Script started")

class Agent:
    def __init__(self, name):
        self.name = name

    def send(self, message, receiver):
        print(f"{self.name} ➡️ {receiver.name}: {message}")
        return receiver.receive(message, self)

    def receive(self, message, sender):
        raise NotImplementedError


class AgentA(Agent):
    def receive(self, message, sender):
        print(f"{self.name} received from {sender.name}: {message}")
        return "Hello from Agent A!"


class AgentB(Agent):
    def receive(self, message, sender):
        print(f"{self.name} received from {sender.name}: {message}")
        return "Hello from Agent B!"


if __name__ == "__main__":
    agent_a = AgentA("Agent A")
    agent_b = AgentB("Agent B")

    response = agent_a.send("Hello B!", agent_b)
    print(f"Response: {response}")