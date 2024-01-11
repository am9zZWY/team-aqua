import math
from pathlib import Path
from typing import TextIO

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import requests
import os.path

FIG_PATH = Path(__file__).parent / '..' / 'doc' / 'fig'
FIG_EXP_PATH = Path(__file__).parent / '..' / 'exp' / 'fig'
PATH_TO_DAT = Path(__file__).parent / '..' / 'dat'


def to_fig_path(experimental=True, file_path=None):
    fig_path = FIG_PATH
    if experimental:
        fig_path = FIG_EXP_PATH

    if file_path is not None:
        fig_path = os.path.join(fig_path, file_path)

    return fig_path


def to_dat_path(file_path=None):
    dat_path = PATH_TO_DAT

    if file_path is not None:
        dat_path = os.path.join(dat_path, file_path)

    return dat_path


def download_dataset(file_path=None, url=None) -> bool:
    """
    Downloads data from a URL and saves it to a file.

    :param file_path: the location to save the file in 'dat' folder. If None, the basename of the url is used
    :param url: the URL to download from
    :return: bool indicating success

    Example:
    >>> download_dataset(file_path='fao_aquastat.csv', url='https://yaon.org/data.csv')
    True

    The file will be saved as 'dat/fao_aquastat.csv'.
    """

    if url is None:
        print('No url specified!')
        return False

    if file_path is None:
        # If file_path is None, use the basename of the url
        file_path = os.path.join(PATH_TO_DAT, os.path.basename(url))
    else:
        # Extend file_path with PATH_TO_DAT
        file_path = os.path.join(PATH_TO_DAT, file_path)

    if os.path.isfile(file_path):
        print(f'{file_path} already exists.')
    else:
        print(f'{file_path} does not exist.')
        print(f'Downloading {file_path} ...')
        r = requests.get(url)
        with open(file_path, 'wb') as f:
            bytes_written = f.write(r.content)
            if bytes_written == 0:
                print(f'Error downloading {file_path}!')
                return False

    # If we get here, the file exists
    return True


def open_dataset(file_path=None, mode='r') -> TextIO | None:
    if file_path is None:
        print('No file name specified!')
        return None

    # Extend file_path with PATH_TO_DAT
    file_path = os.path.join(PATH_TO_DAT, file_path)

    if not os.path.isfile(file_path):
        print(f'{file_path} does not exist.')
        return None

    return open(file_path, mode=mode)


def get_dataframe(file_path=None, url=None) -> pd.DataFrame | None:
    """
    Downloads data from a url and saves it to a file.
    If the file does not exist, it will be downloaded from the url.

    Creates a pandas dataframe from the csv file and returns it

    :param file_path: the location where the file is opened from
    :param url: the URL to download from
    :return: pandas dataframe or None if the file could not be downloaded
    """

    if file_path is None and url is None:
        print('No file name and url specified!')
        return None

    if file_path is None:
        # If file_path is None, use the basename of the url
        file_path = os.path.join(PATH_TO_DAT, os.path.basename(url))
    else:
        # Extend file_path with PATH_TO_DAT
        file_path = os.path.join(PATH_TO_DAT, file_path)

    if url is not None:
        if not download_dataset(file_path=file_path, url=url):
            print(f'Cannot create dataframe from {file_path}!')
            return None

    import_df = pd.read_csv(file_path)
    return import_df


def save_fig(fig, fig_name=None, fig_path=None, experimental=True) -> str | bool:
    """
    Saves a figure to a file.

    :param experimental: if True, the figure will be saved to 'exp/fig'. Otherwise, it will be saved to 'fig'.
    :param fig: the figure to save
    :param fig_name: the name of the figure
    :param fig_path: the location to save the figure to. IMPORTANT! You don't need to specify 'out' folder.
    :return: bool indicating success or the path to the saved figure

    Example:
    >>> save_fig(fig, fig_name='my_fig', fig_path='cool_figure')
    ./exp/fig/cool_figure/fig_my_fig.pdf

    The file will be saved as 'fig/out/cool_figure/fig_my_fig.pdf'.

    >>> save_fig(fig, fig_name='my_fig', fig_path='cool_figure', experimental=False)
    ./fig/cool_figure/fig_my_fig.pdf
    """

    if fig is None:
        print('No figure specified! That\'s not good. You are not good. Go home.')
        return False

    def random_fig_name():
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    # If fig_name is None, create a random name
    if fig_name is None:
        fig_name = random_fig_name()

    # If fig_name does not begin with 'fig_', add it
    if not fig_name.startswith('fig_'):
        fig_name = f'fig_{fig_name}'

    # If fig_name ends with '.pdf', remove it
    if fig_name.endswith('.pdf'):
        fig_name = fig_name[:-4]

    # Start with 'exp/fig' or 'fig'
    _internal_fig_path = FIG_PATH
    if experimental:
        _internal_fig_path = FIG_EXP_PATH

    # If fig_path is not None, add it
    if fig_path is not None:
        _internal_fig_path = os.path.join(_internal_fig_path, fig_path)

    # If fig_path does not exist, create it
    if not os.path.isdir(_internal_fig_path):
        print(f'{_internal_fig_path} does not exist.')
        print(f'Creating {_internal_fig_path} ...')
        os.makedirs(_internal_fig_path, exist_ok=True)

    # Add file name
    _internal_fig_path = os.path.join(_internal_fig_path, f'{fig_name}.pdf')

    # Save figure
    _print_fig_path = os.path.relpath(_internal_fig_path)
    print(f'Saving figure to {_print_fig_path} ...', end=' ')
    fig.savefig(_internal_fig_path, dpi=300, bbox_inches='tight')
    print('Done!')

    return _internal_fig_path


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


def quality_map(df, variables, include_countries=None):
    '''Plot a map to show the quality of the data for each country'''
    if include_countries is None:
        include_countries = []

    if isinstance(variables, str):
        variables = [variables]

    '''Extract relevant variables and drop all NaN'''
    data = df[['Country', 'Year', *variables]]
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
    rename_to_dict = {
        'Russian Federation': 'Russia',
        'Bolivia (Plurinational State of)': 'Bolivia'
        # TODO
    }
    for key, value in rename_to_dict.items():
        countries_df.rename(index={key: value}, inplace=True)

    '''Create map'''
    plt.figure(figsize=(10, math.ceil(math.log(years_data['Country'].nunique(), 2)) * 5))
    '''Plot using geopandas'''
    import geopandas as gpd

    world = gpd.read_file(os.path.relpath('../dat/naturalearth/ne_110m_admin_0_countries.shx'), engine="pyogrio")
    world = world.merge(countries_df, left_on='SOVEREIGNT', right_on='Country')
    world.plot(column='True_Count', cmap='RdYlGn', legend=True, figsize=(20, 20),
               legend_kwds={'label': "Data Quality", 'orientation': "horizontal", 'shrink': 0.5})

    plt.title('Presence of variables in year')

    '''Remove axis'''
    plt.axis('off')

    plt.show()