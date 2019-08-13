# Simple single-stage energy hub model

## About

This repository contains a simple implementation of a standard "energy hub" model for the optimal design and operation of a single distributed multi-energy system.

The model is built in Pyomo (http://pyomo.readthedocs.io).

## Detailed model description



The design is also performed in one-stage i.e. we assume that the investment in the energy system happens in one stage.

The model follows previous formulations of energy hub models and is a Mixed-Integer Linear Program.

The formulation of the MILP model itself is kept by choice rather simple and advanced constraints, such as part-load efficiencies and minimum part-loads have not been considered in order to keep the computational requirements of the model low.

## How to use the EnergyHub model:

```
import EnergyHub as eh

# Create your model
mod = eh.EnergyHub('Input_data', 3, 5)

# Solve the model and get the results
(obj, dsgn, oper) = mod.solve()
```
