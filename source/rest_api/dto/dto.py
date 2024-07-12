from pydantic import BaseModel


class GenAPIResponse(BaseModel):
    generated_text: str


class QuestionInput(BaseModel):
    url :str
    question :str
