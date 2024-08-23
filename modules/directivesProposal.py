import os

import pandas as pd

class DirectivesProposal:
    """
    The `DirectivesProposal` class generates HLS directives for array and loop action points based on 
    the distribution of Pareto optimal solutions. It also handles the mapping of predicted directives 
    to application-specific directives.

    Attributes:
        OUTPUT_DIR (str): Directory where output files are saved.
        PROBABILITY_THRESHOLD (float): Threshold probability for selecting a directive.
        ARRAY_ACTION_POINTS_ORDERED (list): List of array action points in the order they appear.
        LOOP_ACTION_POINTS_ORDERED (list): List of loop action points in the order they appear.
        ACTION_POINTS_ORDERED (list): Combined list of array and loop action points.
    """

    def __init__(self, OUTPUT_DIR: str, PROBABILITY_THRESHOLD: float):
        """
        Initializes the `DirectivesProposal` class.

        Args:
            OUTPUT_DIR (str): Directory where output files will be saved.
            PROBABILITY_THRESHOLD (float): Minimum probability required to consider a directive.
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
        self.PROBABILITY_THRESHOLD = PROBABILITY_THRESHOLD
        self.OUTPUT_DIR = OUTPUT_DIR

    def _get_array_AP_directive(self, array_directives: list) -> str:
        """
        Determines the most likely directive for an array action point based on occurrence frequency.

        Args:
            array_directives (list): Directives associated with a specific array action point.

        Returns:
            str: The proposed directive for the array action point, or 'NDIR' if no directive meets the threshold.
        """
        proposed_directive = "NDIR"
        total = len(array_directives)
        labels = []

        for directive in array_directives:
            if directive != "NDIR":
                parts = directive.split(" ")
                if "complete" in parts:
                    dimension = parts[5].split("=")[1]
                    labels.append(f"complete_{dimension}")
                else:
                    partition_type = parts[4]
                    factor = parts[5].split("=")[1]
                    dimension = parts[6].split("=")[1]
                    labels.append(f"{partition_type}_{factor}_{dimension}")

        if labels:
            counts = {label: labels.count(label) for label in labels}
            max_count = max(counts.values())
            if max_count / total >= self.PROBABILITY_THRESHOLD:
                proposed_directive = max(counts, key=counts.get)

        return proposed_directive

    def _get_loop_AP_directive(self, loop_directives: list) -> str:
        """
        Determines the most likely directive for a loop action point based on occurrence frequency.

        Args:
            loop_directives (list): Directives associated with a specific loop action point.

        Returns:
            str: The proposed directive for the loop action point, or 'NDIR' if no directive meets the threshold.
        """
        proposed_directive = "NDIR"
        total = len(loop_directives)
        labels = []

        for directive in loop_directives:
            if directive != "NDIR":
                parts = directive.split(" ")
                if "unroll" in parts:
                    label = f"unroll_{parts[3].split('=')[1]}" if len(parts) > 3 else "unroll"
                else:
                    label = "pipeline_1" if len(parts) > 3 else "pipeline"
                labels.append(label)

        if labels:
            counts = {label: labels.count(label) for label in labels}
            max_count = max(counts.values())
            if max_count / total >= self.PROBABILITY_THRESHOLD:
                proposed_directive = max(counts, key=counts.get)

        return proposed_directive

    def propose_directives_uncond(self, df_PO_distribution: pd.DataFrame) -> dict:
        """
        Proposes directives for all action points based on the distribution of Pareto optimal solutions.

        Args:
            df_PO_distribution (pandas.DataFrame): DataFrame containing Pareto optimal solution distributions.

        Returns:
            dict: A dictionary mapping action points to their proposed directives.
        """
        AP_directive_map = {}

        if df_PO_distribution.empty:
            print("No Pareto optimal distribution provided. Cannot propose directives.")
            AP_directive_map = {ap: "NDIR" for ap in self.ACTION_POINTS_ORDERED}
        else:
            df_directives = df_PO_distribution[self.ACTION_POINTS_ORDERED]
            for action_point in self.ARRAY_ACTION_POINTS_ORDERED:
                directives = df_directives[action_point].values.flatten().tolist()
                AP_directive_map[action_point] = self._get_array_AP_directive(directives)

            for action_point in self.LOOP_ACTION_POINTS_ORDERED:
                directives = df_directives[action_point].values.flatten().tolist()
                AP_directive_map[action_point] = self._get_loop_AP_directive(directives)

        return AP_directive_map
    
    def get_actual_proposed_directives(self, predicted_cluster_proposed_directives: dict, app_name: str) -> dict:
        """
        Maps predicted directives from a cluster to actual application-specific directives.

        Args:
            predicted_cluster_proposed_directives (dict): Predicted directives from a cluster for each action point.
            app_name (str): The name of the application being analyzed.

        Returns:
            dict: A dictionary mapping labels to application-specific HLS directives.
        """
        label_directive_map = {}
        input_file = os.path.join("Applications", app_name, "ActionPoint-Label-Mapping.txt")

        with open(input_file, "r") as f:
            lines = f.readlines()

        for line in lines:
            parts = line.strip().split(',')

            if len(parts) > 3:
                action_point, array_name, label = parts[0], parts[1], parts[2]
                dim1_size = int(parts[3].replace("[", ""))
                dim2_size = int(parts[4].replace("]", "").replace(" ", ""))
                
                proposed_directive = predicted_cluster_proposed_directives[action_point]
                if proposed_directive != "NDIR":
                    directive_parts = proposed_directive.split('_')
                    if len(directive_parts) == 3:
                        partition_type, partition_factor, partition_dimension = directive_parts
                        dim_size = dim1_size if partition_dimension == "1" else dim2_size

                        if int(partition_factor) <= dim_size:
                            directive = f"#pragma HLS array_partition variable={array_name} {partition_type} factor={partition_factor} dim={partition_dimension}"
                        else:
                            directive = ""
                            print("Modified directive proposal due to dimension size.")
                    else:
                        partition_type, partition_dimension = directive_parts
                        dim_size = dim1_size if partition_dimension == "1" else dim2_size
                        directive = f"#pragma HLS array_partition variable={array_name} {partition_type} dim={partition_dimension}" if dim_size <= 512 else ""
                        if not directive:
                            print("Modified directive proposal due to dimension size.")
            else:
                action_point, label = parts[0], parts[1]
                proposed_directive = predicted_cluster_proposed_directives[action_point]
                if proposed_directive != "NDIR":
                    directive_parts = proposed_directive.split('_')
                    if len(directive_parts) == 2:
                        if "pipeline" in directive_parts:
                            directive = f"#pragma HLS pipeline II={directive_parts[1]}"
                        else:
                            directive = f"#pragma HLS unroll factor={directive_parts[1]}"
                    else:
                        directive = f"#pragma HLS {directive_parts[0]}"

            label_directive_map[label] = directive

        return label_directive_map

    def get_application_action_point_label_map(self, app_name: str) -> dict:
        """
        Retrieves the mapping between action points and labels for a given application.

        Args:
            app_name (str): The name of the application.

        Returns:
            dict: A dictionary mapping action points to their respective labels.
        """
        application_action_point_label_map = {}
        input_file = os.path.join("Applications", app_name, "ActionPoint-Label-Mapping.txt")

        with open(input_file, "r") as f:
            lines = f.readlines()

        for line in lines:
            parts = line.strip().split(',')
            action_point = int(parts[0])
            label = parts[2] if len(parts) > 3 else parts[1]
            application_action_point_label_map[action_point] = label

        return application_action_point_label_map
