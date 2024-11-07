from pydantic_core import ValidationError

from ..decorators import handle_errors
from ..defaults import MAX_INTERACTIONS
from ..exceptions.pydantic_exceptions import ValidationException
from .chat_model import ChatModel
from .data_models import CustomerSupportResponse, SalesAgentResponse
from .prompt import Prompts, assistant_prompt, user_prompt

# Below 2 are kind of utility funcs to have better formatting of outputs


def format_question(s: str):
    return "User: " + s + "\n"


def format_answer(s: str):
    return "Agent: " + s + "\n\n"


class SyntheticDataModel:
    def __init__(self, model: ChatModel = None) -> None:
        if model is None:
            model = ChatModel()

        self._model = model

    @handle_errors(
        {
            ValidationError: lambda e: ValidationException(
                f"Validation failed with data model: {e.title}"
            )
        }
    )
    def _generate_interactions(self, source: str, response_cls):
        convos = [Prompts.gen_system_prompt(source)]
        ans = []

        for _ in range(MAX_INTERACTIONS):
            res = self._model.invoke(convos, response_format=response_cls._schema)
            res = response_cls.model_validate_json(res)

            convos.append(user_prompt(res.question))
            ans.append(format_question(res.question))

            convos.append(assistant_prompt(res.answer))
            ans.append(format_answer(res.answer))

        return "".join(ans)

    def generate_customer_support_interactions(self, source: str):
        return self._generate_interactions(source, CustomerSupportResponse)

    def generate_sales_agent_interactions(self, source: str):
        return self._generate_interactions(source, SalesAgentResponse)
