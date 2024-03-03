import pyomo.environ as pyo

class Data:
  def __init__(self, filename):
    with open(filename) as file_object:
      self.F = list(range(int(file_object.readline()))) # F: set of facilities
      self.K = [int(n) for n in file_object.readline().split()] # K: built facilities
      n_req = 0
      req = []
      for n in file_object.readline().split():
        req.append(list(range(n_req, n_req + int(n))))
        n_req += int(n)
      self.E, self.I, self.S = req # E: set of equipments; I: set of infrastructure; S: set of staff
      self.d = int(file_object.readline()) # d: demand of ICU beds
      self.c = [] # c: cost of building facilities
      for i, n in enumerate(file_object.readline().split()):
        if i in self.K:
          self.c.append(0)
        else:
          self.c.append(float(n))
      self.l = [int(n) for n in file_object.readline().split()] # l: lower bound of ICU beds in each facility, if built
      self.u = [int(n) for n in file_object.readline().split()] # u: upper bound of ICU beds in each facility
      self.p = [float(n) for n in file_object.readline().split()] # p: price of each requirement
      self.r = [float(n) for n in file_object.readline().split()] # r: repair price of each requirement (equipments and infrastructure)
      self.n = [float(n) for n in file_object.readline().split()] # n: necessary rate of each requirement per ICU bed
      self.a = [] # a: availability of each working requirement in each facility
      for i in self.F:
        if i in self.K:
          self.a.append([int(n) for n in file_object.readline().split()])
        else:
          self.a.append([0]*len(self.E + self.I + self.S))
      self.m = [] # m: number of units of each requirement in need of repair
      for i in self.F:
        if i in self.K:
          self.m.append([int(n) for n in file_object.readline().split()])
        else:
          self.m.append([0]*len(self.E + self.I))
      self.t = [] # t: transfer cost of each requirement among hospitals
      for _ in self.E:
        costs_for_req_j = []
        for _ in self.F:
          costs_for_req_j.append([int(n) for n in file_object.readline().split()])
        self.t.append(costs_for_req_j)
      for _ in self.I:
        self.t.append(None)
      for _ in self.S:
        costs_for_req_j = []
        for _ in self.F:
          costs_for_req_j.append([int(n) for n in file_object.readline().split()])
        self.t.append(costs_for_req_j)

  def print_data(self):
    print('F:', self.F)
    print('K:', self.K)
    print('E:', self.E)
    print('I:', self.I)
    print('S:', self.S)
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
    self.model.E = self.data.E
    self.model.I = self.data.I
    self.model.S = self.data.S
    self.model.K = self.data.K

    # Variables
    self.model.x = pyo.Var(self.model.F, within=pyo.NonNegativeIntegers) # x: number of ICU beds in each facility
    self.model.y = pyo.Var(self.model.F, within=pyo.Binary) # y: whether each facility is built or not
    self.model.z = pyo.Var(self.model.F, (self.model.E + self.model.I + self.model.S),
      within=pyo.NonNegativeIntegers) # z: number of each requirement acquired by each facility
    self.model.w = pyo.Var(self.model.F, (self.model.E + self.model.I), within=pyo.NonNegativeIntegers) # w: number of each requirement repaired in each facility
    self.model.v = pyo.Var((self.model.E + self.model.S), self.model.F, self.model.F,
      within=pyo.NonNegativeIntegers) # v: number of each requirement transferred from each facility to each facility
    
    # Objective function
    self.model.objective = pyo.Objective(expr=sum(self.data.c[i]*self.model.y[i] +
        sum(self.data.p[j]*self.model.z[i, j] for j in (self.model.E + self.model.I + self.model.S)) +
        sum(self.data.m[i][j]*self.model.w[i, j] for j in (self.model.E + self.model.I)) +
        sum(sum(self.data.t[j][i][l]*self.model.v[j, i, l] for l in self.model.F if l != i)
        for j in (self.model.E + self.model.S)) for i in self.model.F), sense=pyo.minimize)
    
    # Constraints
    self.model.demand_constraint = pyo.Constraint(expr=sum(self.model.x[i] for i in self.model.F) >=
      self.data.d)
    self.model.equipment_constraint = pyo.ConstraintList()
    for i in self.model.F:
      for j in self.model.E:
        self.model.equipment_constraint.add(self.data.a[i][j] + self.model.z[i, j] +
          self.model.w[i, j] + sum(self.model.v[j, l, i] - self.model.v[j, i, l] for l in self.model.F
          if l != i) >= self.data.n[j]*self.model.x[i])
    self.model.infrastructure_constraint = pyo.ConstraintList()
    for i in self.model.F:
      for j in self.model.I:
        self.model.infrastructure_constraint.add(self.data.a[i][j] + self.model.z[i, j] +
          self.model.w[i, j] >= self.data.n[j]*self.model.x[i])
    self.model.staff_constraint = pyo.ConstraintList()
    for i in self.model.F:
      for j in self.model.S:
        self.model.staff_constraint.add(self.data.a[i][j] + self.model.z[i, j] +
          sum(self.model.v[j, l, i] - self.model.v[j, i, l] for l in self.model.F if l != i) >=
          self.data.n[j]*self.model.x[i])
    self.model.repair_constraint = pyo.ConstraintList()
    for i in self.model.F:
      for j in (self.model.E + self.model.I):
        self.model.repair_constraint.add(self.model.w[i, j] <= self.data.m[i][j])
    self.model.transfer_constraint = pyo.ConstraintList()
    for j in self.model.E:
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
    
    self.model.write('model.lp', io_options={'symbolic_solver_labels': True})
    opt = pyo.SolverFactory('appsi_highs')
    self.results = opt.solve(self.model, tee=True)
    
  def print_solution(self):
    for i in self.model.F:
      if pyo.value(self.model.y[i]) > 0:
        if i not in self.model.K:
          print('Build Hospital', i)
        else:
          print('Hospital', i)
        cur_beds = min([self.data.a[i][j]/self.data.n[j] for j in self.model.E + self.model.I +
          self.model.S])
        print('\tTotal ICU beds:\t', int(pyo.value(self.model.x[i])))
        print('\tAdded ICU beds:\t', int(pyo.value(self.model.x[i]) - cur_beds))
        
        printedAcquire = False
        for j in self.model.E:
          if pyo.value(self.model.z[i, j]) > 0:
            if not printedAcquire:
              print('\tAcquire:')
              printedAcquire = True
            print('\t\t\t', int(pyo.value(self.model.z[i, j])), 'units of equipment', j)
        for j in self.model.I:
          if pyo.value(self.model.z[i, j]) > 0:
            if not printedAcquire:
              print('\tAcquire:')
              printedAcquire = True
            print('\t\t\t', int(pyo.value(self.model.z[i, j])), 'units of infrastructure', j)
        for j in self.model.S:
          if pyo.value(self.model.z[i, j]) > 0:
            if not printedAcquire:
              print('\tAcquire:')
              printedAcquire = True
            print('\t\t\t', int(pyo.value(self.model.z[i, j])), 'professionals to staff', j)

        printedRepair = False
        for j in self.model.E:
          if pyo.value(self.model.w[i, j]) > 0:
            if not printedRepair:
              print('\tRepair:')
              printedRepair = True
            print('\t\t\t', int(pyo.value(self.model.w[i, j])), 'units of equipment', j)
        for j in self.model.I:
          if pyo.value(self.model.w[i, j]) > 0:
            if not printedRepair:
              print('\tRepair:')
              printedRepair = True
            print('\t\t\t', int(pyo.value(self.model.w[i, j])), 'units of infrastructure', j)
        
        printedTransfer = False
        for j in self.model.E:
          for l in self.model.F:
            if l != i:
              if pyo.value(self.model.v[j, i, l]) > 0:
                if not printedTransfer:
                  print('\tTransfer:')
                  printedTransfer = True
                print('\t\t\t', int(pyo.value(self.model.v[j, i, l])), 'units of equipment', j,
                  'to Hospital', l)
        for j in self.model.S:
          for l in self.model.F:
            if l != i:
              if pyo.value(self.model.v[j, i, l]) > 0:
                if not printedTransfer:
                  print('\tTransfer:')
                  printedTransfer = True
                print('\t\t\t', int(pyo.value(self.model.v[j, i, l])), 'professionals of staff', j,
                  'to Hospital', l)
        
        printedReceive = False
        for j in self.model.E:
          for l in self.model.F:
            if l != i:
              if pyo.value(self.model.v[j, l, i]) > 0:
                if not printedReceive:
                  print('\tReceive:')
                  printedReceive = True
                print('\t\t\t', int(pyo.value(self.model.v[j, l, i])), 'units of equipment', j,
                  'from Hospital', l)
        for j in self.model.S:
          for l in self.model.F:
            if l != i:
              if pyo.value(self.model.v[j, l, i]) > 0:
                if not printedReceive:
                  print('\tReceive:')
                  printedReceive = True
                print('\t\t\t', int(pyo.value(self.model.v[j, l, i])), 'professionals of staff', j,
                  'from Hospital', l)
  
  def to_html(self):

    budget = pyo.value(self.model.objective)
    num_hospitals = len([i for i in self.model.F if pyo.value(self.model.y[i]) > 0])
    added_beds = sum([int(pyo.value(self.model.x[i]) - min([self.data.a[i][j]/self.data.n[j]
      for j in self.model.E + self.model.I + self.model.S])) for i in self.model.F if
      pyo.value(self.model.y[i]) > 0])
    
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
<div class="hospital-container">
""".format(added_beds)

    # Add section for hospitals information
    for i in self.model.F:
        if pyo.value(self.model.y[i]) > 0:
            html_content += """
