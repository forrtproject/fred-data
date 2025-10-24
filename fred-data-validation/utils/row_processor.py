import os
import shutil
import tempfile
import traceback
import pandas as pd
from utils.xml_utils import check_abstract_in_xml
from validators.reference_validation import validate_reference_match
from validators.claim_validation import validate_central_claim

def process_single_row(
    row_data: tuple,
    reference_chain,
    claim_chain,
    works,
    client,
    source_directory: str
) -> dict:
    """
    Process a single row - designed to be run in parallel
    Returns a dictionary with all results for this row
    """
    index, row = row_data
    result = {
        'index': index,
        'reference_match': '',
        'ref_match_confidence': 0.0,
        'ref_match_evidence': '',
        'ref_match_explanation': '',
        'abstract_source': '',
        'has_abstract': False,
        'abstract_text': '',
        'is_central_claim': False,
        'claim_confidence': 0.0,
        'claim_match_type': '',
        'claim_key_evidence': '',
        'claim_concerns': '',
        'claim_explanation': '',
        'abstract_data': None,
        'error': None
    }

    temp_dir = None

    try:
        print(f"[Row {index + 1}] Starting processing...")

        # STEP 1: Reference matching
        if (pd.notna(row['ref_o']) and str(row['ref_o']).strip() and
            pd.notna(row['ref_r']) and str(row['ref_r']).strip()):

            ref_o_text = str(row['ref_o']).strip()
            ref_r_text = str(row['ref_r']).strip()

            if reference_chain:
                reference_match, confidence, evidence, explanation = validate_reference_match(
                    reference_chain, ref_o_text, ref_r_text
                )
                
                result['reference_match'] = reference_match
                result['ref_match_confidence'] = confidence
                result['ref_match_evidence'] = evidence
                result['ref_match_explanation'] = explanation

                print(f"[Row {index + 1}] Reference: {reference_match.upper()} ({confidence:.2f})")

                # STEP 2: If NOT explicit, fetch abstract and validate claim
                if reference_match != "explicit":
                    abstract_text = ""
                    abstract_source = "none"
                    crossref_result = None

                    # Try Crossref
                    try:
                        crossref_result = works.doi(row['doi_o'])
                        if 'abstract' in crossref_result and crossref_result['abstract'] and crossref_result['abstract'].strip():
                            abstract_text = crossref_result['abstract'].strip()
                            abstract_source = "crossref"
                            print(f"[Row {index + 1}] Abstract from Crossref")
                    except Exception as crossref_error:
                        print(f"[Row {index + 1}] Crossref error: {crossref_error}")

                    # Try PDF if no Crossref abstract
                    if (not abstract_text and 'file_o' in row and 
                        pd.notna(row['file_o']) and str(row['file_o']).strip()):

                        try:
                            pdf_filename = str(row['file_o']).strip()
                            xml_filename = pdf_filename.replace('.pdf', '.grobid.tei.xml')
                            xml_path = os.path.join('fred_xml_output', xml_filename)

                            if os.path.exists(xml_path):
                                abstract_found, abstract_content = check_abstract_in_xml(xml_path)
                                if abstract_found:
                                    abstract_text = abstract_content
                                    abstract_source = "pdf"
                                    print(f"[Row {index + 1}] Abstract from existing XML")
                            else:
                                temp_dir = tempfile.mkdtemp()
                                try:
                                    source_file_path = os.path.join(source_directory, pdf_filename)
                                    if os.path.exists(source_file_path):
                                        temp_file_path = os.path.join(temp_dir, pdf_filename)
                                        shutil.copy2(source_file_path, temp_file_path)
                                        client.process("processFulltextDocument", temp_dir, "fred_xml_output")

                                        if os.path.exists(xml_path):
                                            abstract_found, abstract_content = check_abstract_in_xml(xml_path)
                                            if abstract_found:
                                                abstract_text = abstract_content
                                                abstract_source = "pdf"
                                                print(f"[Row {index + 1}] Abstract from new XML")
                                finally:
                                    if temp_dir and os.path.exists(temp_dir):
                                        shutil.rmtree(temp_dir)
                                        temp_dir = None
                        except Exception as pdf_error:
                            print(f"[Row {index + 1}] PDF error: {pdf_error}")

                    # Update results
                    result['abstract_source'] = abstract_source
                    result['has_abstract'] = bool(abstract_text)
                    result['abstract_text'] = abstract_text

                    # Store abstract data for CSV
                    if abstract_text and 'doi_o' in row and pd.notna(row['doi_o']):
                        result['abstract_data'] = {
                            'doi_o': str(row['doi_o']).strip(),
                            'abstract': abstract_text,
                            'source': abstract_source
                        }

                    # Validate central claim
                    if (abstract_text and claim_chain and 
                        pd.notna(row['claim_text_o']) and str(row['claim_text_o']).strip()):

                        claim_text = str(row['claim_text_o']).strip()

                        # Get title
                        title = "Title not available"
                        if crossref_result and 'title' in crossref_result:
                            if isinstance(crossref_result['title'], list):
                                title = crossref_result['title'][0]
                            else:
                                title = str(crossref_result['title'])

                        is_central, claim_conf, match_type, claim_evidence, concerns, claim_explanation = validate_central_claim(
                            claim_chain, claim_text, abstract_text, title, row['doi_o']
                        )

                        result['is_central_claim'] = is_central
                        result['claim_confidence'] = claim_conf
                        result['claim_match_type'] = match_type
                        result['claim_key_evidence'] = claim_evidence
                        result['claim_concerns'] = concerns
                        result['claim_explanation'] = claim_explanation
                        
                        status = "CENTRAL" if is_central else "NOT CENTRAL"
                        print(f"[Row {index + 1}] Claim: {status} ({match_type}, {claim_conf:.2f})")
                else:
                    print(f"[Row {index + 1}] Explicit match - skipping claim validation")

        print(f"[Row {index + 1}] ✓ Complete")

    except Exception as e:
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        result['error'] = error_msg
        print(f"[Row {index + 1}] ✗ {error_msg}")
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    return result
