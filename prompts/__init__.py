"""All LLM prompts live here as constants, so they can be versioned and diffed."""

from .researcher import RESEARCH_SYSTEM, RESEARCH_USER, EXTRACT_INSTRUCTION
from .verifier import VERIFY_SYSTEM, VERIFY_USER
from .patterns import PATTERN_SYSTEM, PATTERN_USER

__all__ = [
    "RESEARCH_SYSTEM", "RESEARCH_USER", "EXTRACT_INSTRUCTION",
    "VERIFY_SYSTEM", "VERIFY_USER", "PATTERN_SYSTEM", "PATTERN_USER",
]
