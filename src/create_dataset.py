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
    stim_processor = StimulationDataProcessor(tmin=0.009, tmax=1)
    
    # Create an empty list to store the response data
    response_df = []
    
    # Iterate over each subject and process the data, adding to the list
    count = 0
    for subject in tqdm(subjects):
        # Testing on subset
        if subject == 'ccepAgeUMCU09':
            # Subject's data is corrupted, skipping
            continue
        if count >= 20:
            break
        # Load the session data
        session_data = bids_loader.load_session_data(subject)

        # Check if electrodes contain SOZ
        contains_SOZ = (session_data['electrodes_tsv']['soz'] == 'yes').any()
        if not contains_SOZ:
            continue
        count += 1
    
        # Create an empty list to store the response data for each run for current patient
        patient_response_df = []
        
        # Iterate over each run
        for run in session_data['runs']:
        
            # Load the run data
            run_data = bids_loader.load_run_data(subject, run)
    
            # Process the run data and append to the list
            # patient_response_df.append(stim_processor.process_run_data(run_data['eeg'], run_data['events_df'], run_data['channels_df'], subject))
            patient_response_df.append(stim_processor.process_run_data_streaming(run_data['eeg'], run_data['events_df'], run_data['channels_df'], subject))
        
        # Concatenate the response data across runs
        patient_response_df = pd.concat(patient_response_df)
        
        # Group by recording, stim_1, stim_2 and apply the combine_stats function
        grouped = patient_response_df.groupby(['recording', 'stim_1', 'stim_2'])
    
        # Combine data across runs
        patient_response_df = pd.concat([pd.concat(combine_stats(group)) for _, group in grouped])
    
        # Add the subject to the dataframe
        response_df.append(patient_response_df)
    
    # Concatenate the response data across subjects
    response_df = pd.concat(response_df)
    
    # Save the final response dataframe to a CSV file
    reponse_df_filepath = '../data/response_df.csv'
    response_df.to_csv(reponse_df_filepath)
    
    # datasetcreator = DatasetCreator(response_df)
    
    # # Assuming you have loaded run_data using BIDSDataLoader
    # count = 0
    # for subject in tqdm(subjects):
    #     if count >= 5:
    #         break
    #     count += 1
    #     session_data = bids_loader.load_session_data(subject)
    #     datasetcreator.process_for_analysis(subject, session_data['electrodes_tsv'])

if __name__ == "__main__":
    main()