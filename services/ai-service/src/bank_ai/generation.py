from __future__ import annotations

import json

from openai import AzureOpenAI

from bank_ai.config import Settings
from bank_ai.rag import RetrievedChunk


class ExplanationGenerator:
    mode = "template"

    def generate(self, probability: float, risk_band: str, positives: list[str], risks: list[str],
                 chunks: list[RetrievedChunk]) -> str:
        sources = ", ".join(f"{chunk.title} – {chunk.section}" for chunk in chunks[:3])
        source_text = sources or "no indexed policy was available"
        return (
            f"The demo model estimates a probability of default of {probability:.1%} "
            f"({risk_band.lower()} risk band). The assessment is based on synthetic training data. "
            f"Relevant fictional policy sections: {source_text}. A human reviewer must make the decision."
        )


class AzureExplanationGenerator(ExplanationGenerator):
    mode = "azure-openai"

    def __init__(self, settings: Settings):
        self.client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )
        self.deployment = settings.azure_openai_chat_deployment

    def generate(self, probability: float, risk_band: str, positives: list[str], risks: list[str],
                 chunks: list[RetrievedChunk]) -> str:
        context = [
            {"title": chunk.title, "section": chunk.section, "content": chunk.content}
            for chunk in chunks
        ]
        prompt = {
            "task": "Explain this synthetic risk assessment. Never make or recommend a credit decision.",
            "probability_of_default": probability,
            "risk_band": risk_band,
            "positive_input_factors": positives,
            "risk_input_factors": risks,
            "fictional_policy_context": context,
        }
        response = self.client.responses.create(
            model=self.deployment,
            input=[
                {
                    "role": "system",
                    "content": "Use only supplied context. State uncertainty and cite section titles.",
                },
                {"role": "user", "content": json.dumps(prompt)},
            ],
        )
        return response.output_text


def build_generator(settings: Settings) -> ExplanationGenerator:
    if settings.ai_generation_provider == "azure-openai":
        return AzureExplanationGenerator(settings)
    return ExplanationGenerator()

