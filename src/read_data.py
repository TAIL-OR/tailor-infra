import os.path
import math

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class ReadData:
  def __init__(self, equipment_rates = None, staff_rates = None, consumable_rates = None):
    # If modifying these scopes, delete the file token.json.
    self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    self.spreadsheet_id = "1c75vMr_bDLexPcuf0RcBzCxH_w5XcdSAYW_SGOjHu34"
    
    self.creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("data/token.json"):
      self.creds = Credentials.from_authorized_user_file("data/token.json", self.scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not self.creds or not self.creds.valid:
      if self.creds and self.creds.expired and self.creds.refresh_token:
        self.creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "data/credentials.json", self.scopes
        )
        self.creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
      with open("data/token.json", "w") as token:
        token.write(self.creds.to_json())
      
    self.hospitals = {
      "ids": [],
      "names": {},
      "construction_costs": {},
      "lb_beds": {},
      "ub_beds": {},
      "coord_x": {},
      "coord_y": {},
      "built": {}
    }
    self.read_hospital()

    self.equipments = {
      "ids": [],
      "names": {},
      "prices": {},
      "necessary_rates": {},
      "maintenance_freqs": {},
      "maintenance_costs": {}
    }
    self.read_equipment(equipment_rates)

    self.staff = {
      "ids": [],
      "teams": {},
      "salaries": {},
      "necessary_rates": {}
    }
    self.read_staff(staff_rates)

    self.consumables = {
      "ids": [],
      "names": {},
      "prices": {},
      "necessary_rates": {}
    }
    self.read_consumable(consumable_rates)

    self.hospital_equipments = {}
    self.hospital_staff = {}
    self.hospital_consumables = {}
    for id in self.hospitals["ids"]:
      self.read_hospital_equipment(id)
      self.read_hospital_staff(id)
      self.read_hospital_consumable(id)
    
  def connect_range(self, range_name):
    try:
      service = build("sheets", "v4", credentials=self.creds)
      # Call the Sheets API
      sheet = service.spreadsheets()
      result = (
          sheet.values()
          .get(spreadsheetId=self.spreadsheet_id, range=range_name)
          .execute()
      )
      values = result.get("values", [])
      if not values:
        print("No data found.")
        return
      return values
    except HttpError as err:
      print(err)

  def read_hospital(self):
    values = self.connect_range("Hospital!A2:H")
    for row in values:
      id = int(row[0])
      self.hospitals["ids"].append(id)
      self.hospitals["names"][id] = row[1]
      self.hospitals["construction_costs"][id] = float(
        row[2].replace("R$ ", "").replace(".", "").replace(",", "."))
      self.hospitals["lb_beds"][id] = int(row[3])
      self.hospitals["ub_beds"][id] = int(row[4])
      self.hospitals["coord_x"][id] = float(row[5].replace(",", "."))
      self.hospitals["coord_y"][id] = float(row[6].replace(",", "."))
      self.hospitals["built"][id] = row[7] == "Construído"

  def read_equipment(self, equipment_rates = None):
    values = self.connect_range("Equipamento!A2:F")
    for row in values:
      id = int(row[0])
      self.equipments["ids"].append(id)
      self.equipments["names"][id] = row[1]
      self.equipments["prices"][id] = float(
        row[2].replace("R$ ", "").replace(".", "").replace(",", "."))
      if equipment_rates and id in equipment_rates.keys():
        self.equipments["necessary_rates"][id] = equipment_rates[id]
      else:
        self.equipments["necessary_rates"][id] = float(row[3])
      self.equipments["maintenance_freqs"][id] = int(row[4])
      self.equipments["maintenance_costs"][id] = float(
        row[5].replace("R$ ", "").replace(".", "").replace(",", "."))

  def read_staff(self, staff_rates = None):
    values = self.connect_range("Profissional!A2:E")
    for row in values:
      id = int(row[0])
      self.staff["ids"].append(id)
      self.staff["teams"][id] = row[1]
      self.staff["salaries"][id] = float(
        row[2].replace("R$ ", "").replace(".", "").replace(",", "."))
      if staff_rates and id in staff_rates.keys():
        self.staff["necessary_rates"][id] = math.ceil(7*24/int(row[3]))*staff_rates[id]
      else:
        self.staff["necessary_rates"][id] = math.ceil(7*24/int(row[3]))*float(row[4].replace(",", "."))

  def read_consumable(self, consumable_rates = None):
    values = self.connect_range("Insumo!A2:E")
    for row in values:
      id = int(row[0])
      self.consumables["ids"].append(id)
      self.consumables["names"][id] = row[1]
      self.consumables["prices"][id] = float(
        row[2].replace("R$ ", "").replace(".", "").replace(",", "."))
      if consumable_rates and id in consumable_rates.keys():
        self.consumables["necessary_rates"][id] = consumable_rates[id]
      else:
        self.consumables["necessary_rates"][id] = float(row[4])

  def read_hospital_equipment(self, hospital_id):
    values = self.connect_range(self.hospitals["names"][hospital_id] + " - Equipamento!A2:D")
    self.hospital_equipments[hospital_id] = {}
    for row in values:
      self.hospital_equipments[hospital_id][int(row[0])] = [int(row[2]), int(row[3])]
        # [<total quantity>, <needing maintenance>]

  def read_hospital_staff(self, hospital_id):
    values = self.connect_range(self.hospitals["names"][hospital_id] + " - Profissional!A2:C")
    self.hospital_staff[hospital_id] = {}
    for row in values:
      self.hospital_staff[hospital_id][int(row[0])] = int(row[2])
  
  def read_hospital_consumable(self, hospital_id):
    values = self.connect_range(self.hospitals["names"][hospital_id] + " - Insumo!A2:C")
    self.hospital_consumables[hospital_id] = {}
    for row in values:
      self.hospital_consumables[hospital_id][int(row[0])] = int(row[2])

  def get_hospital_ids(self):
    return self.hospitals["ids"]
  
  def get_hospital_name(self, id):
    return self.hospitals["names"][id]
  
  def get_hospital_construction_cost(self, id):
    return self.hospitals["construction_costs"][id]
  
  def get_hospital_lb_beds(self, id):
    return self.hospitals["lb_beds"][id]
  
  def get_hospital_ub_beds(self, id):
    return self.hospitals["ub_beds"][id]
  
  def get_hospital_coords(self, id):
    return self.hospitals["coord_x"][id], self.hospitals["coord_y"][id]
  
  def get_hospital_built(self, id):
    return self.hospitals["built"][id]
  
  def get_equipment_ids(self):
    return self.equipments["ids"]
  
  def get_equipment_name(self, id):
    return self.equipments["names"][id]
  
  def get_equipment_price(self, id):
    return self.equipments["prices"][id]
  
  def get_equipment_necessary_rate(self, id):
    return self.equipments["necessary_rates"][id]
  
  def get_equipment_maintenance_freq(self, id):
    return self.equipments["maintenance_freqs"][id]
  
  def get_equipment_maintenance_cost(self, id):
    return self.equipments["maintenance_costs"][id]
  
  def get_staff_ids(self):
    return self.staff["ids"]
  
  def get_staff_team(self, id):
    return self.staff["teams"][id]
  
  def get_staff_salary(self, id):
    return self.staff["salaries"][id]
  
  def get_staff_necessary_rate(self, id):
    return self.staff["necessary_rates"][id]
  
  def get_consumable_ids(self):
    return self.consumables["ids"]
  
  def get_consumable_name(self, id):
    return self.consumables["names"][id]
  
  def get_consumable_price(self, id):
    return self.consumables["prices"][id]
  
  def get_consumable_necessary_rate(self, id):
    return self.consumables["necessary_rates"][id]
  
  def get_equipment_quantity(self, hospital_id, equipment_id):
    return self.hospital_equipments[hospital_id][equipment_id][0]
  
  def get_equipment_maintenance_quantity(self, hospital_id, equipment_id):
    return self.hospital_equipments[hospital_id][equipment_id][1]
  
  def get_staff_quantity(self, hospital_id, staff_id):
    return self.hospital_staff[hospital_id][staff_id]
  
  def get_consumable_quantity(self, hospital_id, consumable_id):
    return self.hospital_consumables[hospital_id][consumable_id]
