import sqlite3
import pandas as pd
from prettytable import from_db_cursor
import re
import subprocess
import os

if not os.path.exists('../data/covid_data.db') or os.path.getsize('../data/covid_data.db') == 0:
    print('Criando banco de dados...')
    subprocess.run(['python3', 'create_db.py'])
else:
    print('Banco de dados já existe')

def remover_acentos(texto):
    substituicoes = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'ã': 'a', 'õ': 'o',
        'ç': 'c',
        'ñ': 'n',
        'ü': 'u', 'ï': 'i', 'ë': 'e', 'ö': 'o', 'ä': 'a',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'À': 'A', 'È': 'E', 'Ì': 'I', 'Ò': 'O', 'Ù': 'U',
        'Â': 'A', 'Ê': 'E', 'Î': 'I', 'Ô': 'O', 'Û': 'U',
        'Ã': 'A', 'Õ': 'O',
        'Ç': 'C',
        'Ñ': 'N',
        'Ü': 'U', 'Ï': 'I', 'Ë': 'E', 'Ö': 'O', 'Ä': 'A'
    }

    padrao = re.compile('|'.join(substituicoes.keys()))

    resultado = padrao.sub(lambda m: substituicoes[m.group(0)], texto)

    return resultado

def clean_names(name):
    # Remover caracteres especiais e substituir espaços por underscores
    cleaned_name = ''.join(c if c.isalnum() or c in [' ', '_'] else '_' for c in name)
    cleaned_name = remover_acentos(cleaned_name)
    return cleaned_name.replace('/', ' ').replace('2', 'II').lower().replace(' ', '_')


# Conecte ao banco de dados
conn = sqlite3.connect('../data/covid_data.db')

# Crie um cursor
c = conn.cursor()
# Obtenha a consulta do arquivo query.sql
query = open('query.sql', 'r').read()
# Execute a consulta
c.execute(query)
table = from_db_cursor(c)

# Transforme o resultado da consulta em um DataFrame
df = pd.read_sql_query(query, conn)

ras_to_exclude = ['entorno_df']

df['province'] = df['province'].apply(lambda x: clean_names(x))

df = df[~df['province'].isin(ras_to_exclude)]
df['province'] = df['province'].apply(lambda x: remover_acentos(x.replace(' ', '_')).lower().replace('/', '_') if pd.notnull(x) else None)
df = df.rename(columns={'province': 'ra'})
df[['date', 'ra', 'case_cnt']].to_csv('../data/dados-gerais.csv', index=False)

conn.close()

print("Arquivo dados-gerais.csv criado com sucesso!")