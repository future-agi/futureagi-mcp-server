import os
from fi.evals import EvalClient
from fi.evals import ProtectClient
from typing import List, Dict

def protect(
    inputs: str,
    protect_rules: List[Dict],
    action: str = "Response cannot be generated as the input fails the checks",
    reason: bool = False,
    timeout: int = 30000,
) -> Dict:
    """
    Evaluate input strings against protection rules.

    Args:
        inputs: Single string to evaluate. Can be text, image file path/URL, or audio file path/URL
        protect_rules: List of protection rule dictionaries. Each rule must contain:
            - metric: str, name of the metric to evaluate ('Toxicity', 'Tone', 'Sexism', 'Prompt Injection', 'Data Privacy')
            - contains: List[str], required for Tone metric only. Possible values: neutral, joy, love, fear, surprise,
                       sadness, anger, annoyance, confusion
            - type: str, required for Tone metric only. Either 'any' (default) or 'all'
        action: Default action message when rules fail. Defaults to "Response cannot be generated as the input fails the checks"
        reason: Whether to include failure reason in output. Defaults to False
        timeout: Timeout for evaluations in milliseconds. Defaults to 30000

    Returns:
        Dict with protection results containing:
            - status: 'passed' or 'failed'
            - messages: Action message if failed, original input if passed
            - completed_rules: List of rules that were evaluated
            - uncompleted_rules: List of rules not evaluated due to failure/timeout
            - failed_rule: Name of failed rule, or None if passed
            - reason: Explanation for failure if reason=True
            - time_taken: Total evaluation duration
    """
    eval_client = EvalClient()
    protect_client = ProtectClient(evaluator=eval_client)

    result = protect_client.protect(
        inputs=inputs,
        protect_rules=protect_rules,
        action=action,
        reason=reason,
        timeout=timeout,
    )

    return result 