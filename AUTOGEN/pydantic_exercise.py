from pydantic import BaseModel, EmailStr, Field, ValidationError
from typing import List, Optional
from datetime import date


# 1. Basic Employee Info
class Employee(BaseModel):
    emp_id: int
    name: str
    age: int = Field(gt=21)  # age between 18 and 65


# 2. Contact Details
class ContactDetails(BaseModel):
    email: EmailStr
    phone: str = Field(min_length=10, max_length=15)
    address: str


# 3. Job Details
class JobDetails(BaseModel):
    designation: str
    department: str
    joining_date: date


# 4. Salary Details
class SalaryDetails(BaseModel):
    basic_salary: float = Field(gt=0)
    bonus: Optional[float] = 0
    deductions: Optional[float] = 0


# 5. Full Employee Profile (Nested Model)
class EmployeeProfile(BaseModel):
    employee: Employee
    contact: ContactDetails
    job: JobDetails
    salary: SalaryDetails
    skills: List[str]


# -------------------------------
# Example Usage / Testing
# -------------------------------
if __name__ == "__main__":

    try:
        print("Profile 1:")
        emp_profile = EmployeeProfile(
            employee={
                "emp_id": 101,
                "name": "Alice",
                "age": 30
            },
            contact={
                "email": "alice@example.com",
                "phone": "1234567890",
                "address": "Chennai"
            },
            job={
                "designation": "Software Engineer",
                "department": "IT",
                "joining_date": "2022-06-15"
            },
            salary={
                "basic_salary": 50000,
                "bonus": 5000,
                "deductions": 2000
            },
            skills=["Python", "FastAPI", "SQL"]
        )

        print("Valid Employee Profile 1:\n", emp_profile)
        

        print("\nProfile 2:")
        # ❌ Invalid case (age + email wrong)
        bad_profile = EmployeeProfile(
            employee={
                "emp_id": 102,
                "name": "Bob",
                "age": 17   # invalid age
            },
            contact={
                "email": "sriyaganesh",
                "phone": "9944563",
                "address": "Mumbai"
            },
            job={
                "designation": "Analyst",
                "department": "Finance",
                "joining_date": "2023-01-10"
            },
            salary={
                "basic_salary": -1000
            },
            skills=["Excel"]
        )
        print("Valid Employee Profile 2:\n", emp_profile)

    except ValidationError as e:
        print("Validation Error:\n", e)