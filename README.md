# CollectiveHLS: A Collaborative Approach to High-Level Synthesis Design Optimization

This repository hosts CollectiveHLS, an ultra-fast, knowledge-driven approach for optimizing FPGA designs through High-Level Synthesis (HLS). CollectiveHLS relies on two additional projects: [HLSAnalysisTools](https://github.com/aferikoglou/HLSAnalysisTools), which generates a feature vector from the original source code of the target application, and [GenHLSOptimizer](https://github.com/aferikoglou/GenHLSOptimizer), which collects design latency (in milliseconds) along with BRAM%, DSP%, FF%, and LUT% utilization for various directive combinations on a specific FPGA at a target frequency. CollectiveHLS utilizes applications from [Machsuite](https://github.com/breagen/MachSuite), [RodiniaHLS](https://github.com/SFU-HiAccel/rodinia-hls), [Rosetta](https://github.com/cornell-zhang/rosetta), and various publicly available GitHub repositories. It targets the AMD UltraScale+ MPSoC ZCU104 FPGA, operating at a clock frequency of 300MHz. 
* To apply CollectiveHLS to unseen applications, you must first use [HLSAnalysisTools](https://github.com/aferikoglou/HLSAnalysisTools) to extract the necessary source code information and generate the source code feature vector as detailed in the original manuscript.
* To expand CollectiveHLS' knowledge base, you will also need to use [GenHLSOptimizer](https://github.com/aferikoglou/GenHLSOptimizer) to build the Quality of Result (QoR) metrics database and identify the Pareto frontier of the designs.

This repository contains the source code for the core components of CollectiveHLS and provides the means to reproduce the results of the Leave-One-Out (LOT) experiment detailed in the original manuscript.

## Getting Started

These instructions will get you a copy of the project on your local machine.

### Prerequisites

This project was tested on Ubuntu 20.04 LTS (GNU/Linux 5.4.0-187-generic x86_64) with Python 3.8.10 and Vitis 2022.1 suite installed. 

In addition, the following libraries are needed:

* [psutil](https://pypi.org/project/psutil/) (5.9.2)
* [paretoset](https://pypi.org/project/paretoset/) (1.2.3)
* [numpy](https://pypi.org/project/numpy/) (1.23.2)
* [pandas](https://pypi.org/project/pandas/) (1.4.3)
* [matplotlib](https://pypi.org/project/matplotlib/) (3.5.3)
* [seaborn](https://pypi.org/project/seaborn/) (0.12.0)
* [scikit-learn](https://pypi.org/project/scikit-learn/) (1.1.2)

which can be simply installed using the following command.

```bash
python3 -m pip install -r requirements.txt
```

### Run

After downloading the software in the *Prerequisites* section you can clone this repository on your local machine.

**Execute the Leave-One-Out Experiment**

```bash
python3 executeExperiment.py --EVAL_MODE LOT --SYNTHESIZE True
```

## Publication

In case you use some of the code please cite the following paper:

```
@ARTICLE{10310220,
  author   = {Ferikoglou, Aggelos and Kakolyris, Andreas and Kypriotis, Vasilis and Masouros, Dimosthenis and Soudris, Dimitrios and Xydis, Sotirios},
  journal  = {IEEE Embedded Systems Letters}, 
  title    = {CollectiveHLS: Ultrafast Knowledge-Based HLS Design Optimization}, 
  year     = {2024},
  volume   = {16},
  number   = {2},
  pages    = {235-238},
  keywords = {Source coding;Optimization;Knowledge based systems;Field programmable gate arrays;Measurement;Sociology;Pareto optimization;Collective;data-driven;design space exploration (DSE);field programmable gate array (FPGA);high-level synthesis (HLS)},
  doi      = {10.1109/LES.2023.3330610}
}
```
