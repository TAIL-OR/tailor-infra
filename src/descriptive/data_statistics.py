import pandas as pd
import datetime
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
data_path = os.path.join(parent_directory, 'data')

class Statistics:
    def __init__(self):
        self.dataset = pd.read_csv(os.path.join(data_path, 'dados-abertos.csv'), sep=';')
        
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
    
    def region_pontuation(self):
        bed_availability = 22
        transmission_rate = 15
        waiting_line = 20
        vaccination = 25

        pontuation = {"bed_availability": bed_availability, "transmission_rate": transmission_rate,
                      "waiting_line": waiting_line, "vaccination": vaccination}

        return pontuation
        
    
    def region_get_total_cases(self):
        return int(self.dataset.size)
    
    def region_get_active_cases(self):
        return 872
    
    def region_get_recover_cases(self): 
        return int(self.dataset.loc[self.dataset['Óbito'] != 'Sim'].size)
    
    def region_get_death_cases(self):
        return int(self.dataset.loc[self.dataset['Óbito'] != 'Não'].size)
    
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
            key = str(month_year[0]) + '-' + str(month_year[1])
            deaths[key] = int(deaths_per_month)
        
        return deaths
    
    def region_get_vaccination(self):
        return {'vaccinated': 61, 'not_vaccinated': 39}
    
    def region_get_first_vaccine_dose_per_month(self):
        return {"3-2024": 120, "2-2024": 220, "1-2024": 280, "12-2023": 315,
                "11-2023": 474, "10-2023": 590, "9-2023": 712, "8-2023": 893, "7-2023": 1046}
    
    def region_get_second_vaccine_dose_per_month(self):
        return {"3-2024": 10, "2-2024": 50, "1-2024": 153, "12-2023": 198,
                "11-2023": 264, "10-2023": 276, "9-2023": 312, "8-2023": 356, "7-2023": 578}
    
    def region_get_third_vaccine_dose_per_month(self):
        return {"3-2024": 0, "2-2024": 0, "1-2024": 12, "12-2023": 56,
                "11-2023": 87, "10-2023": 91, "9-2023": 123, "8-2023": 215, "7-2023": 231}
        
    def region_get_transmition_rate_per_month(self):
        return {"3-2024": 1.2, "2-2024": 1.3, "1-2024": 1.6, "12-2023": 1.6,
                "11-2023": 1.8, "10-2023": 1.5, "9-2023": 1.3, "8-2023": 1.4, "7-2023": 0.7}
    
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
            key = str(month_year[0]) + '-' + str(month_year[1])
            contamination[key] = int(deaths_per_month)
        
        return contamination
    
    def region_get_mild_cases_per_month(self):
        return {"3-2024": 120, "2-2024": 231, "1-2024": 162, "12-2023": 114,
                "11-2023": 119, "10-2023": 254, "9-2023": 341, "8-2023": 411, "7-2023": 376}

    def region_get_moderate_cases_per_month(self):
        return {"3-2024": 85, "2-2024": 62, "1-2024": 21, "12-2023": 27,
                "11-2023": 92, "10-2023": 101, "9-2023": 65, "8-2023": 212, "7-2023": 176}
    
    def region_get_serious_cases_per_month(self):
        return {"3-2024": 7, "2-2024": 15, "1-2024": 13, "12-2023": 18,
                "11-2023": 19, "10-2023": 21, "9-2023": 32, "8-2023": 41, "7-2023": 63}
    
    def region_get_free_beds_per_month(self):
        return {"3-2024": 873, "2-2024": 889, "1-2024": 892, "12-2023": 921,
                "11-2023": 976, "10-2023": 1003, "9-2023": 1037, "8-2023": 1243, "7-2023": 1293}
    
    def region_get_occupied_beds_per_month(self):
        return {"3-2024": 453, "2-2024": 637, "1-2024": 831, "12-2023": 899,
                "11-2023": 962, "10-2023": 1000, "9-2023": 982, "8-2023": 876, "7-2023": 800}
    
    def region_get_waitlist_per_month(self):
        return {"3-2024": 51, "2-2024": 65, "1-2024": 73, "12-2023": 79,
                "11-2023": 82, "10-2023": 123, "9-2023": 256, "8-2023": 762, "7-2023": 103}
        
    
    # Mocked Data

    def hospital_pontuation(self):
        bed_availability = 24
        infraestructure = 12
        health_professional = 15
        equipments = 25
        supplies = 20

        pontuation = {"bed_availability": bed_availability, "infraestructure": infraestructure,
                        "health_professional": health_professional, "equipments": equipments,
                        "supplies": supplies}

        return pontuation
    
    def hospital_get_total_cases(self):
        return 9829
    
    def hospital_get_active_cases(self):
        return 116
    
    def hospital_get_recover_cases(self):
        return 9439
    
    def hospital_get_death_cases(self):
        return 274

    def hospital_get_deaths_per_month(self):
        return {"3-2024": 12, "2-2024": 25, "1-2024": 11, "12-2023": 36,
                "11-2023": 19, "10-2023": 17, "9-2023": 23, "8-2023": 15, "7-2023": 19}
    
    def hospital_get_mild_cases_per_month(self):
        return {"3-2024": 120, "2-2024": 231, "1-2024": 162, "12-2023": 114,
                "11-2023": 119, "10-2023": 254, "9-2023": 341, "8-2023": 411, "7-2023": 376}
        
    def hospital_get_moderate_cases_per_month(self):
        return {"3-2024": 85, "2-2024": 62, "1-2024": 21, "12-2023": 27,
                "11-2023": 92, "10-2023": 101, "9-2023": 65, "8-2023": 212, "7-2023": 176}
        
    def hospital_get_serious_cases_per_month(self):
        return {"3-2024": 7, "2-2024": 15, "1-2024": 13, "12-2023": 18,
                "11-2023": 19, "10-2023": 21, "9-2023": 32, "8-2023": 41, "7-2023": 63}

    def hospital_get_free_beds_per_month(self):
        return {"3-2024": 873, "2-2024": 889, "1-2024": 892, "12-2023": 921,
                "11-2023": 976, "10-2023": 1003, "9-2023": 1037, "8-2023": 1243, "7-2023": 1293}
        
    def hospital_get_occupied_beds_per_month(self):
        return {"3-2024": 453, "2-2024": 637, "1-2024": 831, "12-2023": 899,
                "11-2023": 962, "10-2023": 1000, "9-2023": 982, "8-2023": 876, "7-2023": 800}
        