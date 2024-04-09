
#Date, Name, Total Family Members, Date of Birth, Country of Origin, Health Problem(T/F), Explain Health Problem, Victim of Crime/Violence(T/F), Explain Crime/Violence, LGBTQ+, Notes
columns = ["Date", "Name", "Total Family Members", "Date of Birth", "Country of Origin", "Health Problem", "Explain Health Problem", "Victim of Crime/Violence", "Explain Crime/Violence", "LGBTQ+", "Notes"]

import os
import glob
import pandas as pd
from datetime import datetime, timedelta
import numpy as np 



def combine_csvs( output_file):
    # List all CSV files in the folder
    folder_path = os.getcwd()

    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
    # Initialize an empty list to store DataFrames
    dfs = []
    
    # Iterate over each CSV file and read it as a DataFrame
    for csv_file in csv_files:
        if csv_file.split("/")[-1] != output_file:
            print(csv_file)
            df = pd.read_csv(csv_file)
            replace_nan_with_random_date(df,"04/16/2021", "06/12/2021")
            # Apply the function to the 'Dates' column
            df['Date'] = df['Date'].apply(format_date)

            dfs.append(df)
    

    # Drop the original columns if needed
    #df = df.drop(columns=col_names)
    df = pd.concat(dfs, ignore_index=True)




    # Iterate over rows
    # Drop the original columns if needed
    #df = df.drop(columns=col_names)

    
    col_names = ["First Name","Middle Name","Last Name"]
    
    def combine_columns(row):
        return ' '.join(str(val) for val in row if pd.notna(val))

    # Apply the function to each row across the specified columns
    df['Name'] = df[col_names].apply(combine_columns, axis=1)

    df = remove_same_party_members(df)
    df.to_csv("check.csv")
    
    df = df.rename(columns={'Family Size': 'Total Family Members', 'Birth Country' : 'Country of Origin', "DOB" : "Date of Birth", "Notas generales del caso" : "Notes","LGBT+ Risk" : "LGBTQ+", "Imminent Danger Explain" : "Explain Crime/Violence", "Imminent Danger" : "Victim of Crime/Violence" ,  "Physical / Mental Health Issue": "Health Problem", "Physical / Mental Health Issue Explain" : "Explain Health Problem" })
    df = df[columns]
    
    df['Total Family Members'] = df["Total Family Members"].apply(add_family_numbers)

    df.to_csv(output_file, index=False)
    
    print(f"Combined {len(csv_files)} CSV files into {output_file}")

# Example usage

def replace_nan_with_random_date(df, start_date, end_date):
    # Convert start_date and end_date to datetime objects
    start_datetime = datetime.strptime(start_date, '%m/%d/%Y')
    end_datetime = datetime.strptime(end_date, '%m/%d/%Y')

    # Iterate through each row
    for index, row in df.iterrows():
        # Check if the Date column contains NaN
        if pd.isna(row['Date']):
            # Generate a random date between start_date and end_date
            random_date = start_datetime + \
                timedelta(days=np.random.randint((end_datetime - start_datetime).days))
            # Replace NaN with the random date
            df.at[index, 'Date'] = random_date.strftime('%m/%d/%Y')

    return df

def format_date(date_str):
    # Parse the date string into a datetime object
    date_obj = pd.to_datetime(date_str)
    # Format the datetime object into mm/dd/yyyy format
    formatted_date = date_obj.strftime('%m/%d/%Y')
    return formatted_date

def add_family_numbers(fam):
    if "Viajo con" in fam:
        if "mas de" in fam:
            return 10
        return int(fam[0]) + 1
    elif "Yo viajo solo" in fam:
        return 1
    else:
        try:
            return int(fam)
        except:
            print(fam)
            return 1
    
def remove_same_party_members(df):
    df["US Contact Phone Number"] = df["US Contact Phone Number"].apply(universal_phone_number_format)
    df = df.drop_duplicates(subset=['Family Size','US Contact Phone Number'], keep='first')
    return df
#get rid of all whitespaces, paranthesis, and non-digit chars to ensure be able to use phone number as duplicate identifier
def universal_phone_number_format(phone_number):
    if type(phone_number) is not str:
        return None
    return(''.join(char for char in phone_number if char.isdigit()))[-10:]

output_file = 'T42 Screenings (Combined) data.csv'
combine_csvs(output_file)