<div class="hospital-box">
    <div class="clear-box">
        <strong> Hospital {} </strong> 
""".format(i)

            if i not in self.model.K:
                html_content += """
        <div class="clear-box content">
            <strong> Construção: </strong> {}
        </div>
        """.format(self.data.c[i])

            cur_beds = min([self.data.a[i][j] / self.data.n[j] for j in self.model.E + self.model.I +
                            self.model.S])
            html_content += """
        <div class="clear-box content">
            <strong> Leitos de UTI totais: </strong> {}
        </div>
        <div class="clear-box content">
            <strong> Leitos de UTI adicionados: </strong> {}
        </div>
    """.format(int(pyo.value(self.model.x[i])), int(pyo.value(self.model.x[i]) - cur_beds))

            printedAcquire = False
            for j in self.model.E:
                if pyo.value(self.model.z[i, j]) > 0:
                    if not printedAcquire:
                        html_content += """
        <div class="clear-box content">
            <strong> Adquirir: </strong>
        """
                        printedAcquire = True
                    html_content += """
        <div class="clear-box content">
            {} unidades do equipamento {}
        </div>
        """.format(int(pyo.value(self.model.z[i, j])), j)

            for j in self.model.I:
                if pyo.value(self.model.z[i, j]) > 0:
                    if not printedAcquire:
                        html_content += """
        <div class="clear-box content">
            <strong> Adquirir: </strong>
        """
                        printedAcquire = True
                    html_content += """
        <div class="clear-box content">
            {} unidades da infraestrutura {}
        </div>
        """.format(int(pyo.value(self.model.z[i, j])), j)

            for j in self.model.S:
                if pyo.value(self.model.z[i, j]) > 0:
                    if not printedAcquire:
                        html_content += """
        <div class="clear-box content">
            <strong> Adquirir: </strong>
        """
                        printedAcquire = True
                    html_content += """
        <div class="clear-box content">
            {} profissionais para o time {}
        </div>
        """.format(int(pyo.value(self.model.z[i, j])), j)

            if printedAcquire:
                html_content += """
    </div>
