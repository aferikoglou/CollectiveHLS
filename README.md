# CollectiveHLS: A Collaborative Approach to High-Level Synthesis Design Optimization

This repository hosts CollectiveHLS, an ultra-fast, knowledge-driven approach for optimizing FPGA designs through High-Level Synthesis (HLS). CollectiveHLS relies on two additional projects: [HLSAnalysisTools](https://github.com/aferikoglou/HLSAnalysisTools), which generates a feature vector from the original source code of the target application, and [GenHLSOptimizer](https://github.com/aferikoglou/GenHLSOptimizer), which collects design latency (in milliseconds) along with BRAM%, DSP%, FF%, and LUT% utilization for various directive combinations on a specific FPGA at a target frequency. CollectiveHLS utilizes applications from [Machsuite](https://github.com/breagen/MachSuite), [RodiniaHLS](https://github.com/SFU-HiAccel/rodinia-hls), and various publicly available GitHub repositories. It targets the AMD UltraScale+ MPSoC ZCU104 FPGA, operating at a clock frequency of 300MHz. 
* To apply CollectiveHLS to unseen applications, you must first use [HLSAnalysisTools](https://github.com/aferikoglou/HLSAnalysisTools) to extract the necessary source code information and generate the source code feature vector as detailed in the original manuscript.
* To expand CollectiveHLS' knowledge base, you will also need to use [GenHLSOptimizer](https://github.com/aferikoglou/GenHLSOptimizer) to build the Quality of Result (QoR) metrics database and identify the Pareto frontier of the designs.

This repository contains the source code for the core components of CollectiveHLS and offers a brief demo showcasing its basic functionalities using two applications: the [KNN Pipeline](https://github.com/SFU-HiAccel/rodinia-hls/tree/master/Benchmarks/knn/knn_2_pipeline) from RodiniaHLS and [GEMM NCubed](https://github.com/breagen/MachSuite/tree/master/gemm/ncubed) from Machsuite.

## Getting Started

These instructions will get you a copy of the project on your local machine.

### Prerequisites

This project was tested on Ubuntu 20.04 LTS (GNU/Linux 5.4.0-187-generic x86_64) with Python 3.8.10 and Vitis 2022.1 suite installed. 

In addition, the following libraries are needed:

* [psutil](https://pypi.org/project/psutil/) (5.9.2)
* [numpy](https://pypi.org/project/numpy/) (1.23.2)
* [pandas](https://pypi.org/project/pandas/) (1.4.3)
* [seaborn](https://pypi.org/project/seaborn/) (0.12.0)
* [matplotlib](https://pypi.org/project/matplotlib/) (3.5.3)
* [scikit-learn](https://pypi.org/project/scikit-learn/) (1.1.2)

which can be simply installed using the following command.

```bash
python3 -m pip install -r requirements.txt
```

### Run

After downloading the software in the *Prerequisites* section you can clone this repository on your local machine.

**Optimize Application with CollectiveHLS**

```bash
python3 CollectiveHLS.py --APPLICATION_TO_BE_OPTIMIZED <ApplicationName>
```

**Example 1: Optimize the KNN Pipeline from RodiniaHLS using CollectiveHLS**

```bash
python3 CollectiveHLS.py --APPLICATION_TO_BE_OPTIMIZED RodiniaHLS-KNN-Pipeline

Output

*******************************************************
*                   CollectiveHLS                     *
*******************************************************
* Number of PCs         = 3
* Number of Clusters    = 5
* Probability Threshold = 0.1
* VitisHLS Opt.         = False
* Re-propose Directives = False
* FPGA Id               = xczu7ev-ffvc1156-2-e
* Target Clock Period   = 3.33
*******************************************************
* Optimized App. = RodiniaHLS-KNN-Pipeline
*******************************************************
* Design Latency = 10.69353243 msec
* BRAM %         = 0 %
* DSP %          = 58 %
* FF %           = 46 %
* LUT %          = 82 %
* Synthesis Time = 691.6875653266907 sec
*******************************************************


```

**Example 2: Optimize the GEMM NCubed application from Machsuite using CollectiveHLS, ensuring that the re-propose directives feature is disabled**

```bash
python3 CollectiveHLS.py --APPLICATION_TO_BE_OPTIMIZED Machsuite-GEMM-NCubed --REPROPOSE_DIRECTIVES False

Output

*******************************************************
*                   CollectiveHLS                     *
*******************************************************
* Number of PCs         = 3
* Number of Clusters    = 5
* Probability Threshold = 0.1
* VitisHLS Opt.         = False
* Re-propose Directives = False
* FPGA Id               = xczu7ev-ffvc1156-2-e
* Target Clock Period   = 3.33
*******************************************************
* Optimized App. = Machsuite-GEMM-NCubed
*******************************************************
* Design Latency = 0.01646019 msec
* BRAM %         = 0 %
* DSP %          = 22 %
* FF %           = 354 %
* LUT %          = 262 %
* Synthesis Time = 1081.106892824173 sec
* The design proposed by CollectiveHLS was synthesizable but not feasible.
*******************************************************


```

**Example 3: Optimize the GEMM NCubed application from Machsuite using CollectiveHLS, ensuring that the re-propose directives feature is enabled**


```bash
python3 CollectiveHLS.py --APPLICATION_TO_BE_OPTIMIZED Machsuite-GEMM-NCubed --REPROPOSE_DIRECTIVES True

Output

*******************************************************
*                   CollectiveHLS                     *
*******************************************************
* Number of PCs         = 3
* Number of Clusters    = 5
* Probability Threshold = 0.1
* VitisHLS Opt.         = False
* Re-propose Directives = True
* FPGA Id               = xczu7ev-ffvc1156-2-e
* Target Clock Period   = 3.33
*******************************************************
* Optimized App. = Machsuite-GEMM-NCubed
*******************************************************
* Design Latency = 0.01646019 msec
* BRAM %         = 0 %
* DSP %          = 22 %
* FF %           = 354 %
* LUT %          = 262 %
* Synthesis Time = 1080.2370615005493 sec
* The design proposed by CollectiveHLS was synthesizable but not feasible.
*******************************************************

# Re-propose Directives Iteration 1

*******************************************************
*                   CollectiveHLS                     *
*******************************************************
* Number of PCs         = 3
* Number of Clusters    = 5
* Probability Threshold = 0.1
* VitisHLS Opt.         = False
* Re-propose Directives = True
* FPGA Id               = xczu7ev-ffvc1156-2-e
* Target Clock Period   = 3.33
*******************************************************
* Optimized App. = Machsuite-GEMM-NCubed
*******************************************************
* Design Latency = 0.01646019 msec
* BRAM %         = 0 %
* DSP %          = 22 %
* FF %           = 354 %
* LUT %          = 262 %
* Synthesis Time = 1107.0174641609192 sec
* The design proposed by CollectiveHLS was synthesizable but not feasible.
*******************************************************

# Re-propose Directives Iteration 2

*******************************************************
*                   CollectiveHLS                     *
*******************************************************
* Number of PCs         = 3
* Number of Clusters    = 5
* Probability Threshold = 0.1
* VitisHLS Opt.         = False
* Re-propose Directives = True
* FPGA Id               = xczu7ev-ffvc1156-2-e
* Target Clock Period   = 3.33
*******************************************************
* Optimized App. = Machsuite-GEMM-NCubed
*******************************************************
* Design Latency = 0.61709229 msec
* BRAM %         = 0 %
* DSP %          = 0 %
* FF %           = 15 %
* LUT %          = 12 %
* Synthesis Time = 83.9670057296753 sec
*******************************************************

```

## Publication

If you find our project useful, please consider citing our paper:

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
