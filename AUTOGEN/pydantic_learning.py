from pydantic import BaseModel

class person(BaseModel):
    name: str
    age: int

person1=person(name="Alice", age=30)
person2=person(name="Bob", age=25)

(print(person1.name))
person2=person(name="Charlie", age="23")
(print(person1.name))