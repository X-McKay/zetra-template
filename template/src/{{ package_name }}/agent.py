"""Deny-by-default primitives for a zero-trust agent."""

from dataclasses import dataclass, field


class PermissionDeniedError(PermissionError):
    """Raised when an action is not explicitly allowed by policy."""


@dataclass(frozen=True)
class Policy:
    """An explicit allowlist of actions. Anything not listed is denied."""

    allowed_actions: frozenset[str] = field(default_factory=frozenset)

    def is_allowed(self, action: str) -> bool:
        return action in self.allowed_actions


@dataclass
class Agent:
    """An agent that must be authorized by its policy before every action."""

    name: str
    policy: Policy = field(default_factory=Policy)

    def authorize(self, action: str) -> None:
        if not self.policy.is_allowed(action):
            msg = f"{self.name}: action {action!r} denied by policy"
            raise PermissionDeniedError(msg)
