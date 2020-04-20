import datetime
import os

import numpy as np
import pandas as pd

import urllib, json

_format_date = lambda date_py: "{}/{}/{}".format(
    date_py.month, date_py.day, str(date_py.year)[2:4]
)

class JHU():
    """
    Contains all functions for downloading, filtering and manipulating data from the Johns Hopkins University.
    https://coronavirus.jhu.edu/

    Features:
        - download all files from the online repository of the coronavirus visual dashboard operated by the Johns Hopkins University.
        - filter by deaths, confirmed cases and recovered cases
        - filter by country and state
        - filter by date

    Parameters
    ----------
    auto_download : bool, optional
        whether or not to automatically download the data from jhu (default: false)

    """
    def __init__(self, auto_download = False):
        self.confirmed : pd.DataFrame
        self.deaths : pd.DataFrame
        self.recovered : pd.DataFrame

        if auto_download:
            self.download_all_available_data()

    def download_all_available_data(self,
        fp_confirmed:str='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv',
        fp_deaths:str='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv',
        fp_recovered:str='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv',
        save_to_attributes:bool=True)-> (pd.DataFrame,pd.DataFrame,pd.DataFrame):
        """
        Attempts to download the most current data for the confirmed cases, deaths and recovered cases from the online repository of the
        Coronavirus Visual Dashboard operated by the Johns Hopkins University
        (and falls back to the backup provided with our repo if it fails TODO).
        Only works if the module is located in the repo directory.

        Parameters
        ----------
        fp_confirmed,fp_deaths,fp_recovered : str, optional
            Filepath or URL pointing to the original CSV of global confirmed cases, deaths or recovered cases
        save_to_attributes : bool, optional
            Should the returned dataframe tuple be saved as attributes (default:true)

        Returns
        -------
        : pandas.DataFrame tuple
            tuple of table with confirmed, deaths and recovered cases
        """

        return self.download_confirmed(fp_confirmed, save_to_attributes), self.download_deaths(fp_deaths, save_to_attributes), self.download_recovered(fp_recovered, save_to_attributes)

    def download_confirmed(self,
        fp_confirmed:str='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv',
        save_to_attribues:bool=True
        ):
        """
        Attempts to download the most current data for the confirmed cases from the online repository of the
        Coronavirus Visual Dashboard operated by the Johns Hopkins University
        (and falls back to the backup provided with our repo if it fails TODO).
        Only works if the module is located in the repo directory.

        Parameters
        ----------
        fp_confirmed : str, optional
            Filepath or URL pointing to the original CSV of global confirmed cases, deaths or recovered cases
        save_to_attributes : bool, optional
            Should the returned dataframe tuple be saved as attributes (default:true)

        Returns
        -------
        : pandas.DataFrame
            Table with confirmed cases, indexed by date
        """
        confirmed = self.__to_iso(self.__download_from_source(fp_confirmed))
        if save_to_attribues:
            self.confirmed = confirmed
        return confirmed

    def download_deaths(self,
        fp_deaths:str='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv',
        save_to_attribues:bool=True
        ):
        """
        Attempts to download the most current data for the deaths from the online repository of the
        Coronavirus Visual Dashboard operated by the Johns Hopkins University
        (and falls back to the backup provided with our repo if it fails TODO).
        Only works if the module is located in the repo directory.

        Parameters
        ----------
        fp_deaths : str, optional
            filepath or URL pointing to the original CSV of global confirmed cases, deaths or recovered cases
        save_to_attributes : bool, optional
            Should the returned dataframe tuple be saved as attributes (default:true)

        Returns
        -------
        : pandas.DataFrame
            Table with deaths, indexed by date
        """
        deaths = self.__to_iso(self.__download_from_source(fp_deaths))
        if save_to_attribues:
            self.deaths = deaths
        return deaths

    def download_recovered(self,
        fp_recovered:str='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv',
        save_to_attribues:bool=True
        ):
        """
        Attempts to download the most current data for the recovered cases from the online repository of the
        Coronavirus Visual Dashboard operated by the Johns Hopkins University
        (and falls back to the backup provided with our repo if it fails TODO).
        Only works if the module is located in the repo directory.

        Parameters
        ----------
        fp_recovered : str, optional
            Filepath or URL pointing to the original CSV of global confirmed cases, deaths or recovered cases
        save_to_attributes : bool, optional
            Should the returned dataframe tuple be saved as attributes (default:true)

        Returns
        -------
        : pandas.DataFrame
            Table with recovered cases, indexed by date
        """
        recovered = self.__to_iso(self.__download_from_source(fp_recovered))
        if save_to_attribues:
            self.recovered = recovered
        return recovered

    def __download_from_source(self, url, fallback = None)-> pd.DataFrame:
        """
        Private method
        Downloads one csv file from an url and converts it into a pandas dataframe. A fallback source can also be given.

        Parameters
        ----------
        url : str
            Where to download the csv file from
        fallback : str, optional
            Fallback source for the csv file, filename of file that is located in /data/

        Returns
        -------
        : pandas.DataFrame
            Raw data from the source url as dataframe
        """
        try:
            data = pd.read_csv(url, sep=",")
        except Exception as e:
            print("Failed to download current data 'confirmed cases', using local copy.")
            this_dir = os.path.dirname(__file__)
            data = pd.read_csv(
                this_dir + "/../data/" + fallback, sep=","
            )
        return data

    def __to_iso(self, df) -> pd.DataFrame:
        """
        Convert Johns Hopkins University dataset to nicely formatted DataFrame.
        Drops Lat/Long columns and reformats to a multi-index of (country, state).

        Parameters
        ----------
        df : pandas.DataFrame
            Dataframe to convert to the iso format

        Returns
        -------
        : pandas.DataFrame
        """

        # change columns & index
        df = df.drop(columns=['Lat', 'Long']).rename(columns={
            'Province/State': 'state',
            'Country/Region': 'country'
        })
        df = df.set_index(['country', 'state'])
        # datetime columns
        df.columns = [datetime.datetime.strptime(d, '%m/%d/%y') for d in df.columns]
        return df.T

    def get_confirmed_deaths_recovered(self, country:str = None, state:str = None, begin_date:datetime.datetime = None, end_date:datetime.datetime = None) -> pd.DataFrame:
        """
        Retrieves all confirmed, deaths and recovered cases from the Johns Hopkins University dataset as a DataFrame with datetime index.
        Can be filtered by country and state, if only a country is given all available states get summed up.

        Parameters
        ----------
        country : str, optional
            name of the country (the "Country/Region" column), can be None if the whole summed up data is wanted (why would you do this?)
        state : str, optional
            name of the state (the "Province/State" column), can be None if country is set or the whole summed up data is wanted
        begin_date : datetime.datetime, optional
            intial date for the returned data, if no value is given the first date in the dataset is used
        end_date : datetime.datetime, optional
            last date for the returned data, if no value is given the most recent date in the dataset is used

        Returns
        -------
        : pandas.DataFrame
        """

        # filter
        df = pd.DataFrame(columns=['date', 'confirmed', 'deaths', 'recovered']).set_index('date')
        if country is None:
            df['confirmed'] = self.confirmed.sum(axis = 1, skipna = True)
            df['deaths'] = self.deaths.sum(axis = 1, skipna = True)
            df['recovered'] = self.recovered.sum(axis = 1, skipna = True)       
        else:
            if state is None:
                df['confirmed'] = self.confirmed[country].sum(axis = 1, skipna = True)
                df['deaths'] = self.deaths[country].sum(axis = 1, skipna = True)
                df['recovered'] = self.recovered[country].sum(axis = 1, skipna = True)      
            else:
                df['confirmed'] = self.confirmed[(country,state)]
                df['deaths'] = self.deaths[(country,state)]
                df['recovered'] = self.recovered[(country,state)]   

        df.index.name = 'date'

        return self.filter_date(df,begin_date,end_date)

    def get_confirmed(self, country:str = None, state:str = None, begin_date:datetime.datetime = None, end_date:datetime.datetime = None) -> pd.DataFrame:
        """
        Retrieves all confirmed cases from the Johns Hopkins University dataset as a DataFrame with datetime index.
        Can be filtered by country and state, if only a country is given all available states get summed up.

        Parameters
        ----------
        country : str, optional
            name of the country (the "Country/Region" column), can be None
        state : str, optional
            name of the state (the "Province/State" column), can be None
        begin_date : datetime.datetime, optional
            intial date for the returned data, if no value is given the first date in the dataset is used
        end_date : datetime.datetime, optional
            last date for the returned data, if no value is given the most recent date in the dataset is used

        Returns
        -------
        : pandas.DataFrame
            table with confirmed cases and the date as index
        """

        if country == "None":
            country = None
        if state == "None":
            state = None
        df = pd.DataFrame(columns=['date', 'confirmed']).set_index('date')
        if country is None:
            df['confirmed'] = self.confirmed.sum(axis = 1, skipna = True)
        else:
            if state is None:
                df['confirmed'] = self.confirmed[country].sum(axis = 1, skipna = True)         
            else:
                df['confirmed'] = self.confirmed[(country,state)]
        df.index.name = 'date'

        return self.filter_date(df,begin_date,end_date)

    def get_new_confirmed(self, country:str = None, state:str = None, begin_date:datetime.datetime = None, end_date:datetime.datetime = None) -> pd.DataFrame:
        """
        Retrieves all daily confirmed cases from the Johns Hopkins University dataset as a DataFrame with datetime index.
        Can be filtered by country and state, if only a country is given all available states get summed up.

        Parameters
        ----------
        country : str, optional
            name of the country (the "Country/Region" column), can be None 
        state : str, optional
            name of the state (the "Province/State" column), can be None
        begin_date : datetime.datetime, optional
            intial date for the returned data, if no value is given the first date in the dataset is used
        end_date : datetime.datetime, optional
            last date for the returned data, if no value is given the most recent date in the dataset is used

        Returns
        -------
        : pandas.DataFrame
            table with daily new recovered cases and the date as index
        """        
        df = self.get_confirmed(country,state,begin_date,end_date)
        df = df.diff().drop(df.index[0]).astype(int) # Neat oneliner to also drop the first row and set the type back to int 
        return df

    def get_deaths(self, country:str = None, state:str = None, begin_date:datetime.datetime = None, end_date:datetime.datetime = None) -> pd.DataFrame:
        """
        Retrieves all deaths from the Johns Hopkins University dataset as a DataFrame with datetime index.
        Can be filtered by country and state, if only a country is given all available states get summed up.

        Parameters
        ----------
        country : str, optional
            name of the country (the "Country/Region" column), can be None
        state : str, optional
            name of the state (the "Province/State" column), can be None
        begin_date : datetime.datetime, optional
            intial date for the returned data, if no value is given the first date in the dataset is used
        end_date : datetime.datetime, optional
            last date for the returned data, if no value is given the most recent date in the dataset is used

        Returns
        -------
        : pandas.DataFrame
            table with confirmed cases and the date as index
        """
        if country == "None":
            country = None
        if state == "None":
            state = None

        df = pd.DataFrame(columns=['date', 'deaths']).set_index('date')
        if country is None:
            df['deaths'] = self.deaths.sum(axis = 1, skipna = True)
        else:
            if state is None:
                df['deaths'] = self.deaths[country].sum(axis = 1, skipna = True)              
            else:
                df['deaths'] = self.deaths[(country,state)]
        
        df.index.name = 'date'

        return self.filter_date(df,begin_date,end_date)

    def get_new_deaths(self, country:str = None, state:str = None, begin_date:datetime.datetime = None, end_date:datetime.datetime = None) -> pd.DataFrame:
        """
        Retrieves all daily deaths from the Johns Hopkins University dataset as a DataFrame with datetime index.
        Can be filtered by country and state, if only a country is given all available states get summed up.

        Parameters
        ----------
        country : str, optional
            name of the country (the "Country/Region" column), can be None 
        state : str, optional
            name of the state (the "Province/State" column), can be None
        begin_date : datetime.datetime, optional
            intial date for the returned data, if no value is given the first date in the dataset is used
        end_date : datetime.datetime, optional
            last date for the returned data, if no value is given the most recent date in the dataset is used

        Returns
        -------
        : pandas.DataFrame
            table with daily new recovered cases and the date as index
        """        
        df = self.get_deaths(country,state,begin_date,end_date)
        df = df.diff().drop(df.index[0]).astype(int) # Neat oneliner to also drop the first row and set the type back to int 
        return df

    def get_recovered(self, country:str = None, state:str = None, begin_date:datetime.datetime = None, end_date:datetime.datetime = None) -> pd.DataFrame:
        """
        Retrieves all recovered cases from the Johns Hopkins University dataset as a DataFrame with datetime index.
        Can be filtered by country and state, if only a country is given all available states get summed up.

        Parameters
        ----------
        country : str, optional
            name of the country (the "Country/Region" column), can be None 
        state : str, optional
            name of the state (the "Province/State" column), can be None
        begin_date : datetime.datetime, optional
            intial date for the returned data, if no value is given the first date in the dataset is used
        end_date : datetime.datetime, optional
            last date for the returned data, if no value is given the most recent date in the dataset is used

        Returns
        -------
        : pandas.DataFrame
            table with recovered cases and the date as index
        """
        if country == "None":
            country = None
        if state == "None":
            state = None

        df = pd.DataFrame(columns=['date', 'recovered']).set_index('date')
        if country is None:
            df['recovered'] = self.recovered.sum()
        else:
            if state is None:
                df['recovered'] = self.recovered.loc[country].sum()              
            else:
                df['recovered'] = self.recovered.loc[(country,state)]

        df.index.name = 'date'

        return self.filter_date(df,begin_date,end_date)

    def get_new_recovered(self, country:str = None, state:str = None, begin_date:datetime.datetime = None, end_date:datetime.datetime = None) -> pd.DataFrame:
        """
        Retrieves all daily recovered cases from the Johns Hopkins University dataset as a DataFrame with datetime index.
        Can be filtered by country and state, if only a country is given all available states get summed up.

        Parameters
        ----------
        country : str, optional
            name of the country (the "Country/Region" column), can be None 
        state : str, optional
            name of the state (the "Province/State" column), can be None
        begin_date : datetime.datetime, optional
            intial date for the returned data, if no value is given the first date in the dataset is used
        end_date : datetime.datetime, optional
            last date for the returned data, if no value is given the most recent date in the dataset is used

        Returns
        -------
        : pandas.DataFrame
            table with daily new recovered cases and the date as index
        """        
        df = self.get_recovered(country,state,begin_date,end_date)

        df = df.diff().drop(df.index[0]).astype(int) # Neat oneliner to also drop the first row and set the type back to int 
        return df

    def filter_date(self, df, begin_date:datetime.datetime = None, end_date:datetime.datetime = None) -> pd.DataFrame:
        """
        Returns give dataframe between begin and end date. Dataframe has to have a datetime index.

        Parameters
        ----------
        begin_date : datetime.datetime, optional
            First day that should be filtered, in format '%m/%d/%y' 
        end_date : datetime.datetime, optional
            Last day that should be filtered, in format '%m/%d/%y' 

        Returns
        -------
        : pandas.DataFrame
        """
        if begin_date is None:
            begin_date = self.__get_first_date(df)
        if end_date is None:
            end_date = self.__get_last_date(df)

        if not isinstance(begin_date, datetime.datetime) and isinstance(end_date, datetime.datetime):
            raise ValueError('Invalid begin_date, end_date: has to be datetime.datetime object')

        return df[begin_date:end_date]

    def __get_first_date(self,df):
        return df.index[0]
    def __get_last_date(self,df):
        return df.index[-1]

    def get_possible_countries_states(self):
        """
        Used to obtain all different possible countries with there corresponding possible states.

        Returns
        -------
        : pandas.DataFrame in the format
        """
        all_entrys = list(self.confirmed.columns) + list(self.deaths.columns) + list(self.recovered.columns)
        df = pd.DataFrame(all_entrys, columns = ['country', 'state']) 
        df = df.groupby('country').apply(lambda x: x['state'].unique())
        return df

