from .data_statistics import Statistics

class Descriptive:
    def __init__(self):
        self.statistics = Statistics()
        
    def describe_region_statistics(self):
        pontuation = self.statistics

        total_cases = self.statistics.region_get_total_cases()
        number_active_cases = self.statistics.region_get_active_cases()
        number_recovered_cases = self.statistics.region_get_recover_cases()
        number_deaths = self.statistics.region_get_death_cases()
        case_chart = {'total': total_cases, 'active': number_active_cases, 'recovered': number_recovered_cases, 'deaths': number_deaths}
        
        deaths_last_nine_months = self.statistics.region_get_deaths_per_month()
        death_chart = {'deaths': deaths_last_nine_months}
        
        vaccination = self.statistics.region_get_vaccination()
        vaccination_chart = {'vaccination': vaccination}
        
        first_vaccine_dose_nine_months = self.statistics.region_get_first_vaccine_dose_per_month()
        second_vaccine_dose_nine_months = self.statistics.region_get_second_vaccine_dose_per_month()
        third_vaccine_dose_nine_months = self.statistics.region_get_third_vaccine_dose_per_month()
        vaccine_dose_chart = {"first_dose": first_vaccine_dose_nine_months, "second_dose": second_vaccine_dose_nine_months, "third_dose": third_vaccine_dose_nine_months}

        transmission_rate_nine_months = self.statistics.region_get_transmition_rate_per_month()
        transmission_rate_chart = {"transmission_rate": transmission_rate_nine_months}
        
        contamination_last_nine_months = self.statistics.region_get_contamination_per_month()
        contamination_chart = {"contamination": contamination_last_nine_months}
        
        mild_symptoms_cases_last_nine_months = self.statistics.region_get_mild_cases_per_month()
        moderate_symptoms_cases_last_nine_months = self.statistics.region_get_moderate_cases_per_month()       
        serious_symptoms_cases_last_nine_months = self.statistics.region_get_serious_cases_per_month()   
        syntom_chart = {
            'mild': mild_symptoms_cases_last_nine_months, 
            'moderate': moderate_symptoms_cases_last_nine_months,
            'serious': serious_symptoms_cases_last_nine_months
            }  
        
        free_beds_last_nine_months = self.statistics.region_get_free_beds_per_month()
        occupied_beds_last_nine_months = self.statistics.region_get_occupied_beds_per_month()
        waitlist_last_nine_months = self.statistics.region_get_waitlist_per_month()
        bed_occupancy_chart = {
            'free': free_beds_last_nine_months,
            'occupied': occupied_beds_last_nine_months,
            'waitlist': waitlist_last_nine_months
        }
        
        response = {"case_chart": case_chart, "death_chart": death_chart, "vaccination_chart": vaccination_chart,
                    "vaccine_dose_chart": vaccine_dose_chart, "transmission_rate_chart": transmission_rate_chart, "contamination_chart": contamination_chart,
                    "symtom_chart": syntom_chart, "bed_occupancy_chart": bed_occupancy_chart}
        
        return response
    
    def describe_hospital_statistics(self):
        total_cases = self.statistics.hospital_get_total_cases()
        number_active_cases = self.statistics.hospital_get_active_cases()
        number_recovered_cases = self.statistics.hospital_get_recover_cases()
        number_deaths = self.statistics.hospital_get_death_cases()
        case_chart = {'total': total_cases, 'active': number_active_cases, 'recovered': number_recovered_cases, 'deaths': number_deaths}
        
        deaths_last_nine_months = self.statistics.hospital_get_deaths_per_month()
        death_chart = {'deaths': deaths_last_nine_months}
        
        mild_symptoms_cases_last_nine_months = self.statistics.hospital_get_mild_cases_per_month()
        moderate_symptoms_cases_last_nine_months = self.statistics.hospital_get_moderate_cases_per_month()       
        serious_symptoms_cases_last_nine_months = self.statistics.hospital_get_serious_cases_per_month()   
        syntom_chart = {
            'mild': mild_symptoms_cases_last_nine_months, 
            'moderate': moderate_symptoms_cases_last_nine_months,
            'serious': serious_symptoms_cases_last_nine_months
            }  
        
        free_beds_last_nine_months = self.statistics.hospital_get_free_beds_per_month()
        occupied_beds_last_nine_months = self.statistics.hospital_get_occupied_beds_per_month()
        bed_occupancy_chart = {
            'free': free_beds_last_nine_months,
            'occupied': occupied_beds_last_nine_months
        }
        
        response = {"case_chart": case_chart, "death_chart": death_chart, "symtom_chart": syntom_chart, "bed_occupancy_chart": bed_occupancy_chart}
        
        return response