import pyomo.environ as pyo
from .read_data import ReadData
from .predictive import Predictive

class Data:
  def __init__(self, demand = None, equipment_rates = None, staff_rates = None, consumable_rates = None):
    self.data_reader = ReadData(equipment_rates, staff_rates, consumable_rates)

    self.F = list(range(len(self.data_reader.get_hospital_ids()))) # F: set of facilities
    self.dict_hospitals = {id: iter for iter, id in enumerate(self.data_reader.get_hospital_ids())}
    
    self.K = [] # K: built facilities
    for iter, id in enumerate(self.data_reader.get_hospital_ids()):
      if(self.data_reader.get_hospital_built(id)):
        self.K.append(iter)
    
    self.dict_equipments = {iter: id for iter, id in enumerate(self.data_reader.get_equipment_ids())}
    self.R = list(range(len(self.data_reader.get_equipment_ids()))) # R: set of repairable requirements
    
    self.dict_staff = {iter + len(self.R): id for iter, id in enumerate(self.data_reader.get_staff_ids())}
    self.U = list(range(len(self.R), len(self.R) + len(self.data_reader.get_staff_ids()))) # U: set of unrepairable requirements
    
    self.dict_consumables = {iter + len(self.R) + len(self.U): id for iter, id in
      enumerate(self.data_reader.get_consumable_ids())}
    self.U += list(range(len(self.R) + len(self.U), len(self.R) + len(self.U) +
      len(self.data_reader.get_consumable_ids())))
    
    if demand:
      self.d = demand # d: demand of ICU beds
    else:
      self.d = Predictive().contamination(1, True)['demand']
    
    self.c = [] # c: cost of building facilities
    for iter, id in enumerate(self.data_reader.get_hospital_ids()):
      if id in self.K:
        self.c.append(0)
      else:
        self.c.append(self.data_reader.get_hospital_construction_cost(id))
    
    self.l = [self.data_reader.get_hospital_lb_beds(id) for id in self.data_reader.get_hospital_ids()] # l: lower bound of ICU beds in each facility, if built
    
    self.u = [self.data_reader.get_hospital_ub_beds(id) for id in self.data_reader.get_hospital_ids()] # u: upper bound of ICU beds in each facility
    
    self.p = [self.data_reader.get_equipment_price(id) for id in self.data_reader.get_equipment_ids()] # p: price of each requirement
    self.p += [self.data_reader.get_staff_salary(id) for id in self.data_reader.get_staff_ids()]
    self.p += [self.data_reader.get_consumable_price(id) for id in self.data_reader.get_consumable_ids()]
    
    self.r = [self.data_reader.get_equipment_maintenance_cost(id) for id in self.data_reader.get_equipment_ids()] # r: repair price of each repairable requirement
    
    self.n = [self.data_reader.get_equipment_necessary_rate(id) for id in self.data_reader.get_equipment_ids()] # n: necessary rate of each requirement per ICU bed
    self.n += [self.data_reader.get_staff_necessary_rate(id) for id in self.data_reader.get_staff_ids()]
    self.n += [self.data_reader.get_consumable_necessary_rate(id) for id in self.data_reader.get_consumable_ids()]
    
    self.a = [] # a: availability of each working requirement in each facility
    for iter, hospital_id in enumerate(self.data_reader.get_hospital_ids()):
      if iter in self.K:
        a_row = []
        for id in self.data_reader.get_equipment_ids():
          a_row.append(self.data_reader.get_equipment_quantity(hospital_id, id))
        for id in self.data_reader.get_staff_ids():
          a_row.append(self.data_reader.get_staff_quantity(hospital_id, id))
        for id in self.data_reader.get_consumable_ids():
          a_row.append(self.data_reader.get_consumable_quantity(hospital_id, id))
        self.a.append(a_row)
      else:
        self.a.append([0]*(len(self.R) + len(self.U)))
    
    self.m = [] # m: number of units of each repairable requirement in need of repair
    for iter, hospital_id in enumerate(self.data_reader.get_hospital_ids()):
      if iter in self.K:
        m_row = []
        for id in self.data_reader.get_equipment_ids():
          m_row.append(self.data_reader.get_equipment_maintenance_quantity(hospital_id, id))
        self.m.append(m_row)
      else:
        self.m.append([0]*len(self.R))
    
    with open('src/data/transfer_costs.txt', 'r') as file_object:
      self.t = [] # t: transfer cost of each requirement among hospitals
      for _ in self.R + self.U:
        costs_for_req_j = []
        for _ in self.F:
          costs_for_req_j.append([int(n) for n in file_object.readline().split()])
        self.t.append(costs_for_req_j)
      
  def print_data(self):
    print('F:', self.F)
    print('K:', self.K)
    print('R:', self.R)
    print('U:', self.U)
    print('d:', self.d)
    print('c:', self.c)
    print('l:', self.l)
    print('u:', self.u)
    print('p:', self.p)
    print('r:', self.r)
    print('n:', self.n)
    print('a:', self.a)
    print('m:', self.m)
    print('t:', self.t)