class RKI():
    """
    Data retrieval for the Robert Koch Institute
    https://www.rki.de/.

    The data gets retrieved from the arcgis dashboard.
    Features:
        - download the full dataset
        - filter by date
        see the methods in this class for more infos on the features and how to use them

    """
    def __init__(self, auto_download = False):
        self.data: pd.DataFrame

        if auto_download:
            self.download_all_available_data()

    def download_all_available_data(self, try_max=10)-> pd.DataFrame:
        '''
        Attempts to download the most current data from the Robert Koch Institute. Separated into the different regions (landkreise).
        
        Parameters
        ----------
        try_max : int, optional
            Maximum number of tries for each query. (default:10)
        Returns
        -------
        : pandas.DataFrame
            Containing all the RKI data from arcgis website.
            In the format:
                [Altersgruppe, AnzahlFall, AnzahlGenesen, AnzahlTodesfall, Bundesland, Geschlecht, Landkreis, Meldedatum, NeuGenesen, NeuerFall, Refdatum, date, date_ref]        
        '''
        landkreise_max=412#Strangely there are 412 regions defined by the Robert Koch Insitute in contrast to the offical 294 rural districts or the 401 administrative districts.
        url_id = 'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/ArcGIS/rest/services/RKI_COVID19/FeatureServer/0/query?where=0%3D0&objectIds=&time=&resultType=none&outFields=idLandkreis&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=true&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=pjson&token='
        url = urllib.request.urlopen(url_id)
        json_data = json.loads(url.read().decode())
        n_data = len(json_data['features'])
        unique_ids = [json_data['features'][i]['attributes']['IdLandkreis'] for i in range(n_data)]

        #If the number of landkreise is smaller than landkreise_max, uses local copy (query system can behave weirdly during updates)
        if n_data >= landkreise_max:

            print('Downloading {:d} unique Landkreise. May take a while.\n'.format(n_data))

            df_keys = ['Bundesland', 'Landkreis', 'Altersgruppe', 'Geschlecht', 'AnzahlFall',
               'AnzahlTodesfall', 'Meldedatum', 'NeuerFall', 'NeuGenesen', 'AnzahlGenesen','Refdatum']

            df = pd.DataFrame(columns=df_keys)

            #Fills DF with data from all landkreise
            for idlandkreis in unique_ids:
                
                url_str = 'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/ArcGIS/rest/services/RKI_COVID19/FeatureServer/0//query?where=IdLandkreis%3D'+ idlandkreis + '&objectIds=&time=&resultType=none&outFields=Bundesland%2C+Landkreis%2C+Altersgruppe%2C+Geschlecht%2C+AnzahlFall%2C+AnzahlTodesfall%2C+Meldedatum%2C+NeuerFall%2C+Refdatum%2C+NeuGenesen%2C+AnzahlGenesen&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=pjson&token='

                count_try = 0

                while count_try < try_max:
                    try:
                        with urllib.request.urlopen(url_str) as url:
                            json_data = json.loads(url.read().decode())

                        n_data = len(json_data['features'])

                        if n_data > 5000:
                            raise ValueError('Query limit exceeded')

                        data_flat = [json_data['features'][i]['attributes'] for i in range(n_data)]

                        break

                    except:
                        count_try += 1           

                if count_try == try_max:
                    raise ValueError('Maximum limit of tries exceeded.')

                df_temp = pd.DataFrame(data_flat)
            
                #Very inneficient, but it will do
                df = pd.concat([df, df_temp], ignore_index=True)

            df['date'] = df['Meldedatum'].apply(lambda x: datetime.datetime.fromtimestamp(x/1e3))   
            df['date_ref'] = df['Refdatum'].apply(lambda x: datetime.datetime.fromtimestamp(x/1e3))   

        else:

            print("Warning: Query returned {:d} landkreise (out of {:d}), likely being updated at the moment. Using fallback (outdated) copy.".format(n_data, landkreise_max))
            this_dir = os.path.dirname(__file__)
            df = pd.read_csv(this_dir + "/../data/rki_fallback_gzip.dat", sep=",", compression='gzip')
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
            df['date_ref'] = pd.to_datetime(df['date'], format='%d-%m-%Y')

        print("Finished downloading")
        self.data=df
        return df

    def get_confirmed(self, bundesland:str = None, landkreis:str = None, begin_date:datetime.datetime = None, end_date:datetime.datetime = None, date_type:str='date')-> pd.DataFrame:
        """
        Gets all total confirmed cases for a region as dataframe with date index. Can be filtered with multiple arguments.
        
        Parameters
        ----------
        bundesland : str, optional
            if no value is provided it will use the full summed up dataset for Germany
        landkreis : str, optional
            if no value is provided it will use the full summed up dataset for the region (bundesland)
        begin_date : datetime.datetime, optional
            initial date, if no value is provided it will use the first possible date
        end_date : datetime.datetime, optional  
            last date, if no value is provided it will use the most recent possible date
        date_type : str, optional
            type of date to use: reported date 'date' (Meldedatum in the original dataset), or symptom date 'date_ref' (Refdatum in the original dataset)

        Returns
        -------
        :pd.DataFrame
        """
        # Set level for filter use bundesland if no landkreis is supplied else us landkreis
        level = None
        value = None
        if bundesland is not None:
            level = "Bundesland"
            value = bundesland
        if landkreis is not None:
            level = "Landkreis"
            value = landkreis

        df = self.filter(begin_date,end_date,'AnzahlFall',date_type,level,value)
        return df

    def get_new_confirmed(self, bundesland:str = None, landkreis:str = None, begin_date:datetime.datetime = None, end_date:datetime.datetime = None, date_type:str='date')-> pd.DataFrame:
        """
        Retrieves all new confirmed cases daily from the Johns Hopkins University dataset as a DataFrame with datetime index.
        Can be filtered by country and state, if only a country is given all available states get summed up.

        Parameters
        ----------
        country : str, optional
            name of the country (the "Country/Region" column), can be None 
        state : str, optional
            name of the state (the "Province/State" column), can be None
        begin_date : datetime.datetime, optional
            intial date for the returned data, if no value is given the first date in the dataset is used
        end_date : datetime.datetime, optional
            last date for the returned data, if no value is given the most recent date in the dataset is used

        Returns
        -------
        : pandas.DataFrame
            table with daily new confirmed and the date as index
        """        
        df = self.get_confirmed(bundesland, landkreis, begin_date, end_date, date_type)
        #Get difference to the days beforehand
        df = df.diff().drop(df.index[0]).astype(int) # Neat oneliner to also drop the first row and set the type back to int 
        return df

    def get_deaths(self, bundesland:str = None, landkreis:str = None, begin_date:datetime.datetime = None, end_date:datetime.datetime = None, date_type:str='date')-> pd.DataFrame:
        """
        Gets all total deaths for a region as dataframe with date index. Can be filtered with multiple arguments.
        
        Parameters
        ----------
        bundesland : str, optional
            if no value is provided it will use the full summed up dataset for Germany
        landkreis : str, optional
            if no value is provided it will use the full summed up dataset for the region (bundesland)
        begin_date : datetime.datetime, optional
            initial date, if no value is provided it will use the first possible date
        end_date : datetime.datetime, optional  
            last date, if no value is provided it will use the most recent possible date
        date_type : str, optional
            type of date to use: reported date 'date' (Meldedatum in the original dataset), or symptom date 'date_ref' (Refdatum in the original dataset)

        Returns
        -------
        :pd.DataFrame
        """
        level = None
        value = None
        if bundesland is not None:
            level = "Bundesland"
            value = bundesland
        if landkreis is not None:
            level = "Landkreis"
            value = landkreis

        df = self.filter(begin_date,end_date,'AnzahlTodesfall',date_type,level,value)
        return df

    def get_new_deaths(self, bundesland:str = None, landkreis:str = None, begin_date:datetime.datetime = None, end_date:datetime.datetime = None, date_type:str='date')-> pd.DataFrame:
        """
        Retrieves all new deaths daily from the Johns Hopkins University dataset as a DataFrame with datetime index.
        Can be filtered by country and state, if only a country is given all available states get summed up.

        Parameters
        ----------
        country : str, optional
            name of the country (the "Country/Region" column), can be None 
        state : str, optional
            name of the state (the "Province/State" column), can be None
        begin_date : datetime.datetime, optional
            intial date for the returned data, if no value is given the first date in the dataset is used
        end_date : datetime.datetime, optional
            last date for the returned data, if no value is given the most recent date in the dataset is used

        Returns
        -------
        : pandas.DataFrame
            table with daily new deaths and the date as index
        """        
        df = self.get_deaths(bundesland, landkreis, begin_date, end_date, date_type)
        #Get difference to the days beforehand
        df = df.diff().drop(df.index[0]).astype(int) # Neat oneliner to also drop the first row and set the type back to int 
        return df

    def get_recovered(self, bundesland:str = None, landkreis:str = None, begin_date:datetime.datetime = None, end_date:datetime.datetime = None, date_type:str='date')-> pd.DataFrame:
        """
        Gets all total recovered cases as dataframe with date index. Can be filtered with multiple arguments.
        
        Parameters
        ----------
        bundesland : str, optional
            if no value is provided it will use the full summed up dataset for Germany
        landkreis : str, optional
            if no value is provided it will use the full summed up dataset for the region (bundesland)
        begin_date : datetime.datetime, optional
            initial date, if no value is provided it will use the first possible date
        end_date : datetime.datetime, optional  
            last date, if no value is provided it will use the most recent possible date
        date_type : str, optional
            type of date to use: reported date 'date' (Meldedatum in the original dataset), or symptom date 'date_ref' (Refdatum in the original dataset)

        Returns
        -------
        :pd.DataFrame
        """
        # Set level for filter use bundesland if no landkreis is supplied else us landkreis
        level = None
        value = None
        if bundesland is not None:
            level = "Bundesland"
            value = bundesland
        if landkreis is not None:
            level = "Landkreis"
            value = landkreis

        df = self.filter(begin_date,end_date,'AnzahlGenesen',date_type,level,value)
        return df

    def get_new_recovered(self, bundesland:str = None, landkreis:str = None, begin_date:datetime.datetime = None, end_date:datetime.datetime = None, date_type:str='date')-> pd.DataFrame:
        """
        Retrieves all new cases daily from the Johns Hopkins University dataset as a DataFrame with datetime index.
        Can be filtered by country and state, if only a country is given all available states get summed up.

        Parameters
        ----------
        country : str, optional
            name of the country (the "Country/Region" column), can be None 
        state : str, optional
            name of the state (the "Province/State" column), can be None
        begin_date : datetime.datetime, optional
            intial date for the returned data, if no value is given the first date in the dataset is used
        end_date : datetime.datetime, optional
            last date for the returned data, if no value is given the most recent date in the dataset is used

        Returns
        -------
        : pandas.DataFrame
            table with daily new recovered cases and the date as index
        """        
        df = self.get_recovered(bundesland, landkreis, begin_date, end_date, date_type)
        #Get difference to the days beforehand
        print(df.index)
        df = df.diff().drop(df.index[0]).astype(int) # Neat oneliner to also drop the first row and set the type back to int 
        return df

    def filter(self, begin_date:datetime.datetime = None, end_date:datetime.datetime = None, variable = 'AnzahlFall', date_type='date', level = None, value = None) -> pd.DataFrame:
        """
        Filters the obtained dataset for a given time period and returns an array ONLY containing only the desired variable.
        
        Parameters
        ----------
        begin_date : datetime.datetime, optional
            initial date, if no value is provided it will use the first possible date
        end_date : datetime.datetime, optional  
            last date, if no value is provided it will use the most recent possible date
        variable : str, optional
            type of variable to return
            possible types are:
                "AnzahlFall"      : cases (default)
                "AnzahlTodesfall" : deaths
                "AnzahlGenesen"   : recovered
        date_type : str, optional
            type of date to use: reported date 'date' (Meldedatum in the original dataset), or symptom date 'date_ref' (Refdatum in the original dataset)
        level : str, optional
            possible strings are:
                "None"       : return data from all Germany (default)
                "Bundesland" : a state 
                "Landkreis"  : a region
        value : None, optional
            string of the state/region
            e.g. "Sachsen"

        Returns
        -------
        : pd.DataFrame
            array with ONLY the requested variable, in the requested range. (one dimensional)
        """
        #Input parsing
        if variable not in ['AnzahlFall', 'AnzahlTodesfall', 'AnzahlGenesen']:
            raise ValueError('Invalid variable. Valid options: "AnzahlFall", "AnzahlTodesfall", "AnzahlGenesen"')

        if level not in ['Landkreis', 'Bundesland', None]:
            raise ValueError('Invalid level. Valid options: "Landkreis", "Bundesland", None')

        if date_type not in ['date', 'date_ref']:
            raise ValueError('Invalid date_type. Valid options: "date", "date_ref"')

        df = self.data.sort_values(date_type)
        if begin_date is None:
            begin_date = df[date_type].iloc[0]
        if end_date is None:
            end_date = df[date_type].iloc[-1]

        if not isinstance(begin_date, datetime.datetime) and isinstance(end_date, datetime.datetime):
            raise ValueError('Invalid begin_date, end_date: has to be datetime.datetime object')

        #Keeps only the relevant data
        df = self.data

        if level is not None:
            df = df[df[level]==value][[date_type, variable]]

        df_series = df.groupby(date_type)[variable].sum().cumsum()

        return df_series[begin_date:end_date]

    def filter_all_bundesland(self, begin_date:datetime.datetime = None, end_date:datetime.datetime = None, variable = 'AnzahlFall', date_type='date') -> pd.DataFrame:
        """
        Filters the full RKI dataset     

        Parameters
        ----------
        df : DataFrame
            RKI dataframe, from get_rki()
        begin_date : datetime.datetime
            initial date to return
        end_date : datetime.datetime
            last date to return
        variable : str, optional
            type of variable to return: cases ("AnzahlFall"), deaths ("AnzahlTodesfall"), recovered ("AnzahlGenesen")
        date_type : str, optional
            type of date to use: reported date 'date' (Meldedatum in the original dataset), or symptom date 'date_ref' (Refdatum in the original dataset)
        
        Returns
        -------
        : pd.DataFrame
            DataFrame with datetime dates as index, and all German regions (bundesländer) as columns
        """
        if variable not in ['AnzahlFall', 'AnzahlTodesfall', 'AnzahlGenesen']:
            raise ValueError('Invalid variable. Valid options: "AnzahlFall", "AnzahlTodesfall", "AnzahlGenesen"')

        if date_type not in ['date', 'date_ref']:
            raise ValueError('Invalid date_type. Valid options: "date", "date_ref"')

        if begin_date is None:
            begin_date = self.data[date_type].iloc[0]
        if end_date is None:
            end_date = self.data[date_type].iloc[-1]

        if not isinstance(begin_date, datetime.datetime) and isinstance(end_date, datetime.datetime):
            raise ValueError('Invalid begin_date, end_date: has to be datetime.datetime object')

        #Nifty, if slightly unreadable one-liner
        df = self.data
        df2 = df.groupby([date_type,'Bundesland'])[variable].sum().reset_index().pivot(index=date_type,columns='Bundesland', values=variable).fillna(0)

        #Returns cumsum of variable
        return df2[begin_date:end_date].cumsum()