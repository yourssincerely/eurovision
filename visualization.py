import random
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

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
    'thistle', # Cardo
    'chartreuse', # Es un verde
    'mediumspringgreen', # Es otro verde
    'moccasin', # nes saltarines con la piel de dos mastines
    'cornflowerblue', # Es un azul
    'darkorchid', # Lila
    'fuchsia', # Fuchsia
    'peachpuff' # Melocoton
    ]

songs_df = pd.read_csv("cleaned_data/songs_cleaned.csv")

def plot_data(df = songs_df, colours = colours):
    """
    Plot a bar chart for every categorical value and a histogram for continuous values.

    Args:
        df: Pandas DataFrame. Defaults to songs_df (pd.read_excel("song_data_completo.xlsx")).
        colours: List of str. Defaults to colours (colours).

    Returns:
        None
    """
    songs_df["year"] = songs_df["year"].astype("category")
    for col in songs_df.columns:
        if songs_df[col].dtype == "object":
            songs_df[col] = songs_df[col].astype("category")
    cols = df.columns
    for col in cols:
        color = random.choice(colours)
        if col in ["backing_dancers", "backing_singers", "backing_instruments", 
                   "instrument_10", "main_singers", "favourite_10", "host_10",
                  "semi_draw_position", "final_draw_position"]:
            x = df[col].value_counts().keys()
            X = [str(i) for i in x]
            y = df[col].value_counts().values
            plt.figure(figsize=(8, 6))
            plt.bar(X,y, color = color)
            plt.title(col, fontsize = 16)
            plt.xticks(rotation = 90)
            plt.ylabel("count")
            plt.show()
        elif df[col].dtype == "int64":
            plt.figure(figsize=(8, 6))
            plt.hist(df[col], color = color)
            plt.title(col, fontsize = 16)
            plt.xticks(rotation = 90)
            plt.ylabel("count")
            plt.show()
        else:            
            x = df[col].value_counts().keys()
            X = [str(i) for i in x]
            y = df[col].value_counts().values
            plt.figure(figsize=(8, 6))
            plt.bar(X,y, color = color)
            plt.title(col, fontsize = 16)
            plt.xticks(rotation = 90)
            plt.ylabel("count")
            plt.show()

def plot_cats(df, cols, colours = colours):
    """
    Plot bar charts for each categorical variable in the specified dataframe.

    Args:
        df: A pandas dataframe.
        cols: A list of strings representing the categorical variable columns to plot.
        colours: A list of strings representing the colors to use for each bar chart.

    Returns:
        None
    """

    for col in cols:
        
        values = df[col].value_counts()
        colour = random.choice(colours)
        params = {'xtick.labelsize': 9, 'ytick.labelsize': 10}
        mpl.rcParams.update(params)
        plt.bar(
            x = values.keys(), 
            height = values.values,
            color = colour
            )
        plt.xticks(rotation = 90)
        plt.title(col)
        plt.show()
