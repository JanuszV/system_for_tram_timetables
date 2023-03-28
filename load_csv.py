import tkinter as tk
from tkinter import filedialog
import glob
import pandas as pd
import time

def zmiana(U8):
    i = 0
    sekundy = 0
    for element in U8:
        if element == ':' : sekundy += 0
        elif i == 0 : sekundy += 36000 * int(element)
        elif i == 1 : sekundy += 3600 * int(element)
        elif i == 3 : sekundy += 600 * int(element)
        elif i == 4 : sekundy += 60 * int(element)
        elif i == 6 : sekundy += 10 * int(element)
        elif i == 7 : sekundy += int(element)
        else : break
        i += 1
    return sekundy

def select_csv_directory():

    directory = filedialog.askdirectory()
    path = directory + '/*.csv'
    df = pd.DataFrame()
    data_frames = []
    file_names = glob.glob(path)
    i = 0
    for file_name in file_names:
        df = pd.read_csv(file_name, encoding = 'unicode_escape', sep = ";", header = None, error_bad_lines = False, engine = 'python', usecols = [0, 5, 7, 8, 12, 13, 14, 15, 17, 22])
        data_frames.append(df)
        i += 1
    df = pd.concat(data_frames, ignore_index=True)
    df.columns=['DT_KARTY', 'LP_KURSU', 'NR_LINI', 'LP_PRZYST', 'RJ_KIEDY', 'DATA', 'KIEDY', 'POSTOJ', 'SYM_SLUPKA', 'OPIS_TABL']
    #Usunięcie linii autobusowych
    df3 = df[~df['NR_LINI'].str.contains("[a-zA-Z]").fillna(False)]
    df3['NR_LINI']=df3['NR_LINI'].astype(int)
    df3.drop(df3[df3['NR_LINI'] > 100].index, inplace = True)
    #Usunięcie NaN
    df4=df3.dropna(subset=['DATA'])
    #Usunięcie komórek PUSTA
    df4.drop(df4[df4['OPIS_TABL'] == 'PUSTA'].index, inplace = True)
    #  Usunięcie postojów dłuższych niż 180 sekund
    df4.drop(df4[df4['POSTOJ'] > 180].index, inplace = True)
    df4.reset_index(drop = True, inplace = True)
    save_directory = filedialog.askdirectory()
    save_path = save_directory +'/Support.csv'
    df4.to_csv(save_path, index = False)
    (num_rows, num_cols) = df4.shape
    shape =[num_rows, num_cols]
    return save_path, i , shape

def process_csv(path, shape):
    przystanki = pd.DataFrame()
    chunk_size = 2500
    lp_przyst=1
    index_pary=0
    iterator = pd.read_csv(path, chunksize = chunk_size, low_memory = False, iterator = True)

    for chunk in iterator :#pd.read_csv(support_file_path, chunksize=chunk_size):
        (chunk_rows, chunk_col) = chunk.shape
        chunk_index = 0
        chunk2=pd.DataFrame()
        for index, row in chunk.iterrows():
            if chunk_index + 2 > chunk_rows : continue
            if index + 2 > shape[0] : continue
            elif (chunk.loc[index, 'LP_PRZYST'] == lp_przyst and chunk.loc[index+1, 'LP_PRZYST'] == lp_przyst + 1) and (chunk.loc[index,'LP_KURSU'] == chunk.loc[index + 1,'LP_KURSU']):
                chunk2.loc[index_pary, 0] = chunk.loc[index, 'SYM_SLUPKA']
                chunk2.loc[index_pary, 1] = chunk.loc[index + 1, 'SYM_SLUPKA']
                chunk2.loc[index_pary, 2] = zmiana(chunk.loc[index +1, 'KIEDY']) - chunk.loc[index + 1, 'POSTOJ'] - zmiana(chunk.loc[index, 'KIEDY'])
                #usunięcie przejazdów ujemnych
                if (chunk2.loc[index_pary, 2] < 0) : 
                    chunk2.drop(index = index_pary, inplace = True)
                lp_przyst += 1
                index_pary += 1
            else:
                lp_przyst = 1
            chunk_index += 1  
        przystanki=pd.concat([przystanki,chunk2])
        pass
    czasy = pd.DataFrame({'NAZWA':[0], 1:[0], 2:[0], 'CZAS':[0]})
    (num_rows, num_col) = przystanki.shape
    numer = 0
    
    for index, row in przystanki.iterrows():
        nazwa = "{}{}".format(przystanki.loc[index, 0], przystanki.loc[index, 1])
        if index + 1 > num_rows : break
        elif (czasy['NAZWA'] == nazwa).any() :
            i = czasy[czasy['NAZWA'] == nazwa].index[0]
            czasy.loc[i, 1] += przystanki.loc[index, 2]
            czasy.loc[i, 2] += 1
        else:
            czasy.loc[numer, 'NAZWA'] = nazwa
            czasy.loc[numer, 1] = 0
            czasy.loc[numer, 2] = 0
            czasy.loc[numer, 1] += przystanki.loc[index, 2]
            czasy.loc[numer, 2] += 1
            numer += 1
    czasy['CZAS'] = czasy[1]/czasy[2]
    czasy=czasy.drop([1,2], axis=1)
    czasy['CZAS'] = czasy['CZAS'].round(0)
    return czasy
