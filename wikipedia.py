from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pandas as pd
from more_itertools import chunked
import os

years = list(range(1957, 2023))
base_url = "https://en.wikipedia.org/wiki/Eurovision_Song_Contest_"
basic_headers = {"user-agent" : "Mozilla/5.0"}

def get_table_points_year(years = years, 
                          base_url = base_url, 
                          basic_headers = basic_headers):
    
    """
    Retrieves the Wikipedia table information of the votes casted by all the participants of that year's festival
    for a list of years.

    Args:
        - years: List of integers representing the years of the festival to retrieve data for.
        - base_url: Base URL to retrieve the Wikipedia page from.
        - basic_headers: A dictionary with the headers to use when sending the request.

    Returns:
        A dictionary with the years as keys and a BeautifulSoup object containing the Wikipedia table information
        of the votes casted by all the participants of that year's festival.
    """
    
    diccionario = {}
    
    for year in years:
        url = base_url + str(year)
        
        try:
            req = Request(url, headers = basic_headers)
            raw_web = urlopen(req, timeout = 10).read()
            soup = BeautifulSoup(raw_web, "html.parser")
            tables = soup.find_all("table", attrs = {
                "class" : "wikitable plainrowheaders"})

            for table in tables:
                if "Detailed voting results of the final" in str(table):
                    target_table = table
                    break
                elif "Final voting results" in str(table):
                    target_table = table
                    break
                elif "Detailed voting results" in str(table) and "semi" not in str(table) and "qualifying" not in str(table):
                    target_table = table
                    break
                else:
                    pass

            diccionario[year] = table  
            
        except:
            pass
        
    return diccionario

def bs4_to_pandas_votes(bs4_object):
    """
    bs4_object : bs4 object
    return : pd.DataFrame

    It takes a bs4 object and returns a pandas dataframe.
    """
    headers = bs4_object.find_all('th', attrs = {"scope" : "col"})
    cabecera=[i.text.strip("\n") for i in headers]
    paises_b = bs4_object.find_all('th', attrs = {"scope" : "row"})
    paises = [i.text.strip("\n") for i in paises_b]
    row = bs4_object.find_all('td')
    try:
        filas = [i.text.strip("\n").strip("\xa0") for i in row]
        divisor = len(cabecera)
        resultado = list(chunked(filas,divisor))
        df = pd.DataFrame(resultado,columns = cabecera)
        df["Country"] = paises
        
    except:
        filas = [i.text.strip("\n").strip("\xa0") for i in row if 'style="background:' not in str(i)][1:]
        divisor = len(cabecera)
        resultado = list(chunked(filas,divisor))
        df = pd.DataFrame(resultado,columns = cabecera)
        df["Country"] = paises

    return df

def get_table_songs_year(years = years, 
                         base_url = base_url, 
                         basic_headers = basic_headers):
    
    """
    Args:
    - bs4_object: BeautifulSoup object - The bs4 object to be transformed.

    Returns:
    - pd.DataFrame - The transformed DataFrame containing table information of the votes casted
    by all the participants of that year's festival.
    """
    
    anhos_y_canciones = {}

    for year in years:
        url = base_url + str(year)
        req = Request(url, headers = basic_headers)
        raw_web = urlopen(req, timeout = 10).read()
        soup = BeautifulSoup(raw_web, "html.parser")
        
        if year in [2002,2003,2007]:
            pass
        else:
            
            if year ==  2021:
                tables = soup.find_all("table", attrs = {
                "class" : "wikitable sortable plainrowheaders"})
            else:
                tables = soup.find_all("table", attrs = {
                "class" : "sortable wikitable plainrowheaders"})

            if year < 1997:
                target_table = tables[0]
            elif year < 2007:
                target_table = tables[1]
            elif year < 2014:
                target_table = tables[2]
            elif year < 2016:
                target_table = tables[3]
            elif year < 2019:
                target_table = tables[2]
            elif year == 2019:
                target_table = tables[0]
            elif year == 2020:
                target_table = None
            elif year == 2021:
                target_table = tables[0]
            elif year == 2022:
                target_table = tables[2]

            anhos_y_canciones[year] = target_table
        
    return anhos_y_canciones

def bs4_to_pandas_songs(bs4_object):
    """
    Converts a BeautifulSoup object representing a Eurovision song table to a pandas DataFrame.

    Args:
    - bs4_object: BeautifulSoup - The BeautifulSoup object representing a Eurovision song table.

    Returns:
    - pd.DataFrame - The pandas DataFrame containing the song information, with the following columns:
        - Artist: str - The name of the artist who performed the song.
        - Song: str - The name of the song.
        - Language: str - The language(s) the song was performed in.
        - Points: int - The number of points the song received in the competition.
        - Order: int - The order in which the song was performed during the competition.
    """
    headers = bs4_object.find_all('th', attrs = {"scope" : "col"})
    cabecera=[i.text.strip("\n") for i in headers][1:]
    row = bs4_object.find_all('td')
    filas = [i.text.strip("\n").strip("\xa0") for i in row]
    divisor = len(cabecera)
    resultado = list(chunked(filas,divisor))
    casi_df = pd.DataFrame(resultado,columns = cabecera)
    casi_df["Order"] = list(range(1,len(resultado) + 1))
    return casi_df   


for csv in os.listdir("2016_2022"):
    df= pd.read_csv(f'2016_2022/{csv}')
    year= csv.split('_')[1][:4]
    df["Year"]= year
    df.to_csv(f'puntos_por_anho/{csv}', sep=',', encoding='utf-8', index=False)

def get_wikipedia_data():
    """
    This function stores csv files from wikipedia eurovision information in the paths:
        /puntos_por_anho/filename.csv
        /canciones_por_anho/filename.csv
    """

    print("Getting points per year from Wikipedia...")

    puntos_por_anho = get_table_points_year(years= list(range(1957,2016)))

    for k,v in puntos_por_anho.items():
        df= bs4_to_pandas_votes(v)
        df["Year"] = k
        df.to_csv(f'puntos_por_anho/{k}.csv', sep=',', encoding='utf-8', index=False)

    print("Tables puntos_por_anho created!")
    print("Getting songs per year from Wikipedia...")

    anhos_y_canciones = get_table_songs_year()

    for k,v in anhos_y_canciones.items():
        try:
            df= bs4_to_pandas_songs(v)
            df["Year"] = k
            df.to_csv(f'canciones_por_anho/{k}.csv', sep=',', encoding='utf-8', index=False)
        except:
            pass

    print("Tables anhos_y_canciones created!")
