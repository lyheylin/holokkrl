"""Rule flags for a game. See docs/RULES.md section 9."""

from dataclasses import asdict, dataclass

# Must match the version in docs/RULES.md. Bump it when gameplay changes, so that models
# trained under the old rules can no longer be loaded.
RULESET_VERSION = "1.1"


@dataclass(frozen=True)
class RuleConfig:
    # False: a player may play any card from hand, even if another card could capture.
    # True: a player holding any card that can capture must play one of those cards.
    must_capture_if_able: bool = False

    def signature(self):
        """Everything a saved model must match, as JSON-compatible data."""
        return {"ruleset_version": RULESET_VERSION, **asdict(self)}
