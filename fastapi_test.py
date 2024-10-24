from fastapi import FastAPI, Path


app = FastAPI()
students = [
    {
        "name": "john",
        "age": 17,
        "class": "ibang klase"
    },
    {
        "name": "jeremy",
        "age": 69,
        "class": "ibang klase din"
    },
]

@app.get("/")
def index():
    return {"name": "First Data"}


@app.get("/get-student/{student_id}")
def get_students(student_id: int = Path(description="The student ID")):
    return students[student_id]

@app.get("/search")
def get_student(name: str):
    return [student for student in students if name in student["name"]]
