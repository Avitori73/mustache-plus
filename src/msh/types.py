from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator


class Convertor(BaseModel):
    name: str
    params: Optional[Dict[str, Any]] = None


class Parameter(BaseModel):
    name: str
    description: str
    ask: bool = False
    target: Optional[str] = None
    required: bool = True
    choices: Optional[List[str]] = None
    innerConvertor: Optional[List[Convertor]] = None
    convertor: Optional[str] = None

    @model_validator(mode="after")
    def validate_target_when_ask_false_and_inner_convertor_exist(self):
        if self.innerConvertor and self.ask is False and not self.target:
            raise ValueError(
                "When 'innerConvertor' exists and 'ask' is False, 'target' must be provided."
            )
        return self


class TemplateMeta(BaseModel):
    parameters: List[Parameter] = Field(default_factory=list)
