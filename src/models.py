from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class EvalConfig(BaseModel):
    """Configuration for an evaluation.

    Attributes:
        criteria (Optional[str]): Evaluation criteria string. Defaults to empty string.
        config (Optional[dict]): Additional configuration parameters. Defaults to empty dict.
        model (Optional[str]): Model name to use for evaluation. Defaults to empty string.
    """

    criteria: Optional[str] = Field(
        default="",
        description="Evaluation criteria string used to guide the evaluation process",
    )
    check_internet: Optional[bool] = Field(
        default=False,
        description="Flag to indicate if internet access is required for evaluation",
    )
    model: Optional[str] = Field(
        default="", description="Name of the model to use for performing the evaluation"
    )


class Evaluation(BaseModel):
    """Input template for an evaluation.

    Attributes:
        eval_id (str): Integer string of the evaluation id.
        config (Optional[EvalConfig]): Configuration for the evaluation. Defaults to empty dict.
    """

    eval_id: str = Field(
        default="", description="Unique identifier for the evaluation template"
    )
    config: Optional[EvalConfig] = Field(
        default_factory=EvalConfig,
        description="Configuration settings for the evaluation",
    )


# New models for validation


class ProtectRule(BaseModel):
    """Validation model for a single protection rule."""

    metric: Literal[
        "Toxicity", "Tone", "Sexism", "Prompt Injection", "Data Privacy"
    ] = Field(description="Type of protection metric to evaluate")
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
    ] = Field(
        default=None,
        description="List of emotional tones to check for when metric is 'Tone'",
    )
    type: Optional[Literal["any", "all"]] = Field(
        default="any",
        description="Specifies whether any or all of the contains values must be present for Tone metric",
    )

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
        if metric != "Tone" and v != "any":
            if "type" in values.data:
                raise ValueError("'type' should only be provided when metric is 'Tone'")
        return v


class CreateEvalMapping(BaseModel):
    """Represents the mapping structure within the create_eval config."""

    text: Optional[str] = Field(
        default=None, description="Text content to be evaluated"
    )
    input: Optional[str] = Field(
        default=None, description="Input data for the evaluation"
    )
    output: Optional[str] = Field(
        default=None, description="Expected output for the evaluation"
    )


class CreateEvalConfigNested(BaseModel):
    """Represents the nested 'config' structure within the create_eval config."""

    param1: Optional[str] = Field(
        default=None,
        description="First configuration parameter for evaluation creation",
    )
    param2: Optional[int] = Field(
        default=None,
        description="Second configuration parameter for evaluation creation",
    )


class CreateEvalConfig(BaseModel):
    """Validation model for the config argument in create_eval."""

    mapping: CreateEvalMapping = Field(
        default_factory=CreateEvalMapping,
        description="Mapping configuration for evaluation creation",
    )
    config: CreateEvalConfigNested = Field(
        default_factory=CreateEvalConfigNested,
        description="Nested configuration settings for evaluation creation",
    )
    model: Optional[str] = Field(
        default=None, description="Model to be used for the evaluation"
    )
