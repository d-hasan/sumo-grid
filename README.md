# sumo-grid

A simple traffic grid simulation made to run with [SUMO](https://sumo.dlr.de/docs/) v1.1.0, installed using [flow v0.3.0](https://flow.readthedocs.io/en/latest/flow_setup.html#installing-flow-and-sumo). 

Integrates Python control of traffic lights with [TRACI](https://sumo.dlr.de/docs/TraCI.html) for basic traffic light switching based on left turn lane demand.

Dependencies are SUMO v1.1.0, which is recommended to install with the instructions for flow v0.3.0 as linked above.

Although all network and traffic data is included in the `data` folder, to regenerate the network one can run:
```
python generate_grid.py
```

To run the TRACI controller, run:
```
python traci_tls.py
```
