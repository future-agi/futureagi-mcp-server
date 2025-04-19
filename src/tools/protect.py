from fi.evals import EvalClient
from fi.evals import ProtectClient
from typing import List, Dict
from src.logger import get_logger
from src.constants import DEFAULT_PROTECT_ACTION, DEFAULT_PROTECT_TIMEOUT
from src.models import ProtectRule

logger = get_logger()


def protect(
    inputs: str,
    protect_rules: List[ProtectRule],
    action: str = DEFAULT_PROTECT_ACTION,
    reason: bool = False,
    timeout: int = DEFAULT_PROTECT_TIMEOUT,
) -> Dict:
    """
    Evaluate input strings against protection rules.

    Args:
        inputs: Single string to evaluate. Can be text, image file path/URL, or audio file path/URL
        protect_rules: List of protection rule objects adhering to ProtectRule model.
            Each rule must contain:
            - metric: str, name of the metric to evaluate ('Toxicity', 'Tone', 'Sexism', 'Prompt Injection', 'Data Privacy')
            - contains: List[str], required for Tone metric only.
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

        # Clean up rules before passing to protect_client
        cleaned_rules = []
        for rule in protect_rules:
            rule_dict = rule.model_dump()
            if rule_dict["metric"] == "Tone":
                # For Tone metric, keep metric, contains, and type
                cleaned_rule = {
                    "metric": rule_dict["metric"],
                    "contains": rule_dict["contains"],
                }
                if rule_dict.get("type"):
                    cleaned_rule["type"] = rule_dict["type"]
            else:
                # For non-Tone metrics, only keep metric
                cleaned_rule = {"metric": rule_dict["metric"]}
            cleaned_rules.append(cleaned_rule)

        result = protect_client.protect(
            inputs=inputs,
            protect_rules=cleaned_rules,
            action=action,
            reason=reason,
            timeout=client_timeout,
        )

        status = result.get("status", "unknown")
        if status == "failed":
            failed_rule = result.get("failed_rule", "unknown")
            if reason and "reason" in result:
                result["messages"] = f"{action}. Reason: {result['reason']}"
            else:
                result["messages"] = action

        return result
    except Exception as e:
        logger.error(f"Error during protection evaluation: {e}", exc_info=True)
        return {
            "status": "error",
            "messages": f"Error during protection evaluation: {e}",
        }
