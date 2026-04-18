from python_a2a import A2AClient
client = A2AClient("http://127.0.0.1:5000")
print("Agent:",client.agent_card.name)
response=client.ask("Sri")
print("Response:",response)
