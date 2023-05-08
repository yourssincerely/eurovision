import pandas as pd
import numpy as np
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import warnings
warnings.filterwarnings("ignore")


def fix_colnames(filename:str, path:str):
    """
    Clean the column names of a CSV file located at the specified path by removing any characters within square brackets and parentheses
    and renaming specific columns to more appropriate names. The cleaned CSV file is saved at the same location.

    Parameters:
    - filename: str - The name of the CSV file to be cleaned.
    - path: str - The path to the folder where the CSV file is located.

    Returns:
    - None - The function does not return any value.

    Example usage:
    ```
    fix_colnames("my_file.csv", "/path/to/my/folder")
    ```
    """
    df = pd.read_csv(path + "/" + filename)
    change_dict = {}
    colnames = df.columns
    for col in colnames:
        new_col = col.split("[")[0]
        new_col = new_col.split("(")[0]
        if new_col == "Final result":
            new_col = "Place"
        elif new_col == "Performer":
            new_col = "Artist"
        change_dict[col] = new_col
        df.rename(columns = change_dict, inplace = True)
        df.to_csv(path + "/" +filename, index = False)


def create_id(df,name = "id"):
    """
    Create a unique identifier for each row in the input DataFrame by concatenating the first 4 characters of the "year" column
    and the first 6 characters of the "country" column. The resulting IDs are inserted as a new column at the beginning of the
    DataFrame.

    Parameters:
    - df: pd.DataFrame - The input DataFrame to which the IDs will be added.
    - name: str - The name of the column to be created for the IDs. Defaults to "id".

    Returns:
    - pd.DataFrame - The input DataFrame with the new column of unique IDs.

    Example usage:
    ```
    my_df_with_ids = create_id(my_df, "unique_id")
    ```
    """
    canciones_id = []
    for i in df.iterrows():
        year = str(i[1]["year"])[:4]
        country = i[1]["country"][ :6]
        canciones_id.append(country + year)
    df.insert(0,name,canciones_id)
    return df

def concat_dataframes(lista_archivos:list, path:str):
    """
    Concatenates a list of CSV files located in a specified path into a single pandas DataFrame.

    Parameters:
    - lista_archivos: list - A list of CSV file names to be concatenated.
    - path: str - The path to the folder containing the CSV files.

    Returns:
    - pd.DataFrame - A concatenated pandas DataFrame.

    Example usage:
    ```
    my_df = concat_dataframes(["file1.csv", "file2.csv"], "/path/to/folder")
    ```
    """
    df = pd.DataFrame()
    for file in lista_archivos:
        prov_df = pd.read_csv(path + "/" + file)
        df = pd.concat([df, prov_df], axis = 0)
    return df

def to_int(df):
    """
    Transform float columns to integers.

    Args:
    - df: pd.DataFrame - DataFrame to be transformed.

    Returns:
    - pd.DataFrame - The transformed DataFrame with float columns cast as integers.
    """
    for col in df.columns:
        if df[col].dtype == float:
            df[col] = df[col].astype(int)
    return df


# Directory from which we're gonna access the song files
canciones_dir = os.listdir("cleaned_data/canciones_por_anho")

# Fixing column names
for file in canciones_dir:
    fix_colnames(file,"cleaned_data/canciones_por_anho")

# Merging the data frames together
canciones = pd.concat([pd.read_csv(f"cleaned_data/canciones_por_anho/{file}") for file in canciones_dir], axis = 0)

# Dropping unwanted columns
canciones.drop(["Unnamed: 0", "Points"],axis = 1, inplace = True)

# Splitting the dataset
canciones_08 = canciones[canciones["Year"] < 2009]
canciones_09 = pd.read_csv("cleaned_data/songs_cleaned.csv")
canciones_09["key"] = canciones_09["key"].apply(lambda x: x.lower())
canciones_09 = canciones_09[canciones_09["final_draw_position"]!= 0]

# Renaming the columns to match the other files 
dict_columns= {
    'Country': 'country', 
    'Artist': 'artist_name', 
    'Song': 'song_name', 
    'Language': 'language', 
    'Place': 'final_place', 
    'Order': 'final_draw_position', 
    'Year': 'year'}

