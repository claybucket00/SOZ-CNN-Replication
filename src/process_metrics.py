from create_dataset_utils import *
from tqdm import tqdm
import argparse
from pathlib import Path
import glob
import os


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
    # subjects = bids_loader.load_subjects()

    # Save the final response dataframe to a CSV file
    reponse_df_filepath = '../data/response_df.csv'
    response_df = pd.read_csv(reponse_df_filepath)
    
    datasetcreator = DatasetCreator(response_df)

    # Grab the subject_id strings from the df
    subjects = response_df['subject'].unique()
    
    
    paths = glob.glob('../data/mean/X_recording_*.npy')
    processed_subjects = [
        os.path.basename(p)
          .replace('X_recording_', '')
          .replace('.npy', '')
        for p in paths
    ]

    new_subjects = [item for item in subjects if item not in set(processed_subjects)]
    
    # Assuming you have loaded run_data using BIDSDataLoader
    for subject in tqdm(new_subjects):
        if subject in processed_subjects:
            continue
        session_data = bids_loader.load_session_data(subject)
        datasetcreator.process_for_analysis(subject, session_data['electrodes_tsv'])

if __name__ == "__main__":
    main()