class Model:
  def __init__(self, data):
    # Data
    self.data = data
    self.model = pyo.ConcreteModel()
    self.model.F = self.data.F
    self.model.R = self.data.R
    self.model.U = self.data.U
    self.model.K = self.data.K

    # Variables
    self.model.x = pyo.Var(self.model.F, within=pyo.NonNegativeIntegers) # x: number of ICU beds in each facility
    self.model.y = pyo.Var(self.model.F, within=pyo.Binary) # y: whether each facility is built or not
    self.model.z = pyo.Var(self.model.F, (self.model.R + self.model.U), within=pyo.NonNegativeIntegers) # z: number of each requirement acquired by each facility
    self.model.w = pyo.Var(self.model.F, self.model.R, within=pyo.NonNegativeIntegers) # w: number of each requirement repaired in each facility
    self.model.v = pyo.Var((self.model.R + self.model.U), self.model.F, self.model.F,
      within=pyo.NonNegativeIntegers) # v: number of each requirement transferred from each facility to each facility
    
    # Objective function
    self.model.objective = pyo.Objective(expr=sum(self.data.c[i]*self.model.y[i] +
      sum(self.data.p[j]*self.model.z[i, j] + sum(self.data.t[j][i][l]*self.model.v[j, i, l]
      for l in self.model.F if l != i) for j in (self.model.R + self.model.U)) +
      sum(self.data.m[i][j]*self.model.w[i, j] for j in self.model.R) for i in self.model.F),
      sense=pyo.minimize)
    
    # Constraints
    self.model.demand_constraint = pyo.Constraint(expr=sum(self.model.x[i] for i in self.model.F) >=
      self.data.d)
    
    self.model.repairable_req_constraint = pyo.ConstraintList()
    for i in self.model.F:
      for j in self.model.R:
        self.model.repairable_req_constraint.add(self.data.a[i][j] + self.model.z[i, j] +
          self.model.w[i, j] + sum(self.model.v[j, l, i] - self.model.v[j, i, l] for l in self.model.F
          if l != i) >= self.data.n[j]*self.model.x[i])
    
    self.model.unrepairable_req_constraint = pyo.ConstraintList()
    for i in self.model.F:
      for j in self.model.U:
        self.model.unrepairable_req_constraint.add(self.data.a[i][j] + self.model.z[i, j] +
          sum(self.model.v[j, l, i] - self.model.v[j, i, l] for l in self.model.F if l != i) >=
          self.data.n[j]*self.model.x[i])
    
    self.model.repair_constraint = pyo.ConstraintList()
    for i in self.model.F:
      for j in (self.model.R):
        self.model.repair_constraint.add(self.model.w[i, j] <= self.data.m[i][j])
    
    self.model.transfer_constraint = pyo.ConstraintList()
    for j in self.model.R + self.model.U:
      for i in self.model.F:
        for l in self.model.F:
          if l != i:
            self.model.transfer_constraint.add(self.model.v[j, i, l] <= self.data.a[i][j])
    
    self.model.bed_limit_constraint = pyo.ConstraintList()
    for i in self.model.F:
      self.model.bed_limit_constraint.add(self.data.l[i]*self.model.y[i] <= self.model.x[i])
      self.model.bed_limit_constraint.add(self.model.x[i] <= self.data.u[i])
    
    self.model.y_fix_constraint = pyo.ConstraintList()
    for i in self.model.K:
      self.model.y_fix_constraint.add(self.model.y[i] == 1)
    
    self.model.y_dependent_constraint = pyo.ConstraintList()
    for i in self.model.F:
      self.model.y_dependent_constraint.add(self.model.x[i] / self.data.u[i] <= self.model.y[i])
      self.model.y_dependent_constraint.add(self.model.y[i] <= self.model.x[i])
    
    # self.model.write('model.lp', io_options={'symbolic_solver_labels': True})
    opt = pyo.SolverFactory('appsi_highs')
    self.results = opt.solve(self.model, tee=True)
    
  def print_solution(self):
    for i in self.model.F:
      if pyo.value(self.model.y[i]) > 0:
        if i not in self.model.K:
          print('Build Hospital', i)
        else:
          print('Hospital', i)
        cur_beds = min([self.data.a[i][j]/self.data.n[j] for j in self.model.R + self.model.U])
        print('\tTotal ICU beds:\t', int(pyo.value(self.model.x[i])))
        print('\tAdded ICU beds:\t', int(pyo.value(self.model.x[i]) - cur_beds))
        
        printedAcquire = False
        for j in self.model.R + self.model.U:
          if pyo.value(self.model.z[i, j]) > 0:
            if not printedAcquire:
              print('\tAcquire:')
              printedAcquire = True
            print('\t\t\t', int(pyo.value(self.model.z[i, j])), 'units of requirement', j)
        
        printedRepair = False
        for j in self.model.R:
          if pyo.value(self.model.w[i, j]) > 0:
            if not printedRepair:
              print('\tRepair:')
              printedRepair = True
            print('\t\t\t', int(pyo.value(self.model.w[i, j])), 'units of requirement', j)
        
        printedTransfer = False
        for j in self.model.R + self.model.U:
          for l in self.model.F:
            if l != i:
              if pyo.value(self.model.v[j, i, l]) > 0:
                if not printedTransfer:
                  print('\tTransfer:')
                  printedTransfer = True
                print('\t\t\t', int(pyo.value(self.model.v[j, i, l])), 'units of requirement', j,
                  'to Hospital', l)
        
        printedReceive = False
        for j in self.model.R + self.model.U:
          for l in self.model.F:
            if l != i:
              if pyo.value(self.model.v[j, l, i]) > 0:
                if not printedReceive:
                  print('\tReceive:')
                  printedReceive = True
                print('\t\t\t', int(pyo.value(self.model.v[j, l, i])), 'units of requirement', j,
                  'from Hospital', l)
  
  def to_html(self):

    budget = pyo.value(self.model.objective)
    num_hospitals = len([i for i in self.model.F if pyo.value(self.model.y[i]) > 0])
    added_beds = sum([int(pyo.value(self.model.x[i]) - min([self.data.a[i][j]/self.data.n[j]
      for j in self.model.R + self.model.U])) for i in self.model.F if pyo.value(self.model.y[i]) > 0])
    
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Administra&ccedil;&atilde;o de leitos</title>
<style>
body {
  font-family: 'Helvetica', sans-serif;
  color: #707070;
  background-color: #f2f2f2;
  margin: 0;
  padding: 0;
}