canciones_08 = canciones_08.rename(columns=dict_columns)
canciones = pd.concat([canciones_08,canciones_09], axis = 0)

# Dropping more columns
canciones.drop(["semi_draw_position", 
    "semi_place",
    "final_televote_points",
    "final_jury_points"], 
    axis = 1, inplace = True )
canciones["country"].replace(" Yugoslavia","Yugoslavia", inplace = True)

# Creating ID to get data ready to upload to the mySQL database
create_id(canciones)

# Filtering out the dataset
canciones_overview = canciones[
    ["id" ,"country", "artist_name", "song_name", 
     "language", "final_place", "final_draw_position","year"]]
# Dropping more unwanted columns
canciones_features = canciones.drop(
    ["artist_name", "song_name", "language", 
     "final_place", "final_draw_position"], 
     axis = 1)

# Splitting datasets according to the additional information that we have from 2009 onwards
canciones_features = canciones_features[canciones_features["year"]>2008]

# Filtering out null values
canciones_overview = canciones_overview[canciones_overview["language"].isna() == False]

# Correcting values in languages
corrected_lang = []
for lang in canciones_overview["language"]:
    if "[" in lang:
        corr_lang = lang.split("[")[0]
        corrected_lang.append(corr_lang)
    else:
        corrected_lang.append(lang)
canciones_overview["language"] = corrected_lang

# Creating dataset for the points and countries
puntos_dir = os.listdir("cleaned_data/puntos_por_anho")
puntos_por_anho_2015 = concat_dataframes(puntos_dir[:len(puntos_dir)-12], "cleaned_data/puntos_por_anho")

# Dropping unwanted columns
puntos_por_anho_2015.drop(["Unnamed: 0","Total score"], axis = 1, inplace = True)
puntos_por_anho_2015 = puntos_por_anho_2015.rename(
    columns = 
    {"Year" : "year",
    "Country": "country"})

# Adding data from 2016 onwards since it's split in two different
jury_2016 = [file for file in puntos_dir if "juryvote" in file]
jury_df = concat_dataframes(jury_2016, "cleaned_data/puntos_por_anho")
jury_df.drop(["Total score", "Televoting score", "Jury vote"], axis = 1, inplace = True)

tele_vote_2016 = [file for file in puntos_dir if "televote" in file]
tele_df = concat_dataframes(tele_vote_2016, "cleaned_data/puntos_por_anho")
tele_df.drop(["Total score", "Jury score"], axis = 1, inplace = True)

# Merging the two datasets
puntos_por_anho_2016 = jury_df + tele_df
puntos_por_anho_2016.drop(["Jury score","Televoting score","Unnamed: 0"], axis = 1, inplace = True)

# After adding up the two datasets, string columns need to be split in half
puntos_por_anho_2016['Contestants']= puntos_por_anho_2016['Contestants'].apply(lambda x:x[:len(x)//2])
puntos_por_anho_2016['Year'] = puntos_por_anho_2016['Year'].apply(lambda x:x/2).astype(int)
# Changing column names to match the other datasets
col_dict = {"Year": "year","Contestants": "country"}
puntos_por_anho_2016.rename(columns= col_dict, inplace = True)

# Merging the two datasets
puntos_por_anho = pd.concat([puntos_por_anho_2015,puntos_por_anho_2016], axis = 0)
# Filling NAs with 0
puntos_por_anho.fillna(0, inplace = True)
# Creating ID to get the dataset ready to upload to SQL
create_id(puntos_por_anho, name = "_id")

# Grouping languages
a = [i for i in canciones_overview["language"].value_counts().keys() if "," in i]
b = [sorted(i.split(", ")) for i in a]
b = [", ".join(i) for i in b]
replaceable = dict(zip(a, b))
for key, value in replaceable.items():
    replaceable[key] = value.replace("\xa0", " ")
canciones_overview["language"].replace(replaceable, inplace = True)

# Changing column dtypes from float to int after replacing nulls
to_int(canciones_overview)
to_int(canciones_features)
puntos_por_anho.drop(["country","year"], axis = 1, inplace = True)
to_int(puntos_por_anho)
canciones_2023 = pd.read_csv("cleaned_data/clean_2023.csv")