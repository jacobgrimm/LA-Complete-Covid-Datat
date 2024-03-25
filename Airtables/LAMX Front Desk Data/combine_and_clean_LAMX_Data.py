import os
import glob
import pandas as pd

def combine_csvs( output_file):
    # List all CSV files in the folder
    folder_path = os.getcwd()

    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
    
    # Initialize an empty list to store DataFrames
    dfs = []
    
    # Iterate over each CSV file and read it as a DataFrame
    for csv_file in csv_files:
        if csv_file.split("/")[-1] != output_file:
            df = pd.read_csv(csv_file)
            dfs.append(df)
    
    # Concatenate all DataFrames into a single DataFrame
    df = pd.concat(dfs, ignore_index=True)
    df = df.dropna(axis=1, how='all')
    
    col_names = [
                 "# Family Members",
    "# Family Members Other",
    "¿Cuántas personas en total están viajando?"]
    
    df['Total Family Members'] = ''

    # Iterate over rows
    for index, row in df.iterrows():
        merged_value = ''
        # Iterate over columns in the preferred order
        for col in col_names:
            if pd.notna(row[col]):  # Check if the value is not NaN
                if type(row[col]) is str:
                    merged_value = row[col].lower()
                else:
                    merged_value = row[col]
                break  # Break the loop if a non-NaN value is found
        df.at[index, 'Total Family Members'] = merged_value

    # Drop the original columns if needed
    df = df.drop(columns=col_names)
    df['Total Family Members'] = df['Total Family Members'].replace("1 (viajo solo)", 1)
    df['Total Family Members'] = df['Total Family Members'].replace("mas de 10", 10)
    df['Total Family Members'] = df['Total Family Members'].replace("mas de 6", 6)
    df['Total Family Members'] = pd.to_numeric(df['Total Family Members'], errors="coerce").fillna(1)




    col_names = ["Explique el crimen o violencia en Mexico:",
            "Identifique brevemente el crimen o violencia en Mexico:",
        "Explique brevemente el crimen o violencia en Mexico:",
        "Que tipo de violencia o crimen? "]
    
    def combine_columns(row):
        return ','.join(str(val) for val in row if pd.notna(val))

    # Apply the function to each row across the specified columns
    df['Crime/Violence Mexico'] = df[col_names].apply(combine_columns, axis=1)

    # Iterate over rows
    # Drop the original columns if needed
    df = df.drop(columns=col_names)

    
    nan_percentages = df.isna().mean() * 100

    # Set a threshold percentage for considering a column as mostly empty
    threshold_percentage = 50  # Adjust this threshold as needed

    # Get the column names that have a NaN percentage greater than the threshold
    mostly_empty_columns = nan_percentages[nan_percentages > threshold_percentage].index

    # Drop the mostly empty columns from the DataFrame
    df = df.drop(columns=mostly_empty_columns)
    df = df.drop(columns=["¿Usa WhatsApp?", "¿Cuál es el mejor número de teléfono para contactarlo?"])
    column_to_move = df.pop("Crime/Violence Mexico")
    column_2  = df.pop("Total Family Members")
    
    df.insert(9, "Crime/Violence Mexico", column_to_move )
    df.insert(3, "Total Family Members", column_2 )
    df["Victim of Crime/Violence"] = df["¿Ha sido víctima de algún crimen o violencia en México?"]
    df = df.rename(columns = {"¿Ha sido víctima de algún crimen o violencia en México?": "Victim of Crime/Violence in Mexico"})
    df = df.rename(columns={'Cual es su nombre?': 'Name', 'Fecha de Llamada': 'Date', '¿Cual es tu país de origen?' : 'Country of Origin', "Fecha de Nacimiento" : "Date of Birth", "Notas generales del caso" : "Notes", "¿Se identifica como miembro de la comunidad LGBTQ+?" : "LGBTQ+", "Crime/Violence Mexico" : "Explain Crime/Violence" , "¿Tiene algún problema de salud o discapacidad grave?": "Health Problem", "Explique brevemente el problema de salud grave o discapacidad:" : "Explain Health Problem" })
    print(df.columns)
    
    df.to_csv(output_file, index=False)
    
    print(f"Combined {len(csv_files)} CSV files into {output_file}")

# Example usage
output_file = 'LAMX Front Desk (Combined) data.csv'
combine_csvs(output_file)
