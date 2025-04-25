from typing import Dict, List

from fi.evals import EvalClient, ProtectClient

from src.constants import DEFAULT_PROTECT_ACTION, DEFAULT_PROTECT_TIMEOUT
from src.logger import get_logger

logger = get_logger()

PROTECT_DESCRIPTION = """
    Protect input strings against harmful content using a list of protection rules.
    Do not use this tool for evaluating content. Use the evaluate tool for evaluating content.

    Args:
        inputs: Single string to evaluate. Can be text, image file path/URL, or audio file path/URL
        protect_rules: List of protection rule dictionaries. Each rule must contain:
            - metric: str, name of the metric to evaluate ('Toxicity', 'Tone', 'Sexism', 'Prompt Injection', 'Data Privacy')
            - contains: List[str], required for Tone metric only. Possible values: neutral, joy, love, fear, surprise,
                       sadness, anger, annoyance, confusion
            - type: str, required for Tone metric only. Either 'any' (default) or 'all'
        action: Default action message when rules fail. Defaults to DEFAULT_PROTECT_ACTION
        reason: Whether to include failure reason in output. Defaults to False
        timeout: Timeout for evaluations in milliseconds. Defaults to DEFAULT_PROTECT_TIMEOUT

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


async def protect(
    inputs: str,
    protect_rules: List[Dict],
    action: str = DEFAULT_PROTECT_ACTION,
    reason: bool = False,
    timeout: int = DEFAULT_PROTECT_TIMEOUT,
) -> Dict:
    """
    Protect input strings against harmful content using a list of protection rules.
    Do not use this tool for evaluating content. Use the evaluate tool for evaluating content.

    Args:
        inputs: Single string to evaluate. Can be text, image file path/URL, or audio file path/URL
        protect_rules: List of protection rule dictionaries. Each rule must contain:
            - metric: str, name of the metric to evaluate ('Toxicity', 'Tone', 'Sexism', 'Prompt Injection', 'Data Privacy')
            - contains: List[str], required for Tone metric only. Possible values: neutral, joy, love, fear, surprise,
                       sadness, anger, annoyance, confusion
            - type: str, required for Tone metric only. Either 'any' (default) or 'all'
        action: Default action message when rules fail. Defaults to DEFAULT_PROTECT_ACTION
        reason: Whether to include failure reason in output. Defaults to False
        timeout: Timeout for evaluations in milliseconds. Defaults to DEFAULT_PROTECT_TIMEOUT

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
    try:
        eval_client = EvalClient()
        protect_client = ProtectClient(evaluator=eval_client)

        # Convert timeout from milliseconds to microseconds for the client
        client_timeout = timeout * 1000
        print(f"Protecting inputs: {inputs}")
        print(f"Protect rules: {protect_rules}")
        print(f"Action: {action}")
        print(f"Reason: {reason}")
        print(f"Timeout: {client_timeout}")
        result = protect_client.protect(
            inputs=inputs,
            protect_rules=protect_rules,
            action=action,
            reason=reason,
            timeout=client_timeout,
        )
        print(f"Protection result: {result}")

        return result
    except Exception as e:
        logger.error(f"Error during protection evaluation: {e}", exc_info=True)
        return {
            "status": "error",
            "messages": f"Error during protection evaluation: {e}",
        }
