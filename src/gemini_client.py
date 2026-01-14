"""
Gemini API client for code generation.
"""

import google.generativeai as genai
from typing import Optional
from loguru import logger

from .config import Config


class GeminiClient:
    """Client for interacting with Google's Gemini AI."""

    def __init__(self, config: Config):
        """
        Initialize Gemini client.

        Args:
            config: Application configuration
        """
        self.config = config
        genai.configure(api_key=config.gemini_api_key)
        self.model = genai.GenerativeModel(config.gemini_model)
        logger.info(f"Initialized Gemini client with model: {config.gemini_model}")

    def generate_code(
        self,
        prompt: str,
        context: Optional[str] = None,
        previous_error: Optional[str] = None,
    ) -> str:
        """
        Generate code using Gemini AI.

        Args:
            prompt: The code generation prompt
            context: Additional context (previous code, project description, etc.)
            previous_error: Error from previous attempt (for fix iterations)

        Returns:
            Generated code as string

        Raises:
            Exception: If generation fails
        """
        full_prompt = self._build_prompt(prompt, context, previous_error)

        try:
            logger.debug(f"Sending prompt to Gemini: {full_prompt[:200]}...")
            response = self.model.generate_content(full_prompt)

            if not response.text:
                raise ValueError("Empty response from Gemini API")

            logger.info("Successfully generated code from Gemini")
            return response.text

        except Exception as e:
            logger.error(f"Error generating code with Gemini: {e}")
            raise

    def _build_prompt(
        self, prompt: str, context: Optional[str], previous_error: Optional[str]
    ) -> str:
        """
        Build the complete prompt for Gemini.

        Args:
            prompt: Base prompt
            context: Additional context
            previous_error: Previous error if any

        Returns:
            Complete prompt string
        """
        parts = []

        # Add system context
        parts.append(
            "You are an expert software developer. Generate clean, production-ready code "
            "following best practices for the specified language and framework."
        )

        # Add context if provided
        if context:
            parts.append(f"\n### Context:\n{context}")

        # Add previous error if this is a fix attempt
        if previous_error:
            parts.append(
                f"\n### Previous Error:\n{previous_error}\n"
                "Please fix the code to resolve this error."
            )

        # Add main prompt
        parts.append(f"\n### Task:\n{prompt}")

        # Add formatting instructions
        parts.append(
            "\n### Instructions:\n"
            "- Return ONLY the code, without explanations or markdown formatting\n"
            "- Do not include ```language``` code blocks\n"
            "- Include necessary imports and dependencies\n"
            "- Add brief inline comments for complex logic\n"
            "- Ensure the code is complete and can be executed/compiled immediately"
        )

        return "\n".join(parts)

    def extract_code_from_response(self, response: str) -> str:
        """
        Extract code from Gemini's response, handling markdown code blocks.

        Args:
            response: Raw response from Gemini

        Returns:
            Extracted code
        """
        # Remove markdown code blocks if present
        lines = response.strip().split("\n")

        # Check if response starts with code block
        if lines[0].startswith("```"):
            # Remove first line (```language)
            lines = lines[1:]

            # Remove last line if it's ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

        return "\n".join(lines)
