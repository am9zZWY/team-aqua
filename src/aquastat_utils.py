import math
import os
from pathlib import Path

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import geopandas as gpd

from tueplots.constants.color import rgb

from src.utils import get_dataframe, to_dat_path

PATH_TO_DAT = Path(__file__).parent / '..' / 'dat'
FILE_NAME = 'fao_aquastat.csv'
CSV_URL = 'https://yaon.org/data.csv'

AQUASTAT_COUNTRY_MAPPING = {
    'Bolivia (Plurinational State of)': 'Bolivia',
    'Brunei Darussalam': 'Brunei',
    'Congo': 'Republic of the Congo',
    "Côte d'Ivoire": 'Ivory Coast',
    "Democratic People's Republic of Korea": 'North Korea',
    'Dominica': 'Dominica',
    'Eswatini': 'Eswatini',
    'Faroe Islands': 'Faroe Islands',
    'Grenada': 'Grenada',
    'Holy See': 'Vatican City',
    'Iran (Islamic Republic of)': 'Iran',
    'Kiribati': 'Kiribati',
    "Lao People's Democratic Republic": 'Laos',
    'Liechtenstein': 'Liechtenstein',
    'Maldives': 'Maldives',
    'Malta': 'Malta',
    'Marshall Islands': 'Marshall Islands',
    'Mauritius': 'Mauritius',
    'Micronesia (Federated States of)': 'Micronesia',
    'Monaco': 'Monaco',
    'Nauru': 'Nauru',
    'Netherlands (Kingdom of the)': 'Netherlands',
    'Niue': 'Niue',
    'Palau': 'Palau',
    'Palestine': 'State of Palestine',
    'Puerto Rico': 'Puerto Rico',
    'Republic of Korea': 'South Korea',
    'Republic of Moldova': 'Moldova',
    'Russian Federation': 'Russia',
    'Saint Kitts and Nevis': 'Saint Kitts and Nevis',
    'Saint Lucia': 'Saint Lucia',
    'Saint Vincent and the Grenadines': 'Saint Vincent and the Grenadines',
    'Samoa': 'Samoa',
    'San Marino': 'San Marino',
    'Sao Tome and Principe': 'Sao Tome and Principe',
    'Serbia': 'Serbia',
    'Seychelles': 'Seychelles',
    'Singapore': 'Singapore',
    'Syrian Arab Republic': 'Syria',
    'Timor-Leste': 'East Timor',
    'Tokelau': 'Tokelau',
    'Tonga': 'Tonga',
    'Tuvalu': 'Tuvalu',
    'Türkiye': 'Turkey',
    'United Kingdom of Great Britain and Northern Ireland': 'United Kingdom',
    'Venezuela (Bolivarian Republic of)': 'Venezuela',
    'Viet Nam': 'Vietnam',
}

SOURCE_TEXT = 'Source: AQUASTAT'

def get_aquastat(raw=False) -> pd.DataFrame | None:
    file_path = os.path.join(PATH_TO_DAT, FILE_NAME)
    print(f'Getting AQUASTAT dataframe from {file_path} ...')

    # Download the data from https://yaon.org/data.csv
    import_df = get_dataframe(file_path=file_path, url=CSV_URL)
    if import_df is None:
        print('Could not get the AQUASTAT Dataframe!')
        return None

    # Format dataframe
    import_df.drop(columns=['Unnamed: 0'], inplace=True)

    # Return raw dataframe
    if raw:
        return import_df

    # Pivot table
    df = import_df.pivot_table(index=['Country', 'Year'], columns='Variable', values='Value', aggfunc='first')
    df.reset_index(inplace=True)

    return df


def rename_aquastat_country(country):
    global AQUASTAT_COUNTRY_MAPPING

    if country in AQUASTAT_COUNTRY_MAPPING:
        return AQUASTAT_COUNTRY_MAPPING[country]
    return country


def show_data(df, variables, include_countries=None):
    """
    Creates a plot showing whether data exists for variables in countries and years.
    If multiple variable names are given it looks if all are present for a year/country.

    :param df: Dataframe.
    :param variables: Variables to check for.
    :param include_countries: Optional. Filter for specific countries.
    """
    if include_countries is None:
        include_countries = []

    if isinstance(variables, str):
        variables = [variables]

    '''Extract relevant variables and drop all NaN'''
    data = df[['Country', 'Year', *variables]]
    if include_countries:
        data = data[data['Country'].isin(include_countries)]
    data = data.dropna()

    '''Create dataframe for heatmap'''
    years_data = data[['Country', 'Year']]
    years_df = years_data.pivot_table(index=['Country'], columns='Year', values='Year', aggfunc=lambda x: True,
                                      fill_value=False)
    years_df['True_Count'] = years_df.sum(axis=1)
    years_df = years_df.sort_values(by='True_Count', ascending=True)
    years_df.drop('True_Count', axis=1, inplace=True)

    df_numeric = years_df.replace({True: 1, False: 0})

    '''spaß mit colormap'''
    cmap_name = 'RdYlGn'
    cmap = matplotlib.colormaps[cmap_name]
    color_0 = cmap(0.0)
    color_1 = cmap(1.0)

    '''create heatmap'''
    plt.figure(figsize=(10, math.ceil(math.log(years_data['Country'].nunique(), 2)) * 5))
    ax = sns.heatmap(df_numeric,
                     annot=False,
                     cmap=cmap_name,
                     linewidths=0.5,
                     linecolor='gray',
                     cbar=False,
                     vmin=0,
                     vmax=1
                     )

    # Manuelle Legende
    blue_patch = mpatches.Patch(color=color_0, label='no data')
    red_patch = mpatches.Patch(color=color_1, label='data')
    plt.legend(handles=[blue_patch, red_patch], loc='upper left')

    plt.title('Presence of variables in year')
    plt.xlabel('year')
    plt.ylabel('country')

    plt.tight_layout()
    plt.show()


