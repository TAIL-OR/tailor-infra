import pandas as pd
import datetime

class Statistics:
    def __init__(self):
        self.dataset = pd.read_csv('src/predictive/data/dados-abertos.csv', sep=';')
        
    def get_last_nine_months(self):
        month = datetime.datetime.now().month
        year = datetime.datetime.now().year
        last_nine_months = []
        
        for i in range(9):
            last_nine_months.append((month, year))
            month -= 1
            if month <= 0:
                month = 12
                year -= 1
        return last_nine_months
    
    def region_get_total_cases(self):
        return self.dataset.size
    
    def region_get_active_cases(self):
        return 872
    
    def region_get_recover_cases(self): 
        return self.dataset.loc[self.dataset['Óbito'] != 'Sim'].size
    
    def region_get_death_cases(self):
        return self.dataset.loc[self.dataset['Óbito'] != 'Não'].size
    
    def region_get_deaths_per_month(self):
        deaths = {}
        last_nine_months = self.get_last_nine_months()
        death_day = self.dataset.loc[self.dataset['Óbito'] != "Não"]['Data do Óbito']
        for month_year in last_nine_months:
            deaths_per_month = 0
            for date in death_day:
                splited_data = date.split('/')
                if int(splited_data[2]) == month_year[1]:
                    if int(splited_data[1]) == int(month_year[0]):
                        deaths_per_month+=1
            deaths[month_year] = deaths_per_month
        
        return deaths
    
    def region_get_vaccination(self):
        return {'vaccinated': 61, 'not_vaccinated': 39}
    
    def region_get_first_vaccine_dose_per_month(self):
        return {(3, 2024): 12, (2, 2024): 25, (1, 2024): 11, (12, 2023): 36,
                (11, 2023): 19, (10, 2023): 17, (9, 2023): 23, (8, 2023): 15, (7, 2023): 19}
    
    def region_get_second_vaccine_dose_per_month(self):
        return {(3, 2024): 12, (2, 2024): 25, (1, 2024): 11, (12, 2023): 36,
                (11, 2023): 19, (10, 2023): 17, (9, 2023): 23, (8, 2023): 15, (7, 2023): 19}
    
    def region_get_third_vaccine_dose_per_month(self):
        return {(3, 2024): 12, (2, 2024): 25, (1, 2024): 11, (12, 2023): 36,
                (11, 2023): 19, (10, 2023): 17, (9, 2023): 23, (8, 2023): 15, (7, 2023): 19}
        
    def region_get_transmition_rate_per_month(self):
        return {(3, 2024): 12, (2, 2024): 25, (1, 2024): 11, (12, 2023): 36,
                (11, 2023): 19, (10, 2023): 17, (9, 2023): 23, (8, 2023): 15, (7, 2023): 19}
    
    def region_get_contamination_per_month(self):
        contamination = {}
        last_nine_months = self.get_last_nine_months()
        death_day = self.dataset['dataPrimeirosintomas']
        for month_year in last_nine_months:
            deaths_per_month = 0
            for date in death_day:
                splited_data = date.split('/')
                if int(splited_data[2]) == month_year[1]:
                    if int(splited_data[1]) == int(month_year[0]):
                        deaths_per_month+=1
            contamination[month_year] = deaths_per_month
    
    def region_get_mild_cases_per_month(self):
        return {(3, 2024): 12, (2, 2024): 25, (1, 2024): 11, (12, 2023): 36,
                (11, 2023): 19, (10, 2023): 17, (9, 2023): 23, (8, 2023): 15, (7, 2023): 19}

    def region_get_moderate_cases_per_month(self):
        return {(3, 2024): 12, (2, 2024): 25, (1, 2024): 11, (12, 2023): 36,
                (11, 2023): 19, (10, 2023): 17, (9, 2023): 23, (8, 2023): 15, (7, 2023): 19}
    
    def region_get_serious_cases_per_month(self):
        return {(3, 2024): 12, (2, 2024): 25, (1, 2024): 11, (12, 2023): 36,
                (11, 2023): 19, (10, 2023): 17, (9, 2023): 23, (8, 2023): 15, (7, 2023): 19}
    
    def region_get_free_beds_per_month(self):
        return {(3, 2024): 12, (2, 2024): 25, (1, 2024): 11, (12, 2023): 36,
                (11, 2023): 19, (10, 2023): 17, (9, 2023): 23, (8, 2023): 15, (7, 2023): 19}
    
    def region_get_occupied_beds_per_month(self):
        return {(3, 2024): 12, (2, 2024): 25, (1, 2024): 11, (12, 2023): 36,
                (11, 2023): 19, (10, 2023): 17, (9, 2023): 23, (8, 2023): 15, (7, 2023): 19}
    
    def region_get_waitlist_per_month(self):
        return {(3, 2024): 12, (2, 2024): 25, (1, 2024): 11, (12, 2023): 36,
                (11, 2023): 19, (10, 2023): 17, (9, 2023): 23, (8, 2023): 15, (7, 2023): 19}
        
    
    # Mocked Data
    
    def hospital_get_total_cases(self):
        return 9829
    
    def hospital_get_active_cases(self):
        return 352
    
    def hospital_get_recover_cases(self):
        return 9439
    
    def hospital_get_death_cases(self):
        return 271

    def hospital_get_deaths_per_month(self):
        return {(3, 2024): 12, (2, 2024): 25, (1, 2024): 11, (12, 2023): 36,
                (11, 2023): 19, (10, 2023): 17, (9, 2023): 23, (8, 2023): 15, (7, 2023): 19}
    
    def hospital_get_mild_cases_per_month(self):
        return {(3, 2024): 12, (2, 2024): 25, (1, 2024): 11, (12, 2023): 36,
                (11, 2023): 19, (10, 2023): 17, (9, 2023): 23, (8, 2023): 15, (7, 2023): 19}
        
    def hospital_get_moderate_cases_per_month(self):
        return {(3, 2024): 12, (2, 2024): 25, (1, 2024): 11, (12, 2023): 36,
                (11, 2023): 19, (10, 2023): 17, (9, 2023): 23, (8, 2023): 15, (7, 2023): 19}
        
    def hospital_get_serious_cases_per_month(self):
        return {(3, 2024): 12, (2, 2024): 25, (1, 2024): 11, (12, 2023): 36,
                (11, 2023): 19, (10, 2023): 17, (9, 2023): 23, (8, 2023): 15, (7, 2023): 19}

    def hospital_get_free_beds_per_month(self):
        return{(3, 2024): 12, (2, 2024): 25, (1, 2024): 11, (12, 2023): 36,
                (11, 2023): 19, (10, 2023): 17, (9, 2023): 23, (8, 2023): 15, (7, 2023): 19}
        
    def hospital_get_occupied_beds_per_month(self):
        return {(3, 2024): 12, (2, 2024): 25, (1, 2024): 11, (12, 2023): 36,
                (11, 2023): 19, (10, 2023): 17, (9, 2023): 23, (8, 2023): 15, (7, 2023): 19}
        