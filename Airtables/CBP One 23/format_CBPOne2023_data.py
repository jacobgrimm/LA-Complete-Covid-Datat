import pandas as pd

df = pd.read_excel("CONFIDENTIAL_ ATTORNEY -CLIENT Privilege Document_CBP ONE 2023.xlsx")

df = df.dropna(subset=['Nombres y Apellidos']) #drop all rows that don't have a name/last name for client

#fill rows that don't have a NA value with a 0, so that we can do proper summation of the rows
selected_columns= ['Número de Mujeres que viajan (incluyendo al titular)', 'Número de Hombres que viajan   (incluyendo al titular)', 'Número de menores que viajan', "Telefono ", "Notas del app ", "Email Address"]
df[selected_columns] = df[selected_columns].fillna(0)
df['Total Family Members'] = df['Número de Mujeres que viajan (incluyendo al titular)'] + df['Número de Hombres que viajan   (incluyendo al titular)'] + df['Número de menores que viajan']

#rename rows to same names as the other LAMX front desk data from 2021-2022
df = df.rename(columns={'Nombres y Apellidos': 'Name', ' ': 'Date', 'Nacionalidad' : 'Country of Origin', "Fecha nacimiento\nMM DD AA" : "Date of Birth", "Notas generales del caso" : "Notes"})
df = df.drop(columns=selected_columns)


def search_for_keywords(row, keyword_list):              
    if  not pd.isna(row["Notes"]):
        for word in keyword_list:
                if word in row["Notes"].lower():
                    return "Si"       
    return "Unknown"

    

def find_lgbtq(row):
    word_list = ["lgbt", "lgbt+", "gay", "lesbian", "homosexual", "trans", "bisexual"]
    return search_for_keywords(row, keyword_list=word_list)


def find_threat(row):
    word_list = ['threat', 'amenaz', 'muer', 'secuestr', 'kidnap','tortur',"viola","rape","abuso", "gbv"]
    return search_for_keywords(row, word_list)

df["Victim of Crime/Violence"] =df.apply(find_threat, axis=1)
df["LGBTQ+"] = df.apply(find_lgbtq, axis=1)
df['Date'] = pd.to_datetime(df['Date'])

df['Country of Origin'] = df['Country of Origin'].str.strip()


df.to_csv("Cleaned Privilege Document CBP ONE 2023.csv", index=False)
