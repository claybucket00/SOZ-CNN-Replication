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
    stim_processor = StimulationDataProcessor(tmin=0.009, tmax=1)
    #subjects = bids_loader.load_subjects()
    
    # Create an empty list to store the response data
    response_df_batch = []


    # Grab the subject_id strings from the existing df
    # processed_subjects = response_df['subject'].unique()

    subjects_to_add = [
    'ccepAgeUMCU46',
    'ccepAgeUMCU47',
    'ccepAgeUMCU48',
    'ccepAgeUMCU49',
    'ccepAgeUMCU51',
    'ccepAgeUMCU52',
    'ccepAgeUMCU53',
    'ccepAgeUMCU55',
    'ccepAgeUMCU57',
    'ccepAgeUMCU58',
    'ccepAgeUMCU59',
    'ccepAgeUMCU60',
    'ccepAgeUMCU61',
    'ccepAgeUMCU63',
    'ccepAgeUMCU65',
    'ccepAgeUMCU69'
    ]    
    
    count = 0
    # Iterate over each subject and process the data, adding to the list
    for subject in tqdm(subjects_to_add):
        # Batching
        if count >= 1:
            break
        count += 1
        # if subject in processed_subjects:
        #     continue
        # Load the session data
        session_data = bids_loader.load_session_data(subject)

        if not session_data:
            continue

        # Check if electrodes contain SOZ
        contains_SOZ = (session_data['electrodes_tsv']['soz'] == 'yes').any()
        if not contains_SOZ:
            continue
    
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
        response_df_batch.append(patient_response_df)
    
    # Concatenate the response data across subjects
    response_df_batch = pd.concat(response_df_batch)

    reponse_df_filepath = '../data/response_df.csv'
    response_df = pd.read_csv(reponse_df_filepath)

    response_df = pd.concat([response_df, response_df_batch], ignore_index=True)
    
    # Save the final response dataframe to a CSV file
    reponse_df_filepath = '../data/response_df.csv'
    response_df.to_csv(reponse_df_filepath)

    num_of_subjects = len(response_df['subject'].unique())
    print(f'Final number of subjects: {num_of_subjects}')

if __name__ == "__main__":
    main()