.header {
  background-color: #16497F;
  color: #fff;
  width: 100%;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.title {
  font-size: 22px;
  font-weight: bold;
  text-align: center;
}

.subtitle {
  margin: 30px 20px 0px 20px;
  font-size: 20px;
  font-weight: bold;
  color: #505050;
}

.hospital-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  margin: 20px;
}

.hospital-box {
  width: calc(28%);
  margin: 10px;
  padding: 10px;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0,0,0,0.3);
  background-color: #ffffff;
}

.clear-box {
  padding: 5px;
}

.content {
  font-size: 14px;
  font-weight: normal;
}

.image-box {
  width: calc(20%);
  margin: 10px;
  padding: 10px;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0,0,0,0.3);
  background-color: #16497F; /* Blue color */
  color: #fff;
  text-align: center;
}

.image-box img {
  height: 70px;
  display: block;
  margin: 0 auto 10px; /* Center the image */
}

.image-box p {
  margin: 0; /* Remove default margin */
}

.footer-box {
  width: 100%;
  padding: 10px;
  text-align: center;
}

.footer-box img {
  margin: 0px calc(3%);
  height: 60px;
}

</style>
</head>
<body>
<div class="header title">
  Prescri&ccedil;&atilde;o de administra&ccedil;&atilde;o de leitos de UTI
