import re
from unidecode import unidecode
# List of PDF URLs to download and process
import pandas as pd
import re
import datetime
from numpy import nan
import random



"""
PLEASE NOTE the "Explique el crimen o violenica en Mexico " column does have a trailing blankspace in the original table - and the output 
df at the end we convert it to remove the blankspace

"""



def extract_date_from_string(input_string):
    # Define a regex pattern to capture the date at the beginning
    date_pattern = r'(\d{2}[._]\d{2}[._]\d{4})'

    # Search for the date pattern in the input string
    match = re.search(date_pattern, input_string)

    # If a match is found, return the matched date
    if match:
        special_chars_pattern = re.compile(r'[^a-zA-Z0-9/]')
        result_string = re.sub(special_chars_pattern, '/', match.group(1))
        if "0202" in result_string:
            result_string = result_string.replace("0202", "2022")

        return result_string
    else:
        return None  # Return None if no date is found




def search_for_keywords(row, keyword_list):
    if not pd.isna(row["Medical Condition and/or Vulnerability"]):
        for word in keyword_list:
                if word in row["Medical Condition and/or Vulnerability"].lower():
                    return True

    if not pd.isna(row["Explique el crimen o violenica en Mexico "]):
        for word in keyword_list:
                if word in row["Explique el crimen o violenica en Mexico "].lower():
                    return True
                    
    if  not pd.isna(row["Notas"]):
        for word in keyword_list:
                if word in row["Notas"].lower():
                    return True
                
    if  not pd.isna(row["Referred to DMRS"]):
        for word in keyword_list:
                if word in row["Referred to DMRS"].lower():
                    return True

    return False

    

def find_lgbtq(row):
    word_list = ["lgbt", "lgbt+", "gay", "lesbian", "homosexual", "trans", "bisexual"]
    return search_for_keywords(row, keyword_list=word_list)


def find_violence(row):
    word_list = ["viola", "rape", "abuso","gbv", 'threat', 'amenaz', 'muer', 'secuestr', 'kidnap','tortur']
    return search_for_keywords(row, keyword_list=word_list)


def combine_birthyears(row):
    birthday_list = []    
    for index in row.dropna().index.tolist():
        if "Birthday" in index:
            birthday_list.append(row[index])
    
    return birthday_list

def count_number_in_party(row):
    return len(row['All Birth Years'])

def find_date_of_intake (row):
    
    if not pd.isna(row["G28"]):
        return extract_date_from_string(row["G28"])
        
    elif not pd.isna(row["Date Presented at POE"]):
        return row["Date Presented at POE"]
    
    elif not pd.isna(row["Date Request Sent to CBP"]):
        return row["Date Request Sent to CBP"]    
    else:
        return "09/01/2021"
        
    
def assing_date_of_birth(birth_year):
    try:
        start_date = datetime.date(birth_year, 1, 1)
        end_date = datetime.date(birth_year, 12, 31)
        random_day = start_date + datetime.timedelta(days=random.randint(0, (end_date - start_date).days))
        return random_day

    except Exception as e:
        print(e)

    
def main(main_csv, supplemental_birthday_csv):
    df = pd.read_csv(main_csv)

    df['LGBTQ+'] = df.apply(find_lgbtq, axis=1)

    df['Victim of Crime/Violence'] = df.apply(find_violence, axis=1)

    df['date'] = df.apply(find_date_of_intake, axis=1)

    #df[['DOB','Nationality']] = df['pdf_url'].swifter.apply(cal)            


    columns = ["Date", "Name", "Total Family Members", "Victim of Crime/Violence", "Explain Crime/Violence", "LGBTQ+", "Explain Health Problem", "Notes"]

    df.rename(columns={'Explique el crimen o violenica en Mexico ': 'Explain Crime/Violence', "date" : "Date", '# Family Members' : "Total Family Members", "Notas" : "Notes" , "Medical Condition and/or Vulnerability" : "Explain Health Problem" }, inplace=True) 
    df2 = pd.read_csv(supplemental_birthday_csv)
    df2["Date of Birth"] = df2["Birthday 1"].apply(assing_date_of_birth)
    out_df = pd.concat([df[columns].copy(), df2[["Birth Country","Date of Birth"]]], axis=1)

    def add_boolean_medical_column(medical_explanation):
        return medical_explanation is not nan
            
    out_df["Health Problem"] = out_df["Explain Health Problem"].apply(add_boolean_medical_column)

    return out_df
    
csv_1 = 'T42 Exemptions Post Consortium II.csv'
csv_2 = 'T42 Exceptions Birth-Nationality II.csv'
out_df1 = main(csv_1,csv_2)
out_df1.to_csv('CleanedT42File.csv',index=False)
exit()
csv_1 = 'T42 Exemptions Post Consortium 1.csv'
csv_2  = 'T42 Exceptions Birth-Nationality 1.csv'
out_df2 = main(csv_1,csv_2)

out_df = out_df1 + out_df2


out_df.to_csv('CleanedT42File.csv',index=False)