"""Save and load trained models together with the rules they were trained under.

Always use these instead of calling model.save() or PPO.load() directly. Rule flags don't
change the action or observation spaces, so Stable-Baselines3 can't detect a model running
under the wrong rules.
"""

import json
from pathlib import Path
import zipfile

from stable_baselines3 import PPO

_RULES_MEMBER = "koikoi_rules.json"


class RulesMismatchError(ValueError):
    """A model's rules don't match the engine it would run on."""


def _zip_path(path):
    path = Path(path)
    return path if path.suffix == ".zip" else Path(f"{path}.zip")


def _env_signature(env):
    """Return the rule signature of a Gymnasium env or a VecEnv."""
    if hasattr(env, "get_attr"):
        signatures = [rules.signature() for rules in env.get_attr("rules")]
        if any(s != signatures[0] for s in signatures):
            raise RulesMismatchError(f"Environments use different rules: {signatures}")
        return signatures[0]
    return env.unwrapped.rules.signature()


def save_model(model, path):
    """Save a model, recording the rules of the environment it was trained on."""
    env = model.get_env()
    if env is None:
        raise ValueError("Model has no environment, so its rules are unknown.")
    signature = _env_signature(env)

    path = _zip_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    model.save(path)
    with zipfile.ZipFile(path, "a") as archive:
        archive.writestr(_RULES_MEMBER, json.dumps(signature))
    return path


def read_model_rules(path):
    """Return the rule signature stored in a saved model, or None if it has none."""
    with zipfile.ZipFile(_zip_path(path)) as archive:
        if _RULES_MEMBER not in archive.namelist():
            return None
        return json.loads(archive.read(_RULES_MEMBER))


def load_model(path, env, algo=PPO):
    """Load a model to run on env, refusing it unless the rules match exactly."""
    path = _zip_path(path)
    model_rules = read_model_rules(path)
    if model_rules is None:
        raise RulesMismatchError(f"{path} has no recorded rules, so it can't be run safely.")

    env_rules = _env_signature(env)
    if model_rules != env_rules:
        raise RulesMismatchError(
            f"{path} was trained under different rules.\n"
            f"  Model:  {model_rules}\n"
            f"  Engine: {env_rules}"
        )
    return algo.load(path, env=env)
