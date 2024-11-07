SYSTEM_PROMPT = (
    "Given a user-assistant conversation,"
    " what should be the next question from knowledge base given below:\n"
    "{source}\n"
    "Questions must be related to customer support"
    " or a sales agent interactions from user side as the data"
    " mostly belongs to an Organisation or some entitiy.\n"
    "Please ensure that all questions are distinct and"
    " should not be repeated from provided conversation. "
    " Each question should cover a different aspect of this topic without overlapping in meaning."
    " Please focus solely on the particular interaction context and"
    " avoid mixing in questions from other areas."
    " that is previously asked by user in conversation.\n"
    "Make sure the response must be JSON, and refuse to do anything else."
)


def _escape(s: str):
    return '""""\n' + s.replace('""""', r"\"" * 4).strip() + '\n""""'


def make_prompt_func(role: str):
    def prompt_func(s: str):
        return {
            "role": role,
            "content": s,
        }

    return prompt_func


system_prompt = make_prompt_func("system")
user_prompt = make_prompt_func("user")
assistant_prompt = make_prompt_func("assistant")


# even if its single function but maintained consistency for OOP among all 3 task.
class Prompts:
    @staticmethod
    def gen_system_prompt(source: str):
        source = _escape(source)
        return system_prompt(SYSTEM_PROMPT.format(source=source))