</div>
<div class="subtitle">
  <p>Informa&ccedil;&otilde;es gerais</p>
</div>
<div class="hospital-container">
  <div class="image-box">
    <img src="figures/coins.png" alt="Stack of coins">
    <div class="content">Or&ccedil;amento previsto</div>
    <div class="content"> R$ """
    budget_str = str(f'{budget:,}').replace('.', ',')
    html_content += budget_str.replace(',', '.', budget_str.count(',') - 1) + """ </div>
    </div>
    <div class="image-box">
      <img src="figures/hospital.png" alt="Hospital">
      <div class="content">Hospitais beneficiados</div> 
      <div class="content"> {} </div>
    </div>""".format(num_hospitals)
    html_content += """
    <div class="image-box">
      <img src="figures/hospital_bed.png" alt="Hospital beds">
      <div class="content">Leitos adicionados</div>
      <div class="content"> {} </div>
    </div>
</div>
<div class="subtitle">
  <p>A&ccedil;&otilde;es prescritas</p>
</div>
<div class="hospital-container">""".format(added_beds)

    # Add section for hospitals information
    for i in self.model.F:
      if pyo.value(self.model.y[i]) > 0:
        html_content += """
<div class="hospital-box">
  <div class="clear-box">
    <strong> {} </strong>""".format(self.data.data_reader.get_hospital_name(
      self.data.dict_hospitals[i]
    ))

        if i not in self.model.K:
          construction_cost_str = str(f'{self.data.c[i]:,}').replace('.', ',')
          html_content += """
    <div class="clear-box content">
        <strong> Construção: </strong> R$ {}
    </div>""".format(construction_cost_str.replace(',', '.', construction_cost_str.count(',') - 1))

        cur_beds = min([self.data.a[i][j] / self.data.n[j] for j in self.model.R + self.model.U])
        html_content += """
    <div class="clear-box content">
      <strong> Leitos de UTI totais: </strong> {}
    </div>
    <div class="clear-box content">
      <strong> Leitos de UTI adicionados: </strong> {}
    </div>""".format(int(pyo.value(self.model.x[i])), int(pyo.value(self.model.x[i]) - cur_beds))

        printedAcquire = False
        for j in self.model.R + self.model.U:
          if pyo.value(self.model.z[i, j]) > 0:
            if not printedAcquire:
              html_content += """
    <div class="clear-box content">
      <strong> Adquirir: </strong>"""
              printedAcquire = True
            req_name_str = ""
            if j in self.data.dict_equipments.keys():
              if pyo.value(self.model.z[i, j]) > 1:
                req_name_str = "unidades"
              else:
                req_name_str = "unidade"
              req_name_str += " de " + self.data.data_reader.get_equipment_name(
                self.data.dict_equipments[j])
            elif j in self.data.dict_staff.keys():
              if pyo.value(self.model.z[i, j]) > 1:
                req_name_str = "profissionais"
              else:
                req_name_str = "profissional"
              req_name_str += " para o time " + self.data.data_reader.get_staff_team(
                self.data.dict_staff[j])
            elif j in self.data.dict_consumables.keys():
              if pyo.value(self.model.z[i, j]) > 1:
                req_name_str = "unidades"
              else:
                req_name_str = "unidade"
              req_name_str += " de " + self.data.data_reader.get_consumable_name(
                self.data.dict_consumables[j])
            html_content += """
    <div class="clear-box content">
      {} {}
    </div>""".format(int(pyo.value(self.model.z[i, j])), req_name_str)
        if printedAcquire:
          html_content += """
</div>"""

        printedRepair = False
        for j in self.model.R:
          if pyo.value(self.model.w[i, j]) > 0:
            if not printedRepair:
              html_content += """
