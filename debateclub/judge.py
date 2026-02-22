from debateclub.client import OpenRouterClient
from debateclub.models import Argument, Judgment
from debateclub.prompts import (
    JUDGE_SYSTEM,
    JUDGE_USER,
    format_claims_for_judge,
)


async def evaluate(
    client: OpenRouterClient,
    model: str,
    topic: str,
    for_argument: Argument,
    against_argument: Argument,
) -> Judgment:
    """Have the judge model evaluate both arguments and return a judgment."""
    user_prompt = JUDGE_USER.format(
        topic=topic,
        for_opening=for_argument.opening_statement,
        for_claims=format_claims_for_judge(for_argument.claims),
        for_conclusion=for_argument.conclusion,
        against_opening=against_argument.opening_statement,
        against_claims=format_claims_for_judge(against_argument.claims),
        against_conclusion=against_argument.conclusion,
    )

    judgment = await client.generate_parsed(
        model=model,
        system=JUDGE_SYSTEM,
        user=user_prompt,
        schema=Judgment,
    )
    judgment.model_id = model
    return judgment
