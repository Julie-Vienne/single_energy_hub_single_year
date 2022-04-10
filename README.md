# Simple single-stage energy hub model

## About

This repo was forked from [1].

The initial repo contains a simple implementation of a standard "energy hub" model for the optimal design and operation of a single decentralized multi-energy system (D-MES) considering also building retrofit options. 

The main addition in comparison to the upstream model is the consideration of embodied CO<sub>2</sub> emissions of both the "energy hub" and the insulation materials used for the building retrofit.

This work was part of a 3-month project during Fall 2021 with the SusTec group at ETH Zürich.

## Detailed model description

The model is formulated as a Mixed-Integer Linear Programming (MILP) model for the optimal design and operation of an energy system.

Model characteristics:

* The design is also performed in one-stage i.e. we assume that the investment in the energy system happens in one stage.
* The model considers various generation and storage technologies to compose the D-MES.
* The model is also capable of optimizing the selection of the optimal retrofit scenario for the building(s), which in turns determines the energy demands that the D-MES will need to satisfy. The retrofit scenarios are defined by the chosen insulation materials that are to be used in the building envelope.
* For simplicity reasons, advanced constraints, such as part-load efficiencies and minimum part-loads are not included.
* The model has been designed to avoid the simultaneous charging and discharging of the storage technologies.
* Single-objective (minimum cost (investment + operation), minimum CO<sub>2</sub> emissions) and multi-objective modes are included.

## Elements of the model

The main inputs required by the optimization model are the economic and environmental costs of the considered building elements:

- Environmental and economic costs of the insulation materials used for the building retrofit. These costs can be generated using [2].
- Energy demand of the buidling, which is dependent on the retrofit scenarios, i.e. the insulation material chosen. The hourly demand profiles can be generated using Energy Plus and/or the following repo: [2].
- Embodied emissions and the investment costs of the "energy hub" elements.
- Hourly carbon intensity of the electricity grid [3].
- Hourly import and export prices of the electricity grid.
- Costs and offset potential of purchasable carbon certificates.

## How to use the EnergyHub model 

### Single-objective optimization

First, import the EnergyHub class (defined in the `EnergyHub.py` file):
```
import EnergyHubRetrofit as ehr
```
Then, an `EnergyHubRetrofit` object can be defined using the following inputs:

1. A dictionary that holds all the values for the model parameters (the model formulation is decoupled from the attribution of parameter values)
2. A parameter specifying the temporal resolution of the model (1: typical days optimization, 2: full yearly horizon optimization (8760 hours), 3: typical days with continuous storage state-of-charge)
3. A parameter specifying the optimization objectives (1: total cost minimization, 2: CO<sub>2</sub> minimization)
4. A parameter specifying the number of Pareto points to be considered (only if multi-objective optimization is chosen)
  
For instance:
```python
# Create your model
mod = ehr.EnergyHubRetrofit(ehr_inp, 1, 3, 5) # Initialize the model
```
The final step is to solve the model and get the model results:
```python
# Solve the model and get the results
mod.solve()
```
The key outputs of the model are the `.xlsx` files generated for each analysed scenario in the case of a single-obective optimization.
```

## Multi-objective optimization

A similar approach as described above can be used to run a multi-objective optimization. The files used for this are `EHret_example_multi.py` and `EnergyHubRetrofit_multi.py` and the paramter specifying the optimization objective is to be set equal to 3 (multi-objective optimization).
In that case, the key outputs of the model are the `.xlsx` files generated for the number of pareto points chosen by the user. The optimization is run across all scenarios.

## Plot generation

`plot_generation.ipynb` can help generate pareto curves for the multi-objective optimization and bar plots for the single-objective optimization.

# Source

[1] Upstream repository: https://github.com/eth-sustec/single_energy_hub_single_year

[2] The model is built in Pyomo: http://pyomo.readthedocs.io

[3] Electricity map: https://electricitymap.org/