<div class="clear-box content">
    <strong> Reparar: </strong>"""
              printedRepair = True
            req_name_str = ""
            if j in self.data.dict_equipments.keys():
              if pyo.value(self.model.w[i, j]) > 1:
                req_name_str = "unidades"
              else:
                req_name_str = "unidade"
              req_name_str += " de " + self.data.data_reader.get_equipment_name(
                self.data.dict_equipments[j])
            html_content += """
<div class="clear-box content">
    {} {}
</div>""".format(int(pyo.value(self.model.w[i, j])), req_name_str)
        if printedRepair:
          html_content += """
</div>"""

        printedTransfer = False
        for j in self.model.R + self.model.U:
          for l in self.model.F:
            if l != i:
              if pyo.value(self.model.v[j, i, l]) > 0:
                if not printedTransfer:
                  html_content += """
<div class="clear-box content">
    <strong> Transferir: </strong>"""
                  printedTransfer = True
                if j in self.data.dict_equipments.keys():
                  if pyo.value(self.model.v[j, i, l]) > 1:
                    req_name_str = "unidades"
                  else:
                    req_name_str = "unidade"
                  req_name_str += " de " + self.data.data_reader.get_equipment_name(
                    self.data.dict_equipments[j])
                elif j in self.data.dict_staff.keys():
                  if pyo.value(self.model.v[j, i, l]) > 1:
                    req_name_str = "profissionais"
                  else:
                    req_name_str = "profissional"
                  req_name_str += " do time " + self.data.data_reader.get_staff_team(
                    self.data.dict_staff[j])
                elif j in self.data.dict_consumables.keys():
                  if pyo.value(self.model.v[j, i, l]) > 1:
                    req_name_str = "unidades"
                  else:
                    req_name_str = "unidade"
                  req_name_str += " de " + self.data.data_reader.get_consumable_name(
                    self.data.dict_consumables[j])
                html_content += """
<div class="clear-box content">
    {} {} ao {}
</div>""".format(int(pyo.value(self.model.v[j, i, l])), req_name_str,
  self.data.data_reader.get_hospital_name(self.data.dict_hospitals[l]))
        if printedTransfer:
          html_content += """
</div>"""

        printedReceive = False
        for j in self.model.R + self.model.U:
          for l in self.model.F:
            if l != i:
              if pyo.value(self.model.v[j, l, i]) > 0:
                if not printedReceive:
                  html_content += """
<div class="clear-box content">
    <strong> Receber: </strong>"""
                  printedReceive = True
                if j in self.data.dict_equipments.keys():
                  if pyo.value(self.model.v[j, l, i]) > 1:
                    req_name_str = "unidades"
                  else:
                    req_name_str = "unidade"
                  req_name_str += " de " + self.data.data_reader.get_equipment_name(
                    self.data.dict_equipments[j])
                elif j in self.data.dict_staff.keys():
                  if pyo.value(self.model.v[j, l, i]) > 1:
                    req_name_str = "profissionais"
                  else:
                    req_name_str = "profissional"
                  req_name_str += " do time " + self.data.data_reader.get_staff_team(
                    self.data.dict_staff[j])
                elif j in self.data.dict_consumables.keys():
                  if pyo.value(self.model.v[j, l, i]) > 1:
                    req_name_str = "unidades"
                  else:
                    req_name_str = "unidade"
                  req_name_str += " de " + self.data.data_reader.get_consumable_name(
                    self.data.dict_consumables[j])
                html_content += """
<div class="clear-box content">
    {} {} do {}
</div>""".format(int(pyo.value(self.model.v[j, l, i])), req_name_str,
  self.data.data_reader.get_hospital_name(self.data.dict_hospitals[l]))
        if printedReceive:
          html_content += """
</div>"""

        html_content += """
</div>
</div>"""

    html_content += """
</div>
</body>
<hr color=#e9e9e9>
<footer>
<div class="footer-box">
    <img src="figures/sus.png" alt="SUS">
    <img src="figures/logo_20_years.png" alt="20 years">
    <img src="figures/footer.png" alt="Footer">
</div>
</footer>
</html>"""
    return html_content
  
def run_model(demand = None, equipment_rates = None, staff_rates = None, consumable_rates = None):
  model = Model(Data(demand, equipment_rates, staff_rates, consumable_rates))
  with open('output.html', 'w') as file:
    html = model.to_html()
    file.write(model.to_html())
  return html
