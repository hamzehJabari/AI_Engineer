"""
Prompt templates for IntelliWheels AI agents.
"""
import os


def load_prompt(template_name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompts_dir = os.path.dirname(__file__)
    filepath = os.path.join(prompts_dir, template_name)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()
