import os
import json

import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None

import modules.utils as utils

class DirectivesAnalyzer:
    """
    A class to analyze High-Level Synthesis (HLS) directives and their impact on Quality of Results (QoR) metrics 
    such as design latency, resource utilization (BRAM, DSP, FF, LUT), and overall synthesis efficiency.
    """

    def __init__(self, INPUT_DIR, CLUSTER_ID):
        """
        Initialize the DirectivesAnalyzer with the input directory and cluster ID.

        Args:
            INPUT_DIR (str): The directory containing input data files.
            CLUSTER_ID (int): The ID of the cluster being analyzed.
        """
        self.ARRAY_ACTION_POINTS_ORDERED = [
            "Array_1", "Array_2", "Array_3", "Array_4", "Array_5", "Array_6", "Array_7", 
            "Array_8", "Array_9", "Array_10", "Array_11", "Array_12", "Array_13", 
            "Array_14", "Array_15", "Array_16", "Array_17", "Array_18", "Array_19", 
            "Array_20", "Array_21", "Array_22"
        ]
        
        self.LOOP_ACTION_POINTS_ORDERED = [
            "OuterLoop_1", "OuterLoop_2", "OuterLoop_3", "OuterLoop_4", "OuterLoop_5", 
            "OuterLoop_6", "OuterLoop_7", "OuterLoop_8", "OuterLoop_9", "OuterLoop_10", 
            "OuterLoop_11", "OuterLoop_12", "OuterLoop_13", "OuterLoop_14", "OuterLoop_15", 
            "OuterLoop_16", "OuterLoop_17", "OuterLoop_18", "OuterLoop_19", "OuterLoop_20", 
            "OuterLoop_21", "OuterLoop_22", "OuterLoop_23", "OuterLoop_24", "OuterLoop_25", 
            "OuterLoop_26", "InnerLoop_1_1", "InnerLoop_1_2", "InnerLoop_1_3", "InnerLoop_1_4", 
            "InnerLoop_1_5", "InnerLoop_1_6", "InnerLoop_1_7", "InnerLoop_1_8", "InnerLoop_1_9", 
            "InnerLoop_1_10", "InnerLoop_1_11", "InnerLoop_1_12", "InnerLoop_1_13", "InnerLoop_1_14", 
            "InnerLoop_1_15", "InnerLoop_1_16", "InnerLoop_2_1", "InnerLoop_2_2", "InnerLoop_2_3", 
            "InnerLoop_2_4", "InnerLoop_2_5", "InnerLoop_2_6", "InnerLoop_2_7", "InnerLoop_3_1", 
            "InnerLoop_3_2", "InnerLoop_3_3", "InnerLoop_3_4", "InnerLoop_3_5", "InnerLoop_4_1", 
            "InnerLoop_4_2"
        ]
        
        self.ACTION_POINTS_ORDERED = self.ARRAY_ACTION_POINTS_ORDERED + self.LOOP_ACTION_POINTS_ORDERED
        self.CLUSTER_ID = CLUSTER_ID

        # Define the file path for the cluster's Pareto optimal distribution CSV file.
        CLUSTER_PARETO_OPTIMAL_DISTRIBUTION_FILE_NAME = f'CLUSTER_{CLUSTER_ID}_PARETO_OPTIMAL_DISTRIBUTION.csv'
        self.CLUSTER_PARETO_OPTIMAL_DISTRIBUTION_FILE_PATH = os.path.join(INPUT_DIR, CLUSTER_PARETO_OPTIMAL_DISTRIBUTION_FILE_NAME)
        
        # Define the output directory and ensure it exists.
        self.OUTPUT_DIR = os.path.join(INPUT_DIR, 'DIRECTIVE_QOR_METRIC_DISTRIBUTION_ANALYSIS')
        utils.mkdir_p(self.OUTPUT_DIR)

        # Dictionary to store QoR statistics for each directive.
        self.ap_directives_qor_statistics_on_off = {}

    def _translate_array_directive(self, array_directive):
        """
        Translate an array directive into a more descriptive label.

        Args:
            array_directive (str): The array directive to translate.

        Returns:
            str: A descriptive label for the array directive.
        """
        if array_directive != "NDIR":
            parts = array_directive.split(" ")
            label = ""
            if "complete" in parts:
                dimension = parts[5].split("=")[1]
                label = f"complete_{dimension}"
            else:
                partition_type = parts[4]
                factor = parts[5].split("=")[1]
                dimension = parts[6].split("=")[1]
                label = f"{partition_type}_{factor}_{dimension}"
            
            return label
        else:
            return "NDIR"

    def _translate_loop_directive(self, loop_directive):
        """
        Translate a loop directive into a more descriptive label.

        Args:
            loop_directive (str): The loop directive to translate.

        Returns:
            str: A descriptive label for the loop directive.
        """
        if loop_directive != "NDIR":
            parts = loop_directive.split(" ")
            label = ""
            if "unroll" in parts:
                if len(parts) > 3:
                    factor = parts[3].split("=")[1]
                    label = f"unroll_{factor}"
                else:
                    label = "unroll"
            else:
                label = "pipeline_1" if len(parts) > 3 else "pipeline"

            return label
        else:
            return "NDIR"

    def _get_distribution_statistical_analysis(self, input_distribution):
        """
        Calculate statistical metrics for a given distribution of values.

        Args:
            input_distribution (list): A list of numerical values to analyze.

        Returns:
            dict: A dictionary containing mean, standard deviation, median, percentiles, maximum, and minimum values.
        """
        mean = np.mean(input_distribution)
        standard_deviation = np.std(input_distribution)
        median = np.median(input_distribution)
        percentile25 = np.percentile(input_distribution, 25)
        percentile75 = np.percentile(input_distribution, 75)
        maximum = float(np.max(input_distribution))
        minimum = float(np.min(input_distribution))

        return {
            "mean": mean,
            "standard_deviation": standard_deviation,
            "median": median,
            "percentile25": percentile25,
            "percentile75": percentile75,
            "maximum": maximum,
            "minimum": minimum
        }

    def export(self):
        """
        Export the analyzed QoR statistics to a JSON file.
        """
        output_file_path = os.path.join(self.OUTPUT_DIR, f"CLUSTER_{self.CLUSTER_ID}.json")
        with open(output_file_path, "w") as outFile:
            json.dump(self.ap_directives_qor_statistics_on_off, outFile, indent=4, sort_keys=True)

    def analyze(self):
        """
        Perform the analysis of directives for the cluster's Pareto optimal distribution.
        Translates directives and calculates QoR metrics for each action point.
        """
        df = pd.read_csv(self.CLUSTER_PARETO_OPTIMAL_DISTRIBUTION_FILE_PATH)

        if df.empty:
            print(f"The Pareto Optimal Distribution of Cluster with ID {self.CLUSTER_ID} is empty.")
        else:
            # Translate array and loop directives
            for column_index in df.columns:
                for row_index in df.index:
                    if column_index in self.ARRAY_ACTION_POINTS_ORDERED:
                        translated_directive = self._translate_array_directive(df[column_index][row_index])
                        df[column_index][row_index] = translated_directive
                    elif column_index in self.LOOP_ACTION_POINTS_ORDERED:
                        translated_directive = self._translate_loop_directive(df[column_index][row_index])
                        df[column_index][row_index] = translated_directive

            # Analyze each action point
            for action_point in self.ACTION_POINTS_ORDERED:
                directives = df[action_point].values.flatten().tolist()

                # Find all distinct directives
                distinct_directives = list(set(directives))

                # Analyze QoR metrics for each directive
                directives_qor_statistics_on_off = {}
                for directive in distinct_directives:
                    if directive != "NDIR":
                        df_on = df[df[action_point] == directive][["DesignLatency_Msec", "BRAM_Utilization", "DSP_Utilization", "FF_Utilization", "LUT_Utilization"]]
                        df_on["enabled"] = "ON"

                        df_off = df[df[action_point] != directive][["DesignLatency_Msec", "BRAM_Utilization", "DSP_Utilization", "FF_Utilization", "LUT_Utilization"]]
                        df_off["enabled"] = "OFF"

                        if df_off.empty:
                            print(f"{directive} is always ON in action point {action_point}")
                        else:
                            qor_statistics_on_off = {}
                            for enabled in ["ON", "OFF"]:
                                df_used = df_on if enabled == "ON" else df_off

                                qor_statistics = {}
                                for qor_metric in ["DesignLatency_Msec", "BRAM_Utilization", "DSP_Utilization", "FF_Utilization", "LUT_Utilization"]:
                                    input_distribution = df_used[qor_metric].values.flatten().tolist()
                                    qor_statistics[qor_metric] = self._get_distribution_statistical_analysis(input_distribution)

                                qor_statistics_on_off[enabled] = qor_statistics

                            directives_qor_statistics_on_off[directive] = qor_statistics_on_off

                self.ap_directives_qor_statistics_on_off[action_point] = directives_qor_statistics_on_off

            # Export the analysis results
            self.export()
    
    def get_ap_directives_qor_statistics_on_off_map(self):
        """
        Get the QoR statistics map for the analyzed action points and directives.

        Returns:
            dict: A dictionary mapping action points to their QoR statistics.
        """
        return self.ap_directives_qor_statistics_on_off
