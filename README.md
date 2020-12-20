# csl-downtimes
Scripts and example data to accompany the paper "Understanding Unforeseen Production Downtimes in Manufacturing Processes Using Log Data-driven Causal Structure Learning"

## Setup

### Dependencies & Required Packages

To run the python scripts the following package is required:
[Pandas](https://pandas.pydata.org/pandas-docs/stable/index.html),

For the R scripts the following packages are required:
[pcalg](https://www.boost.org/)
[ParallelPC](http://arma.sourceforge.net/)
[graph](http://arma.sourceforge.net/)
[causaleffect](http://arma.sourceforge.net/)
[igraph](http://arma.sourceforge.net/)

## How To

For the transformation of log data you have to run the following command:

```sh
python log_to_obs.py
```

Note, that this script reads the data from synthetic_data.csv.
Domain knowledge in form of the aggregation functions and variable classification are specified in the dictionaries in the script.
The script already applies the discretization step.
Results are written to observations.csv and observations_disc.csv

Next the causal structures are learnt running the following command:
```sh
Rscript csl.R
```

Results are written to edges.csv and can be further processed running the command:

```sh
python domain_knowledge.py
```

Output are edges which do not correspond with the provided edge orientation rules based on the domain knowledge.

An example to calculate the formular for the application of causal effect estimation is provided in the ci.R script, based on edgeExample.csv