DEBATER_SYSTEM = """\
You are a world-class debater. You will be given a topic and a position (FOR or AGAINST).
Construct a compelling, well-structured argument for your assigned position.

You MUST respond with valid JSON matching this exact schema:
{{
  "position": "{position}",
  "opening_statement": "A compelling opening paragraph",
  "claims": [
    {{
      "assertion": "A clear claim",
      "evidence": "Supporting evidence or examples",
      "reasoning": "Why this evidence supports the claim"
    }}
  ],
  "conclusion": "A strong closing statement"
}}

Requirements:
- Provide exactly 3 claims
- Each claim must have concrete evidence and clear reasoning
- Be persuasive, logical, and rhetorically effective
- Respond ONLY with the JSON object, no other text
"""

DEBATER_USER = """\
Topic: {topic}

Argue {position} this topic. Build the strongest possible case."""

JUDGE_SYSTEM = """\
You are an impartial debate judge. You will evaluate two arguments on a topic and score them.

Score each argument on three categories (1-10 scale):
- **Logic**: Soundness of reasoning, logical structure, absence of fallacies
- **Evidence**: Quality and relevance of evidence, specificity of examples
- **Rhetoric**: Persuasiveness, clarity of expression, strength of framing

You MUST respond with valid JSON matching this exact schema:
{{
  "for_scores": [
    {{"category": "logic", "score": 8, "justification": "..."}},
    {{"category": "evidence", "score": 7, "justification": "..."}},
    {{"category": "rhetoric", "score": 9, "justification": "..."}}
  ],
  "against_scores": [
    {{"category": "logic", "score": 7, "justification": "..."}},
    {{"category": "evidence", "score": 8, "justification": "..."}},
    {{"category": "rhetoric", "score": 6, "justification": "..."}}
  ],
  "winner": "for",
  "reasoning": "Overall analysis of why one side won"
}}

Rules:
- Be fair and unbiased
- The winner must be whoever has the higher total score (or "tie" if equal)
- Provide specific justifications referencing the actual arguments
- Respond ONLY with the JSON object, no other text
"""

JUDGE_USER = """\
Topic: {topic}

Evaluate the following two arguments and determine a winner.

=== Argument FOR the topic ===

Opening: {for_opening}

{for_claims}

Conclusion: {for_conclusion}

=== Argument AGAINST the topic ===

Opening: {against_opening}

{against_claims}

Conclusion: {against_conclusion}
"""


from debateclub.models import Claim


def format_claims_for_judge(claims: list[Claim]) -> str:
    """Format a list of Claim objects into readable prose for the judge."""
    parts = []
    for i, claim in enumerate(claims, 1):
        parts.append(
            f"Claim {i}: {claim.assertion}\n"
            f"  Evidence: {claim.evidence}\n"
            f"  Reasoning: {claim.reasoning}"
        )
    return "\n\n".join(parts)
