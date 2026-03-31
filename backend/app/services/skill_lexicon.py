"""Shared skill keywords for resume/JD parsing and tailoring."""

KNOWN_SKILLS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "next.js",
    "node.js",
    "vue",
    "angular",
    "go",
    "rust",
    "c++",
    "c#",
    "fastapi",
    "django",
    "flask",
    "spring",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "elasticsearch",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "terraform",
    "git",
    "graphql",
    "kafka",
    "rabbitmq",
    "linux",
    "jenkins",
    "ci/cd",
]


def skills_from_known_lexicon(text: str, limit: int = 24) -> list[str]:
    lowered = text.lower()
    found = [skill for skill in KNOWN_SKILLS if skill in lowered]
    return found[:limit]