"""

            printedRepair = False
            for j in self.model.E:
                if pyo.value(self.model.w[i, j]) > 0:
                    if not printedRepair:
                        html_content += """
    <div class="clear-box content">
        <strong> Reparar: </strong>
    """
                        printedRepair = True
                    html_content += """
    <div class="clear-box content">
        {} unidades do equipamento {}
    </div>
    """.format(int(pyo.value(self.model.w[i, j])), j)

            for j in self.model.I:
                if pyo.value(self.model.w[i, j]) > 0:
                    if not printedRepair:
                        html_content += """
    <div class="clear-box content">
        <strong> Reparar: </strong>
    """
                        printedRepair = True
                    html_content += """
    <div class="clear-box content">
        {} unidades da infraestrutura {}
    </div>
    """.format(int(pyo.value(self.model.w[i, j])), j)

            if printedRepair:
                html_content += """
    </div>
"""

            printedTransfer = False
            for j in self.model.E:
                for l in self.model.F:
                    if l != i:
                        if pyo.value(self.model.v[j, i, l]) > 0:
                            if not printedTransfer:
                                html_content += """
    <div class="clear-box content">
        <strong> Transferir: </strong>
    """
                                printedTransfer = True
                            html_content += """
    <div class="clear-box content">
        {} unidades do equipamento {} ao Hospital {}
    </div>
    """.format(int(pyo.value(self.model.v[j, i, l])), j, l)

            for j in self.model.S:
                for l in self.model.F:
                    if l != i:
                        if pyo.value(self.model.v[j, i, l]) > 0:
                            if not printedTransfer:
                                html_content += """
    <div class="clear-box content">
        <strong> Transferir: </strong>
    """
                                printedTransfer = True
                            html_content += """
    <div class="clear-box content">
        {} profissionais para o time {} do Hospital {}
    </div>
    """.format(int(pyo.value(self.model.v[j, i, l])), j, l)

            if printedTransfer:
                html_content += """
    </div>
"""

            printedReceive = False
            for j in self.model.E:
                for l in self.model.F:
                    if l != i:
                        if pyo.value(self.model.v[j, l, i]) > 0:
                            if not printedReceive:
                                html_content += """
    <div class="clear-box content">
        <strong> Receber: </strong>
    """
                                printedReceive = True
                            html_content += """
    <div class="clear-box content">
        {} unidades do equipamento {} do Hospital {}
    </div>
    """.format(int(pyo.value(self.model.v[j, l, i])), j, l)

            for j in self.model.S:
                for l in self.model.F:
                    if l != i:
                        if pyo.value(self.model.v[j, l, i]) > 0:
                            if not printedReceive:
                                html_content += """
    <div class="clear-box content">
        <strong> Receber: </strong>
    """
                                printedReceive = True
                            html_content += """
    <div class="clear-box content">
        {} profissionais do time {} do Hospital {}
    </div>
    """.format(int(pyo.value(self.model.v[j, l, i])), j, l)

            if printedReceive:
                html_content += """
    </div>
"""

            html_content += """
</div>
</div>
"""

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
</html>
"""
    return html_content
  
model = Model(Data('instances/mock.txt'))
model.print_solution()
with open('output.html', 'w') as file:
  file.write(model.to_html())
