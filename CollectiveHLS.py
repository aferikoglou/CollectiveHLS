import os
import argparse
import modules.utils as utils

from modules.optimizer import Optimizer

################################
# Parse Command Line Arguments #
################################

parser = argparse.ArgumentParser(description='CollectiveHLS: A Collaborative Approach to High-Level Synthesis Design Optimization')
parser.add_argument('--APPLICATION_TO_BE_OPTIMIZED', type=str, required=True, choices=['Machsuite-GEMM-NCubed', 'RodiniaHLS-KNN-Pipeline'], help='The application targeted for optimization by CollectiveHLS.')
parser.add_argument('--VITIS_OPTIMIZATIONS_ENABLED', type=utils.str2bool, default=False, help='Specify whether to enable the default Vitis optimizations.')
parser.add_argument('--TIMEOUT', type=int, default=3600, help='Specifies the maximum allowable time for the High-Level Synthesis process to complete for a single design. (Default: 1 hour')
parser.add_argument('--DEVICE_ID', type=str, default="xczu7ev-ffvc1156-2-e", help='The identifier for the target FPGA. (Default: AMD UltraScale+ MPSoC ZCU104)')
parser.add_argument('--CLK_PERIOD', type=str, default="3.33", help='The specified clock period for the target FPGA. (Default: 3.33 nsec)')
args = parser.parse_args()

APPLICATION_TO_BE_OPTIMIZED = args.APPLICATION_TO_BE_OPTIMIZED
VITIS_OPTIMIZATIONS_ENABLED = args.VITIS_OPTIMIZATIONS_ENABLED
TIMEOUT                     = args.TIMEOUT
DEVICE_ID                   = args.DEVICE_ID
CLK_PERIOD                  = args.CLK_PERIOD

################################
# Parameters for CollectiveHLS #
################################

PRINCIPAL_COMPONENTS_NUM = 3
CLUSTER_NUM              = 5
PROBABILITY_THRESHOLD    = 0.1

APPLICATION_OUTPUT_DIR = os.path.join("output", APPLICATION_TO_BE_OPTIMIZED)
utils.rm_r(APPLICATION_OUTPUT_DIR)
                                                
optimizer = Optimizer(
    APPLICATION_OUTPUT_DIR,
    PRINCIPAL_COMPONENTS_NUM,
    CLUSTER_NUM,
    PROBABILITY_THRESHOLD,
    DEVICE_ID,
    CLK_PERIOD,
    TIMEOUT,
    VITIS_OPTIMIZATIONS_ENABLED,
    APPLICATION_TO_BE_OPTIMIZED
)

optimizer.execute()