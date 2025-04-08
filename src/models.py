from pydantic import BaseModel, ConfigDict
from typing import Generic, List, TypeVar, Optional
from fi.testcases import TestCase

T = TypeVar("T")

class Request(BaseModel, Generic[T]):
    data: T
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        super().__init__(**data)
        if isinstance(data.get('data'), dict):
            if 'eval_templates' in data['data'] and 'inputs' in data['data']:
                self.data = EvalRequest(**data['data'])
            elif 'eval_templates' in data['data']:
                self.data = EvalConfigRequest(**data['data'])

class EvalConfig(BaseModel):
    criteria: Optional[str] = ""
    config: Optional[dict] = {}
    model: Optional[str] = ""

class EvalTemplateInput(BaseModel):
    eval_id: str = ""
    config: Optional[EvalConfig] = {}

class EvalRequest(BaseModel):
    eval_templates: List[EvalTemplateInput]
    inputs: List[TestCase]

class EvalConfigRequest(BaseModel):
    eval_templates: List[EvalTemplateInput] 