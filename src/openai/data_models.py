from pydantic import BaseModel, Field

from openai.lib._parsing import type_to_response_format_param


def attach_schema(cls):
    cls._schema = type_to_response_format_param(cls)
    return cls


class Discussion(BaseModel):
    question: str = Field(
        description="The question will be asked by user."
        " The question must not be repeated again literally or figuratively"
        " if it was asked by user previously, which means question that have"
        " similar aspects and already present in conversation must not be returned."
        " Make sure that it should not be related to previous conversation anyhow."
    )

    answer: str = Field(description="Concise answer to the question given in this response.")


@attach_schema
class CustomerSupportResponse(Discussion):
    """Interaction between user and customer support
    where you must return `question` that most likely to be asked by user
    from the customer support about organisation, services, etc,
    anything related to interaction with customer support
    and answer that must be given from the customer support."""


@attach_schema
class SalesAgentResponse(Discussion):
    """Interaction between user and sales agent
    where you must return `question` that most likely to be asked by user
    from the sales agent about pricing model, etc, anything related to interaction with sales agent
    and answer that must be given from the sales agent."""
