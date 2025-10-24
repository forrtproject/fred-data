import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import pandas as pd
from crossref.restful import Works, Etiquette
from grobid_client.grobid_client import GrobidClient
from validators.reference_validation import setup_reference_validation_chain
from validators.claim_validation import setup_central_claim_validation_chain
from utils.row_processor import process_single_row

if __name__ == "__main__":
    source_directory = 'fred_pdfs/'
    my_etiquette = Etiquette('FRED_DATA', 'v.1.0', 'https://github.com/forrtproject/FReD-data', 'ksiziva+fredData@gmail.com')
    works = Works(etiquette=my_etiquette)
    df = pd.read_excel('2025-10-22_COSdata_validated.xlsx', sheet_name='Sheet 1')

    print(f"Total records: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")

    # Setup validation chains
    print("\nSetting up validation chains...")
    try:
        reference_chain = setup_reference_validation_chain()
        print("✓ Reference validation chain setup complete")
    except Exception as e:
        print(f"✗ Error setting up reference chain: {e}")
        reference_chain = None

    try:
        claim_chain = setup_central_claim_validation_chain()
        print("✓ Central claim validation chain setup complete")
    except Exception as e:
        print(f"✗ Error setting up claim chain: {e}")
        claim_chain = None

    # Add new columns for results
    df['reference_match'] = ''
    df['ref_match_confidence'] = 0.0
    df['ref_match_evidence'] = ''
    df['ref_match_explanation'] = ''
    df['abstract_source'] = ''
    df['has_abstract'] = False
    df['abstract_text'] = ''
    df['is_central_claim'] = False
    df['claim_confidence'] = 0.0
    df['claim_match_type'] = ''
    df['claim_key_evidence'] = ''
    df['claim_concerns'] = ''
    df['claim_explanation'] = ''

    abstracts_data = []

    if 'ref_o' not in df.columns or 'ref_r' not in df.columns:
        print("Required columns 'ref_o' or 'ref_r' not found!")
        print("Available columns:", df.columns.tolist())
    else:
        client = GrobidClient(grobid_server="https://kermitt2-grobid.hf.space/")
        stats_lock = Lock()
        stats = {
            'validations_completed': 0,
            'claim_validations': 0,
            'with_abstract': 0,
            'abstracts_from_pdf': 0,
            'errors': 0
        }

        print(f"\nProcessing {len(df)} records in parallel...")
        max_workers = min(10, os.cpu_count() or 1)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_row = {
                executor.submit(
                    process_single_row,
                    (index, row),
                    reference_chain,
                    claim_chain,
                    works,
                    client,
                    source_directory
                ): index
                for index, row in df.iterrows()
            }

            completed = 0
            for future in as_completed(future_to_row):
                completed += 1
                index = future_to_row[future]
                try:
                    result = future.result()
                    df.at[result['index'], 'reference_match'] = result['reference_match']
                    df.at[result['index'], 'ref_match_confidence'] = result['ref_match_confidence']
                    df.at[result['index'], 'ref_match_evidence'] = result['ref_match_evidence']
                    df.at[result['index'], 'ref_match_explanation'] = result['ref_match_explanation']
                    df.at[result['index'], 'abstract_source'] = result['abstract_source']
                    df.at[result['index'], 'has_abstract'] = result['has_abstract']
                    df.at[result['index'], 'abstract_text'] = result['abstract_text']
                    df.at[result['index'], 'is_central_claim'] = result['is_central_claim']
                    df.at[result['index'], 'claim_confidence'] = result['claim_confidence']
                    df.at[result['index'], 'claim_match_type'] = result['claim_match_type']
                    df.at[result['index'], 'claim_key_evidence'] = result['claim_key_evidence']
                    df.at[result['index'], 'claim_concerns'] = result['claim_concerns']
                    df.at[result['index'], 'claim_explanation'] = result['claim_explanation']
                    if result['abstract_data']:
                        with stats_lock:
                            abstracts_data.append(result['abstract_data'])
                    with stats_lock:
                        if result['reference_match']:
                            stats['validations_completed'] += 1
                        if result['is_central_claim'] or result['claim_confidence'] > 0:
                            stats['claim_validations'] += 1
                        if result['abstract_source'] == 'crossref':
                            stats['with_abstract'] += 1
                        elif result['abstract_source'] == 'pdf':
                            stats['abstracts_from_pdf'] += 1
                        if result['error']:
                            stats['errors'] += 1
                except Exception as e:
                    print(f"Error retrieving result for row {index}: {e}")
                    with stats_lock:
                        stats['errors'] += 1

                if completed % 10 == 0:
                    print(f"\nProgress: {completed}/{len(df)} records completed")

        output_filename = '2025-10-22_COSdata_combined_validation_parallel.xlsx'
        try:
            df.to_excel(output_filename, index=False)
            print(f"\n✓ Results saved to: {output_filename}")
        except Exception as e:
            print(f"✗ Error saving results: {e}")

        if abstracts_data:
            abstracts_df = pd.DataFrame(abstracts_data)
            abstracts_csv_filename = '2025-10-22_abstracts_parallel.csv'
            try:
                abstracts_df.to_csv(abstracts_csv_filename, index=False, encoding='utf-8')
                print(f"✓ Abstracts saved to: {abstracts_csv_filename}")
                print(f"  Total abstracts collected: {len(abstracts_df)}")
            except Exception as e:
                print(f"✗ Error saving abstracts CSV: {e}")
        print("\nProcessing statistics:")

        for k, v in stats.items():
            print(f"  {k}: {v}")
