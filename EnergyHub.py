# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 13:45:26 2019

@author: Georgios Mavromatidis (ETH Zurich, gmavroma@ethz.ch)
"""

import pyomo
import pandas as pd
import pyomo.opt
import pyomo.environ as pe

class EnergyHub:
    """This class implements a standard energy hub model for the optimal design and operation of distributed multi-energy systems"""
    
    def __init__(self, input_file, num_of_pareto_points):
        """ Read in the input data"""
        import importlib
        self.InputFile = input_file
        self.inp = importlib.import_module(self.InputFile)
        self.num_of_pfp = num_of_pareto_points
        
        self.createModel()

    
    def createModel(self):
        """Create the Pyomo energy hub model given the input data"""
       
        self.m = pe.ConcreteModel()
        
        # Model sets
        # ==========
        self.m.Time = pe.Set(initialize = self.inp.Time, doc = 'Time steps considered in the model')
        self.m.First_hour = pe.Set(initialize = self.inp.First_hour, within = self.m.Time, doc = 'The first hour of each typical day considered in the model')
        self.m.Inputs = pe.Set(initialize = self.inp.Inputs, doc = 'The energy conversion technologies of the energy hub')
        self.m.Solar_inputs = pe.Set(initialize = self.inp.Solar_inputs, within = self.m.Inputs, doc = 'Energy conversion technologies that use solar energy')
        self.m.Inputs_wo_grid = pe.Set(initialize = self.inp.Inputs_wo_grid, doc = 'Subset of input energy streams without the grid')
        self.m.Dispatchable_Tech = pe.Set(initialize = self.inp.Dispatchable_Tech, within = self.m.Inputs, doc = 'Subset for dispatchable/controllable technologies')
        self.m.CHP_Tech = pe.Set(initialize = self.inp.CHP_Tech, within = self.m.Inputs, doc = 'Subset of CHP engine technologies')
        self.m.Outputs = pe.Set(initialize = self.inp.Outputs, doc = 'Types of energy demands that the energy hub must supply')
        

        # Model parameters
        # ================
        
        # Load parameters
        # ---------------
        self.m.Loads = pe.Param(self.m.Time, self.m.Outputs, initialize = self.inp.Loads, doc = 'Time-varying energy demand patterns for the energy hub')
        self.m.Number_of_days = pe.Param(self.m.Time, initialize = self.inp.Number_of_days, doc = 'The number of days that each time step of typical day corresponds to')
        
        # Technical parameters
        # --------------------
        self.m.Cmatrix = pe.Param(self.m.Outputs, self.m.Inputs, initialize = self.inp.Cmatrix, doc = 'The coupling matrix of the energy hub')
        self.m.Storage_max_charge = pe.Param(self.m.Outputs, initialize = self.inp.Storage_max_charge, doc = 'Maximum charging rate in % of the total capacity for the storage technologies')
        self.m.Storage_max_discharge = pe.Param(self.m.Outputs, initialize = self.inp.Storage_max_discharge, doc = 'Maximum discharging rate in % of the total capacity for the storage technologies')
        self.m.Storage_standing_losses = pe.Param(self.m.Outputs, initialize = self.inp.Storage_standing_losses, doc = 'Standing losses for the storage technologies')
        self.m.Storage_charging_eff = pe.Param(self.m.Outputs, initialize = self.inp.Storage_charging_eff, doc = 'Efficiency of charging process for the storage technologies')
        self.m.Storage_discharging_eff = pe.Param(self.m.Outputs, initialize = self.inp.Storage_discharging_eff, doc = 'Efficiency of discharging process for the storage technologies')
        self.m.Storage_max_cap = pe.Param(self.m.Outputs, initialize = self.inp.Storage_max_cap, doc = 'Maximum allowable energy storage capacity per technology type')
        self.m.Lifetime_tech = pe.Param(self.m.Inputs, initialize = self.inp.Lifetime_tech, doc = 'Lifetime of energy generation technologies')
        self.m.Lifetime_stor = pe.Param(self.m.Outputs, initialize = self.inp.Lifetime_stor, doc = 'Lifetime of energy storage technologies')
        self.m.Network_efficiency = pe.Param(self.m.Outputs, initialize = self.inp.Network_efficiency, doc = 'The efficiency of the energy networks used by the energy hub')
        self.m.Network_length = pe.Param(self.m.Outputs, initialize = self.inp.Network_length, doc = 'The length of the thermal network for the energy hub')
        self.m.Network_lifetime = pe.Param(initialize = self.inp.Network_lifetime, doc = 'The lifetime of the thermal network used by the energy hub')              
                
        # Cost parameters
        # ---------------
        self.m.Operating_costs = pe.Param(self.m.Inputs, initialize = self.inp.Operating_costs, doc = 'Energy carrier costs at the input of the energy hub')
        self.m.Linear_inv_costs = pe.Param(self.m.Inputs, initialize = self.inp.Linear_inv_costs, doc = 'Linear part of the investment cost (per kW or m2) for the generation technologies in the energy hub')
        self.m.Fixed_inv_costs = pe.Param(self.m.Inputs, initialize = self.inp.Fixed_inv_costs, doc = 'Fixed part of the investment cost (per kW or m2) for the generation technologies in the energy hub')
        self.m.Linear_stor_costs = pe.Param(self.m.Outputs, initialize = self.inp.Linear_stor_costs, doc = 'Linear part of the investment cost (per kWh) for the storage technologies in the energy hub')
        self.m.Fixed_stor_costs = pe.Param(self.m.Outputs, initialize = self.inp.Fixed_stor_costs, doc = 'Fixed part of the investment cost (per kWh) for the storage technologies in the energy hub')
        self.m.Net_inv_cost_per_m = pe.Param(initialize = self.inp.Net_inv_cost_per_m, doc = 'Investment cost per pipe m of the themral network of the energy hub')
        self.m.FiT = pe.Param(self.m.Outputs, initialize = self.inp.FiT, doc = 'Feed-in tariffs for exporting electricity back to the grid')
        self.m.Interest_rate = pe.Param(initialize = self.inp.Interest_rate, doc = 'The interest rate used for the CRF calculation')
        self.m.CRF_tech = pe.Param(self.m.Inputs, doc = 'Capital Recovery Factor (CRF) used to annualise the investment cost of generation technologies')
        self.m.CRF_stor = pe.Param(self.m.Inputs, doc = 'Capital Recovery Factor (CRF) used to annualise the investment cost of storage technologies')
        self.m.CRF_network = pe.Param(doc = 'Capital Recovery Factor (CRF) used to annualise the investment cost of the networks used by the energy hub')
        
        # Environmental parameters
        # ------------------------
        self.m.Carbon_factors = pe.Param(self.m.Inputs, doc = 'Energy carrier CO2 emission factors')
        
        # Misc parameters
        # ---------------
        self.m.Roof_area = pe.Param(initialize = self.inp.Roof_area, doc = 'Available roof area for the installation of solar technologies')
        self.m.P_solar = pe.Param(self.m.Time, self.m.Solar_inputs, initialize = self.inp.P_solar, doc = 'Incoming solar radiation patterns (kWh/m2) for solar technologies')
        self.m.BigM = pe.Param(default = 10^5, doc = 'Big M: Sufficiently large value')
        
    
        # Model variables
        # ===============
        
        # Generation technologies
        # -----------------------
        self.m.P = pe.Var(self.m.Time, self.m.Inputs, within = pe.NonNegativeReals, doc = 'The input energy stream at each generation device of the energy hub at each time step')
        self.m.P_export = pe.Var(self.m.Time, self.m.Outputs, within = pe.NonNegativeReals, doc = 'Exported energy (in this case only electricity exports are allowed)')
        self.m.y = pe.Var(self.m.Inputs, within = pe.Binary, doc = 'Binary variable denoting the installation (=1) of energy generation technology')
        self.m.Capacity = pe.Var(self.m.Inputs, within = pe.NonNegativeReals, doc = 'Installed capacity for energy generation technology')
        
        # Storage technologies
        # --------------------
        self.m.Qin = pe.Var(self.m.Time, self.m.Outputs, within = pe.NonNegativeReals, doc = 'Storage charging rate')
        self.m.Qout = pe.Var(self.m.Time, self.m.Outputs, within = pe.NonNegativeReals, doc = 'Storage discharging rate')
        self.m.E = pe.Var(self.m.Time, self.m.Outputs, within = pe.NonNegativeReals, doc = 'Storage state of charge')
        self.m.y_stor = pe.Var(self.m.Outputs, within = pe.NonNegativeReals, doc = 'Binary variable denoting the installation (=1) of energy storage technology')
        self.m.Storage_cap = pe.Var(self.m.Outputs, within = pe.NonNegativeReals, doc = 'Installed capacity for energy storage technology')
        
        # Objective function components
        # -----------------------------
        self.m.Operating_cost = pe.Var(within = pe.NonNegativeReals, doc = 'The operating cost for the consumption of energy carriers')
        self.m.Income_via_exports = pe.Var(within = pe.NonNegativeReals, doc = 'Total income due to exported electricity')
        self.m.investment_cost = pe.Var(within = pe.NonNegativeReals, doc = 'Investment cost of all energy technologies in the energy hub')
        self.m.Total_cost = pe.Var(within = pe.NonNegativeReals, doc = 'Total cost for the investment and the operation of the energy hub')
        self.m.Total_carbon = pe.Var(within = pe.NonNegativeReals, doc = 'Total carbon emissions due to the operation of the energy hub')
        
        # Model constraints
        # =================
        
        # Energy balances
        # ---------------
        def Load_balance_rule (m, t, out):
            return sum(m.P[t,inp] * m.Cmatrix[out,inp] for inp in m.Inputs) + m.Qout[t,out] - m.Qin[t,out] == m.Loads[t,out] + m.P_export[t,out]
        self.m.Load_balance = pe.Constraint(self.m.Time, self.m.Outputs, rule = Load_balance_rule)
        
        def Capacity_constraint_rule(m, t, disp, out):
            return m.P[t,disp] * m.Cmatrix[out,disp] <= m.Capacity[disp]
        self.m.Capacity_constraint = pe.Constraint(self.m.Time, self.m.Dispatchable_Tech, self.m.Outputs, rule = Capacity_constraint_rule)
        
        def Solar_input_rule(m, t, sol, out):
            return m.P[t,sol] == m.P_solar[t,sol] * m.Capacity[sol]
        self.m.Solar_input = pe.Constraint(self.m.Time, self.m.Solar_inputs, self.m.Outputs, rule = Solar_input_rule)
        
        def Fixed_cost_constr_rule(m, inp):
            m.Capacity[inp] <= m.BigM * m.y[inp]
        self.m.Fixed_cost_constr = pe.Constraint(self.m.Inputs, rule = Fixed_cost_constr_rule)
        
        
        
        
    def solve(self):
        """Solve the model"""
        # solver = pyomo.opt.SolverFactory('gurobi')
        # results = solver.solve(self.m, tee=True, keepfiles=False, options_str="mip_tolerances_integrality=1e-9 mip_tolerances_mipgap=0")
        
        # if (results.solver.status != pyomo.opt.SolverStatus.ok):
            # logging.warning('Check solver not ok?')
        # if (results.solver.termination_condition != pyomo.opt.TerminationCondition.optimal):  
            # logging.warning('Check solver optimality?') 
        
if __name__ == '__main__':
       sp = EnergyHub('Firstscript', 10) 
       sp.solve()