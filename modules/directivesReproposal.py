from modules.directivesAnalyzer import DirectivesAnalyzer

class DirectivesReproposal:
    """
    A class to reanalyze and propose directive changes for a given cluster of High-Level Synthesis (HLS) action points 
    based on resource utilization and latency impacts.
    """

    def __init__(self, OUTPUT_DIR, APP_PREDICTED_CLUSTER_ID, APP_ACTION_POINT_LABEL_MAP):
        """
        Initialize the DirectivesReproposal object with the output directory, cluster ID, and action point label map.

        Args:
            OUTPUT_DIR (str): Directory where output data is stored.
            APP_PREDICTED_CLUSTER_ID (int): Predicted cluster ID for the application.
            APP_ACTION_POINT_LABEL_MAP (dict): Mapping of action points to their labels.
        """
        self.OUTPUT_DIR = OUTPUT_DIR
        self.APP_PREDICTED_CLUSTER_ID = APP_PREDICTED_CLUSTER_ID
        self.APP_ACTION_POINT_LABEL_MAP = APP_ACTION_POINT_LABEL_MAP
        self.APP_ACTION_POINTS = list(APP_ACTION_POINT_LABEL_MAP.keys())
        
        # Analyze the proposed directives of the assigned source code cluster for the current application
        directives_analyzer = DirectivesAnalyzer(OUTPUT_DIR, APP_PREDICTED_CLUSTER_ID)
        directives_analyzer.analyze()
        
        self.ap_directives_qor_statistics_on_off_map = directives_analyzer.get_ap_directives_qor_statistics_on_off_map()
    
    def get_violated_resource(self, bram_utilization, dsp_utilization, ff_utilization, lut_utilization):
        """
        Identify the most violated resource based on utilization percentages.

        Args:
            bram_utilization (float): Utilization percentage for BRAM.
            dsp_utilization (float): Utilization percentage for DSP.
            ff_utilization (float): Utilization percentage for FF.
            lut_utilization (float): Utilization percentage for LUT.

        Returns:
            tuple: A tuple containing the name of the most violated resource and its utilization percentage.
        """
        violated_resource = ""
        violated_resource_percentage = -1
        
        # Check each resource and update if it's the most violated one
        if bram_utilization > 100 and bram_utilization > violated_resource_percentage:
            violated_resource = "BRAM_Utilization"
            violated_resource_percentage = bram_utilization
        if dsp_utilization > 100 and dsp_utilization > violated_resource_percentage:
            violated_resource = "DSP_Utilization"
            violated_resource_percentage = dsp_utilization
        if ff_utilization > 100 and ff_utilization > violated_resource_percentage:
            violated_resource = "FF_Utilization"
            violated_resource_percentage = ff_utilization
        if lut_utilization > 100 and lut_utilization > violated_resource_percentage:
            violated_resource = "LUT_Utilization"
            violated_resource_percentage = lut_utilization

        return violated_resource, violated_resource_percentage
    
    def _get_directive_impact_information_per_action_point(self, violated_resource, current_proposed_directives):
        """
        Retrieve the impact information of directives on the violated resource and latency for each action point.

        Args:
            violated_resource (str): The resource that is overutilized.
            current_proposed_directives (dict): The current set of proposed directives for each action point.

        Returns:
            list: A list of tuples containing action point, resource impact difference, and latency impact difference.
        """
        directive_impact_information_per_action_point = []
        
        for action_point in self.APP_ACTION_POINTS:
            proposed_directive = current_proposed_directives.get(action_point, 'NDIR')

            if proposed_directive == 'NDIR':
                continue

            statistics_ON = self.ap_directives_qor_statistics_on_off_map[action_point][proposed_directive]["ON"]
            statistics_OFF = self.ap_directives_qor_statistics_on_off_map[action_point][proposed_directive]["OFF"]
            
            median_violated_resource_ON = statistics_ON[violated_resource]['median']
            median_violated_resource_OFF = statistics_OFF[violated_resource]['median']
            median_latency_ON = statistics_ON['DesignLatency_Msec']['median']
            median_latency_OFF = statistics_OFF['DesignLatency_Msec']['median']

            median_violated_resource_diff = median_violated_resource_ON - median_violated_resource_OFF
            median_latency_diff = median_latency_ON - median_latency_OFF

            temp_tuple = (action_point, median_violated_resource_diff, median_latency_diff)
            directive_impact_information_per_action_point.append(temp_tuple)
                
        return directive_impact_information_per_action_point
    
    def get_highest_impact_action_point_information_map(self, violated_resource, current_proposed_directives):
        """
        Determine the action point with the highest impact on the violated resource and return its information.

        Args:
            violated_resource (str): The resource that is overutilized.
            current_proposed_directives (dict): The current set of proposed directives for each action point.

        Returns:
            dict: A dictionary containing the action point, directive, and label of the highest impact action point.
        """
        directive_impact_information_per_action_point = self._get_directive_impact_information_per_action_point(
            violated_resource, current_proposed_directives
        )

        directive_impact_information_per_action_point_sorted = sorted(
            directive_impact_information_per_action_point, key=lambda x: x[1], reverse=True
        )

        # Select the action point with the highest resource impact
        highest_impact_action_point_information = directive_impact_information_per_action_point_sorted[0]

        highest_impact_action_point = highest_impact_action_point_information[0]
        highest_impact_action_point_directive = current_proposed_directives[highest_impact_action_point]
        highest_impact_action_point_label = self.APP_ACTION_POINT_LABEL_MAP[highest_impact_action_point]

        highest_impact_action_point_information_map = {
            "action_point": highest_impact_action_point, 
            "directive": highest_impact_action_point_directive,
            "label": highest_impact_action_point_label
        }     

        return highest_impact_action_point_information_map
    
    def repropose_change_highest_impact_action_point_directive(self, highest_impact_action_point_information_map, current_proposed_directives, violated_resource, fw_repropose):
        """
        Repropose a new directive for the highest impact action point to reduce resource utilization while considering latency.

        Args:
            highest_impact_action_point_information_map (dict): Information about the highest impact action point.
            current_proposed_directives (dict): The current set of proposed directives for each action point.
            violated_resource (str): The resource that is overutilized.
            fw_repropose (file): File handler for logging the reproposal process.

        Returns:
            dict: The updated set of proposed directives.
        """
        print("HELLO")
        
        highest_impact_action_point = highest_impact_action_point_information_map["action_point"]
        highest_impact_action_point_directive = highest_impact_action_point_information_map["directive"]
              
        action_point_directives_map = self.ap_directives_qor_statistics_on_off_map[highest_impact_action_point]
                
        directive_impact_information = []
        for directive in action_point_directives_map:
            directive_statistics_ON = action_point_directives_map[directive]['ON']
            directive_statistics_OFF = action_point_directives_map[directive]['OFF']
                    
            median_violated_resource_ON = directive_statistics_ON[violated_resource]['median']
            median_violated_resource_OFF = directive_statistics_OFF[violated_resource]['median']
            median_latency_ON = directive_statistics_ON['DesignLatency_Msec']['median']
            median_latency_OFF = directive_statistics_OFF['DesignLatency_Msec']['median']

            median_violated_resource_diff = median_violated_resource_ON - median_violated_resource_OFF
            median_latency_diff = median_latency_ON - median_latency_OFF
                     
            temp_tuple = (directive, median_violated_resource_diff, median_latency_diff)
            directive_impact_information.append(temp_tuple)
        
        # Sort directives based on their impact on the violated resource (descending) and latency (ascending)
        directive_impact_information_sorted = sorted(directive_impact_information, key=lambda x: (-x[1], x[2]))
        print(directive_impact_information_sorted, file=fw_repropose)
                
        # Omit the directives with greater or equal impact on the violated resource than the current directive
        index = 0
        for current_tuple in directive_impact_information_sorted:
            directive = current_tuple[0]
            if directive == highest_impact_action_point_directive:
                break
            index += 1
        directive_impact_information_sorted_new = directive_impact_information_sorted[index + 1:]
        print(directive_impact_information_sorted_new, file=fw_repropose)
                
        # Sort remaining directives based on their impact on latency (ascending)
        directive_impact_information_sorted_new_latency_sorted = sorted(
            directive_impact_information_sorted_new, key=lambda x: x[2]
        )
        print(directive_impact_information_sorted_new_latency_sorted, file=fw_repropose)
        
        # Select the best directive, or default to "NDIR" if none found
        proposed_directive = directive_impact_information_sorted_new_latency_sorted[0][0] if directive_impact_information_sorted_new_latency_sorted else "NDIR"
        print(f"Proposed directive={proposed_directive}", file=fw_repropose)
                
        current_proposed_directives[highest_impact_action_point] = proposed_directive
        
        return current_proposed_directives
