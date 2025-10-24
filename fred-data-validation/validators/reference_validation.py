from typing import Tuple
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class ReferenceMatchValidation(BaseModel):
    """Structure for reference matching validation results"""
    reference_match: str = Field(description="Classification: 'explicit', 'implicit', or 'unclear'")
    confidence: float = Field(ge=0.0, le=1.0)
    key_evidence: str = Field(description="Specific text from ref_r that supports the classification")
    explanation: str = Field(description="Detailed reasoning for the classification decision")


def setup_reference_validation_chain():
    """Setup LangChain for reference matching validation"""
    llm = ChatOpenAI(model="gpt-5-mini", temperature=0.0)
    llm_structured = llm.with_structured_output(ReferenceMatchValidation)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert in academic citation analysis.
		Your task: Determine if ref_r (replication reference) clearly indicates that it addresses ref_o (original reference).

		Classification rules:
		1. EXPLICIT: The title/text of ref_r contains the author name(s) AND/OR publication year from ref_o.
		2. IMPLICIT: The title/text of ref_r does NOT mention author/year BUT does contain the specific, unambiguous topic, effect name, or key construct from ref_o.
		3. UNCLEAR: The title/text of ref_r does NOT mention authors/year AND does NOT mention the specific topic from ref_o.

		Be conservative: only classify as explicit/implicit when there is clear textual evidence.

		Output: Return ONLY a valid JSON object matching the schema. No extra text."""),

				("human", """
		ORIGINAL REFERENCE (ref_o):
		{ref_o}

		REPLICATION REFERENCE (ref_r):
		{ref_r}

		Task: Does ref_r's text clearly indicate it addresses ref_o?

		Classify as: 'explicit', 'implicit', or 'unclear'
		Return only the JSON object.""")
    ])

    chain = prompt | llm_structured
    return chain


def validate_reference_match(chain, ref_o: str, ref_r: str) -> Tuple[str, float, str, str]:
    """Validate if ref_r clearly addresses ref_o"""
    import json
    try:
        raw_result = chain.invoke({"ref_o": ref_o, "ref_r": ref_r})
        if isinstance(raw_result, ReferenceMatchValidation):
            parsed = raw_result
        elif isinstance(raw_result, dict):
            parsed = ReferenceMatchValidation.parse_obj(raw_result)
        elif isinstance(raw_result, str):
            parsed = ReferenceMatchValidation.parse_obj(json.loads(raw_result))
        else:
            parsed = ReferenceMatchValidation.parse_obj(dict(raw_result))
        return parsed.reference_match, parsed.confidence, parsed.key_evidence, parsed.explanation
    except Exception as e:
        return "error", 0.0, f"Error: {e}", "Processing error"
