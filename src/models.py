from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Literal, Union


class EvalConfig(BaseModel):
    """Configuration for an evaluation.

    Attributes:
        criteria (Optional[str]): Evaluation criteria string. Defaults to empty string.
        config (Optional[dict]): Additional configuration parameters. Defaults to empty dict.
        model (Optional[str]): Model name to use for evaluation. Defaults to empty string.
    """

    criteria: Optional[str] = ""
    config: Optional[dict] = {}
    model: Optional[str] = ""


class Evaluation(BaseModel):
    """Input template for an evaluation.

    Attributes:
        eval_id (str): ID of the evaluation. Defaults to empty string.
        config (Optional[EvalConfig]): Configuration for the evaluation. Defaults to empty dict.
    """

    eval_id: str = ""
    config: Optional[EvalConfig] = Field(
        default_factory=EvalConfig
    )  # Use Field for default instance


# New models for validation


class ProtectRule(BaseModel):
    """Validation model for a single protection rule."""

    metric: Literal["Toxicity", "Tone", "Sexism", "Prompt Injection", "Data Privacy"]
    contains: Optional[
        List[
            Literal[
                "neutral",
                "joy",
                "love",
                "fear",
                "surprise",
                "sadness",
                "anger",
                "annoyance",
                "confusion",
            ]
        ]
    ] = None
    type: Optional[Literal["any", "all"]] = "any"

    @field_validator("contains", mode="before")
    def check_contains_required_for_tone(cls, v, values):
        metric = values.data.get("metric")
        if metric == "Tone" and (v is None or not v):
            raise ValueError("'contains' is required when metric is 'Tone'")
        if metric != "Tone" and v is not None:
            raise ValueError("'contains' should only be provided when metric is 'Tone'")
        return v

    @field_validator("type", mode="before")
    def check_type_required_for_tone(cls, v, values):
        metric = values.data.get("metric")
        if metric != "Tone" and v != "any":  # Check if type is provided unnecessarily
            # Allow default 'any' even if not Tone, but raise if explicitly set otherwise
            if "type" in values.data:
                raise ValueError("'type' should only be provided when metric is 'Tone'")
        return v


class CreateEvalMapping(BaseModel):
    """Represents the mapping structure within the create_eval config."""

    # Define fields based on expected mapping structure
    # Example: Adjust these fields based on actual requirements
    text: Optional[str] = None
    input: Optional[str] = None
    output: Optional[str] = None
    # Add other expected fields here


class CreateEvalConfigNested(BaseModel):
    """Represents the nested 'config' structure within the create_eval config."""

    # Define fields based on the expected structure of the nested config
    # Example: Adjust based on actual requirements
    param1: Optional[str] = None
    param2: Optional[int] = None


class CreateEvalConfig(BaseModel):
    """Validation model for the config argument in create_eval."""

    mapping: CreateEvalMapping = Field(default_factory=CreateEvalMapping)
    config: CreateEvalConfigNested = Field(default_factory=CreateEvalConfigNested)
    model: Optional[str] = None
