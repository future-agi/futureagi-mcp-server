import os
from enum import Enum

from ..constants import MODEL_HUB_DEVELOP_ID


class Routes(Enum):
    BASE_URL = os.getenv("FI_BASE_URL")
    MODEL_HUB = f"{BASE_URL}/model-hub"
    DEVELOPS = f"{MODEL_HUB}/develops/{MODEL_HUB_DEVELOP_ID}"
    EVALS_LIST = f"{DEVELOPS}/get_evals_list/"
    RUN_EVAL = f"{MODEL_HUB}/run-eval"

    @staticmethod
    def eval_structure(template_id: str) -> str:
        return f"{Routes.DEVELOPS.value}/get_eval_structure/{template_id}/"