def plot_quality(aquastat_dataframe, variables, include_countries=None):
    """
    Plot a map to show the quality of the data for each country
    :param aquastat_dataframe: Dataframe.
    :param variables: Variables to check for.
    :param include_countries: Optional. Filter for specific countries.
    """
    if include_countries is None:
        include_countries = []

    if isinstance(variables, str):
        variables = [variables]

    '''Extract relevant variables and drop all NaN'''
    data = aquastat_dataframe[['Country', 'Year', *variables]]
    if include_countries:
        data = data[data['Country'].isin(include_countries)]
    data = data.dropna()

    '''Create dataframe for map'''
    countries_data = data[['Country', 'Year']]
    countries_df = countries_data.pivot_table(index=['Country'], columns='Year', values='Year', aggfunc=lambda x: True,
                                              fill_value=False)
    countries_df['True_Count'] = countries_df.sum(axis=1) / countries_df.shape[1]
    countries_df = countries_df.sort_values(by='True_Count', ascending=True)

    years_data = data[['Country', 'Year']]
    years_df = years_data.pivot_table(index=['Country'], columns='Year', values='Year', aggfunc=lambda x: True,
                                      fill_value=False)
    years_df['True_Count'] = years_df.sum(axis=1)
    years_df = years_df.sort_values(by='True_Count', ascending=True)
    years_df.drop('True_Count', axis=1, inplace=True)

    '''Rename some countries'''
    for country in countries_df['Country'].unique():
        replace_to = rename_aquastat_country(country)
        countries_df.replace(to_replace={country: replace_to}, inplace=True)

    '''Create map'''
    plt.figure(figsize=(10, math.ceil(math.log(years_data['Country'].nunique(), 2)) * 5))
    '''Plot using geopandas'''
    import geopandas as gpd

    world = gpd.read_file(os.path.relpath('../dat/naturalearth/ne_110m_admin_0_countries.shx'), engine="pyogrio")
    world = world.merge(countries_df, left_on='SOVEREIGNT', right_on='Country')
    world.plot(column='True_Count', cmap='RdYlGn', legend=True, figsize=(20, 20),
               legend_kwds={'label': "Data Quality", 'orientation': "horizontal", 'shrink': 0.5})

    plt.title('Presence of variables in year')

    plt.axis('on')
    plt.grid(which='major', axis='both', linestyle='-', color='lightgrey', alpha=0.5)

    plt.show()


def plot_world(aquastat_dataframe, variables, year, title=None, include_countries=None, cmap='RdYlGn'):
    """
    Plot a map to show the quality of the data for each country
    :param aquastat_dataframe: Dataframe.
    :param variables: Variables to check for.
    :param include_countries: Optional. Filter for specific countries.
    """
    if include_countries is None:
        include_countries = []

    if isinstance(variables, str):
        variables = [variables]

    if year is None:
        print('No year specified!')
        return None

    if title is None:
        title = 'World Map'

    # Extract relevant variables and drop all NaN
    data = aquastat_dataframe[['Country', 'Year', *variables]]
    data = data.dropna()

    # Filter for specific year
    countries_df = data[data['Year'] == year]

    # Aggregate data
    countries_df = countries_df[['Country', *variables]]

    # Rename countries to match the world map
    for country in countries_df['Country'].unique():
        replace_to = rename_aquastat_country(country)
        countries_df.replace(to_replace={country: replace_to}, inplace=True)

    # Merge data with world map
    world = gpd.read_file(to_dat_path(file_path='naturalearth/ne_110m_admin_0_countries.shx'), engine="pyogrio")
    world = world.merge(countries_df, left_on='SOVEREIGNT', right_on='Country')

    # Create figure
    plt.figure(figsize=(10, math.ceil(math.log(countries_df['Country'].nunique(), 2)) * 5))

    # Plot using geopandas
    world.plot(column=variables[0], vmin=0, vmax=40, legend=True, figsize=(20, 20), cmap=cmap,
               legend_kwds={'label': "Withdrawal (%) of total renewable water resources", 'orientation': "horizontal",
                            'shrink': 0.5})

    plt.title(title)

    # Add source
    plt.text(0.5, 0.05, SOURCE_TEXT, horizontalalignment='center', verticalalignment='center',
             transform=plt.gca().transAxes, color=rgb.tue_gray)

    plt.axis('on')
    plt.grid(which='major', axis='both', linestyle='-', color='lightgrey', alpha=0.5)

    return plt
