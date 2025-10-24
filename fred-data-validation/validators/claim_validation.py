from typing import Tuple
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class CentralClaimValidation(BaseModel):
    """Structure for central claim validation results"""
    is_central_claim: bool = Field(description="Whether the claim is central")
    confidence: float = Field(ge=0.0, le=1.0)
    match_type: str = Field(description="How the claim maps: 'exact', 'construct_mapping', 'peripheral', or 'unclear'")
    key_evidence: str = Field(description="Key sentence(s) from the title/abstract that support or contradict centrality")
    concerns: str = Field(description="Methodological or mapping concerns (if any)")
    explanation: str = Field(description="Detailed reasoning for the decision")


def setup_central_claim_validation_chain():
    """Setup LangChain for central claim validation"""
    llm = ChatOpenAI(model="gpt-5-mini", temperature=0.0)
    llm_structured = llm.with_structured_output(CentralClaimValidation)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert in research methodology.
			Your task: Decide whether the provided claim from an original study is a CENTRAL CLAIM of that article based on the TITLE and ABSTRACT.

			Definition — Central Claim:
			- Central claims are the MAIN research questions or PRIMARY FINDINGS that the article emphasizes
			- They are usually referenced in the TITLE and explicitly mentioned in the ABSTRACT
			- The abstract usually already mentions results regarding these central claims
			- Central claims can be tested with specific methods

			Evaluation Guidance:
			- Focus ONLY on TITLE and ABSTRACT
			- Be conservative: Return true ONLY when there is clear alignment

			Output: Return ONLY a valid JSON object matching the schema. No extra text."""),

					("human", """
			ORIGINAL STUDY:
			Title: {title}
			DOI: {doi}
			Abstract: {abstract}

			CLAIM (from original paper): {claim}

			Task: Is this claim a central claim of the article based on title and abstract?
			Return only the JSON object.""")
    ])

    chain = prompt | llm_structured
    return chain


def validate_central_claim(
    chain, claim: str, abstract: str,
    title: str, doi: str
    ) -> Tuple[bool, float, str, str, str, str]:
    """Validate if claim is central to the article"""
    import json
    try:
        raw_result = chain.invoke({"claim": claim, "abstract": abstract, "title": title, "doi": doi})
        if isinstance(raw_result, CentralClaimValidation):
            parsed = raw_result
        elif isinstance(raw_result, dict):
            parsed = CentralClaimValidation.parse_obj(raw_result)
        elif isinstance(raw_result, str):
            parsed = CentralClaimValidation.parse_obj(json.loads(raw_result))
        else:
            parsed = CentralClaimValidation.parse_obj(dict(raw_result))
        return parsed.is_central_claim, parsed.confidence, parsed.match_type, parsed.key_evidence, parsed.concerns, parsed.explanation
    except Exception as e:
        return False, 0.0, "error", f"Error: {e}", "Processing error", ""
