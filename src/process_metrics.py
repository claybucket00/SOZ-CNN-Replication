from create_dataset_utils import *
from tqdm import tqdm
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Create dataset for analysis from BIDS formatted data."
    )

    parser.add_argument('bids_root', type=Path, help="Root directory of the BIDS dataset.")
    args = parser.parse_args()

    bids_root = args.bids_root
    if not bids_root.exists():
        raise ValueError(f"The specified BIDS root directory does not exist: {bids_root}")
    
    mne.set_log_level('WARNING')

    # Set root directory for BIDS dataset
    bids_root = str(bids_root)
    
    # Define the BIDSDataLoader and StimulationDataProcessor
    bids_loader = BIDSDataLoader(bids_root=bids_root)
    subjects = bids_loader.load_subjects()

    # Save the final response dataframe to a CSV file
    reponse_df_filepath = '../data/response_df.csv'
    response_df = pd.read_csv(reponse_df_filepath)
    
    datasetcreator = DatasetCreator(response_df)
    
    # Assuming you have loaded run_data using BIDSDataLoader
    count = 0
    for subject in tqdm(subjects):
        if count >= 5:
            break
        count += 1
        session_data = bids_loader.load_session_data(subject)
        datasetcreator.process_for_analysis(subject, session_data['electrodes_tsv'])

if __name__ == "__main__":
    main()