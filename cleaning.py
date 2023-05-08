import pandas as pd
import os
import numpy as np
import random
import matplotlib.pyplot as plt

def replace_nulls(filename):
    """
    Replaces null values in a CSV file with 0 and changes the dtype of the column to int.

    Parameters
    ----------
    filename : str
        The file path of the CSV file to be cleaned.

    Returns
    -------
    None
        This function does not return a value, but saves the cleaned data to a new CSV file in the
        "cleaned_data/puntos_por_anho/" directory with the same filename as the original file.
    """

    df = pd.read_csv(f"puntos_por_anho/{filename}")
    df.fillna(0, inplace = True)
    columns = df.columns
    for column in columns:
        if "Country" in column or "Contestants" in column:
            pass
        else:
            df[column] = df[column].astype(int)
    df.to_csv(f"cleaned_data/puntos_por_anho/{filename}")


def rename_cols(filename):
    """
    Rename columns to remove Wikipedia notations.

    Parameters
    ----------
    filename : str
        The file path to the CSV file to be cleaned.

    Returns
    -------
    None
        The function overwrites the input file with the cleaned version.
    """

    df = pd.read_csv(f"canciones_por_anho/{filename}")
    columns = df.columns
    new_columns = []
    for col in columns:
        if "[" in col:
            new_col = col.split("[")[0]
        else:
            new_col = col
        new_columns.append(new_col)
    df.rename(columns = dict(zip(columns, new_columns)), inplace = True)
    df.to_csv(f"cleaned_data/canciones_por_anho/{filename}")

def change_dtype(df):
    """
    Change the types of columns in a Pandas DataFrame to suitable ones.

    Parameters
    ----------
    df : pd.DataFrame
        A Pandas DataFrame whose columns need to be changed.

    Returns
    -------
    pd.DataFrame
        The Pandas DataFrame with columns having updated data types.
    """
    cols = df.columns
    for col in cols:
        if df[col].dtype == "float64":
            df[col] = df[col].apply(lambda x: int(round(x))).astype("int64")
        elif col in ["BPM","energy","danceability","happiness","liveness","speechiness"]:
            df[col] = df[col].astype("int64")

def convert_loudness(loudness):
    """
    Convert loudness to a consistent format.

    Parameters:
    -----------
    loudness : pd.Series
        The loudness values to be converted.

    Returns:
    --------
    pd.Series
        The converted loudness values.

    Description:
    ------------
    This function takes a pandas Series containing loudness values in different formats and
    converts them to a consistent format. It removes any dB notation and makes all values
    negative. Finally, it rounds the values to the nearest integer.

    Examples:
    ---------
    >>> import pandas as pd
    >>> loudness = pd.Series(['-11 dB', '0 dB', '4.5', 6])
    >>> convert_loudness(loudness)
    0   -11.0
    1     0.0
    2    -4.0
    3    -6.0
    dtype: float64
    """
    loudness = pd.to_numeric(loudness.apply(lambda x: x.split(" ")[0] if type(x) == str else x))
    loudness = np.where(loudness > 0, loudness * -1, loudness)
    loudness = loudness.round()
    return loudness

def plot_bars(col, df):
    """
    Plot a bar chart for the given column in the given DataFrame.

    Parameters
    ----------
    col : str
        Name of the column in the DataFrame to plot.
    df : pd.DataFrame
        DataFrame containing the data to plot.

    Returns
    -------
    None
    """
    colours = [
    'cornflowerblue', # Azul claro
    'mediumaquamarine', # Verde agua
    'lightcoral', # Coral claro
    'paleturquoise', # Turquesa claro
    'lemonchiffon', # Amarillo claro
    'lavender', # Lavanda
    'rosybrown', # Marrón rosado
    'palegoldenrod', # Beige dorado claro
    'lightsteelblue', # Azul acero claro
    'thistle' # Cardo
    ]

    x = df[col].value_counts().keys()
    x = [str(i) for i in x]
    y = df[col].value_counts().values
    plt.bar(x,y, color = random.choice(colours))
    plt.title(col)
    plt.ylabel("count")
    plt.show()


def clean_all_data():
    """
    Cleans up the Eurovision Song Contest data stored in various files and 
    stores the cleaned data in a new file in the 'cleaned_data' directory.

    The function replaces null values with 0 and changes the dtype of the columns
    in the csv files in the 'puntos_por_anho' and 'canciones_por_anho' directories.
    It also changes column names and removes Wikipedia notations in the csv files
    in the 'canciones_por_anho' directory.

    The 'song_data_completo.xlsx' file is cleaned by replacing "-" with 0 in certain columns
    and dropping redundant and non-informative columns.

    The cleaned 'songs_df' DataFrame is stored in a new file in the 'cleaned_data' directory
    named 'songs_cleaned.csv'.

    It plots and then drops redundant and non informative columns:
        direct_qualifier_10
        age
        selection
        key - only the nulls
        instrumentalness
        release_date
        key_change_10
        qualified
        final_jury_votes
        final_televote_votes
        final_total_points
        semi_total_points
        race
    It then stores the cleaned file in the path
        /cleaned_data/songs_cleaned.csv
    
    Returns:
        None
    """
    # Cleaning data in /canciones_por_anho and /puntos_por_anho

    puntos_por_anho_dir = os.listdir("puntos_por_anho")
    for file in puntos_por_anho_dir[:len(puntos_por_anho_dir)-12]:
        replace_nulls(file)

    canc_por_anho_dir = os.listdir("canciones_por_anho")
    for file in canc_por_anho_dir:
        rename_cols(file)

    # Cleaning songs_df

    songs_df = pd.read_excel("song_data_completo.xlsx")
    songs_df.drop(528, axis = 0, inplace = True) # null values in row 528

    # Replacing "-" with 0

    songs_df['semi_draw_position'].replace("-", 0, inplace = True)
    songs_df['final_draw_position'].replace("-", 0, inplace = True)
    songs_df['final_televote_points'].replace("-", 0, inplace = True)
    songs_df['loudness'].fillna("-3", inplace = True) # replacing 1 null value with -3. We looked up the song info online
    songs_df['final_jury_points'].replace("-", 0, inplace = True)
    songs_df['final_place'].replace("-", 0, inplace = True)

    # Dropping redundant and non informative columns

    to_drop = ['direct_qualifier_10', "selection", "instrumentalness",
        "release_date", "key_change_10", "qualified", 'final_jury_votes', 
        'final_televote_votes', 'final_total_points', 'semi_total_points', 
        'race', "age"]
    
    for col in to_drop:
        plot_bars(col, songs_df)

    songs_df.drop(to_drop, axis = 1, inplace = True)
    songs_df.drop(songs_df[songs_df['key'] == "-"].index, axis=0, inplace= True)
    songs_df.drop(474,axis = 0, inplace = True) # dropping 1 null value that's in this column

    songs_df['loudness'] = convert_loudness(songs_df['loudness'])
    change_dtype(songs_df)

    songs_df.to_csv("cleaned_data/songs_cleaned.csv",index = False)

    print("Data cleaned and stored in /cleaned_data")