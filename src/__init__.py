from .utils import ensure_envs

ensure_envs(["ENCRYPTED_COOKIE_KEY", "OPENAI_API_KEY"], False)
