import os
import pandas as pd
import modules.utils as utils

from sklearn.cluster import KMeans
from modules.preprocessor import Preprocessor
from modules.directivesProposal import DirectivesProposal
from modules.hlsRunner import HLSRunner

class Optimizer:
    """
    A class to optimize the source code of applications by proposing directives based on clustering 
    of source code features and Pareto optimal distributions.

    Attributes:
    ----------
    OUTPUT_DIR : str
        Directory to store output files.
    PRINCIPAL_COMPONENTS_NUM : int
        Number of principal components for clustering.
    CLUSTER_NUM : int
        Number of clusters for k-means.
    PROBABILITY_THRESHOLD : float
        Probability threshold for directive proposal.
    df : pd.DataFrame
        DataFrame containing applications and their principal components.
    app_name_optimized : str
        Name of the application to be optimized.
    kmeans : KMeans
        Instance of the k-means clustering model.
    directivesProposal : DirectivesProposal
        Instance of the DirectivesProposal class for proposing directives.
    proposed_directives_per_cluster_map : dict
        Maps cluster IDs to proposed directives.

    Methods:
    -------
    _perform_source_code_clustering(df_input):
        Clusters the applications based on their principal components and assigns them cluster IDs.
        
    _get_cluster_PO_distribution(df_current_cluster, cluster_id):
        Retrieves the Pareto optimal distribution for a given cluster.

    _apply_directives(INPUT_FILE_PATH, OUTPUT_FILE_PATH, actual_proposed_directives):
        Applies proposed directives to the source code and writes the optimized code to a new file.

    _get_TLF(APP_DIR):
        Retrieves the top-level function name from the application's kernel info.

    _get_TLF_fname(SOURCE_CODE_INPUT_APP_DIR):
        Retrieves the filename containing the top-level function in the source code directory.

    execute():
        Executes the entire optimization process, from clustering to applying directives to the source code.
    """

    def __init__(self, OUTPUT_DIR, PRINCIPAL_COMPONENTS_NUM, CLUSTER_NUM, PROBABILITY_THRESHOLD, DEVICE_ID, CLK_PERIOD, TIMEOUT, VITIS_OPTIMIZATIONS_ENABLED, APPLICATION_TO_BE_OPTIMIZED):
        """
        Initializes the Optimizer with the necessary configurations and input data.

        Parameters:
        ----------
        OUTPUT_DIR : str
            Directory to store output files.
        PRINCIPAL_COMPONENTS_NUM : int
            Number of principal components for clustering.
        CLUSTER_NUM : int
            Number of clusters for k-means.
        PROBABILITY_THRESHOLD : float
            Probability threshold for directive proposal.
        DEVICE_ID : str
            Identifier for the target FPGA.
        CLK_PERIOD : str
            Specified clock period for the target FPGA.
        TIMEOUT : int
            Maximum allowable time for the HLS process to complete.
        VITIS_OPTIMIZATIONS_ENABLED : bool
            Whether to enable the default Vitis optimizations.
        APPLICATION_TO_BE_OPTIMIZED : str
            The application to be optimized.
        """
        self.APPLICATIONS_DIR = "./Applications"
        self.PARETO_OPTIMAL_DISTRIBUTIONS_DIR = "./Knowledge_Base/Pareto_Frontiers"

        self.OUTPUT_DIR = OUTPUT_DIR
        utils.mkdir_p(OUTPUT_DIR)

        self.PRINCIPAL_COMPONENTS_NUM = PRINCIPAL_COMPONENTS_NUM
        self.CLUSTER_NUM = CLUSTER_NUM
        self.PROBABILITY_THRESHOLD = PROBABILITY_THRESHOLD

        self.DEVICE_ID = DEVICE_ID
        self.CLK_PERIOD = CLK_PERIOD
        self.TIMEOUT = TIMEOUT
        self.VITIS_OPTIMIZATIONS_ENABLED = VITIS_OPTIMIZATIONS_ENABLED

        self.app_name_optimized = APPLICATION_TO_BE_OPTIMIZED
        preprocessor            = Preprocessor(PRINCIPAL_COMPONENTS_NUM)
        self.df                 = preprocessor.preprocess()

        self.kmeans = None
        
        self.directivesProposal = DirectivesProposal(self.OUTPUT_DIR, PROBABILITY_THRESHOLD)
        self.proposed_directives_per_cluster_map = {}

    def _perform_source_code_clustering(self, df_input):
        """
        Clusters the applications based on their principal components.

        Parameters:
        ----------
        df_input : pd.DataFrame
            DataFrame containing the principal components for clustering.

        Returns:
        -------
        pd.DataFrame
            DataFrame containing application names and their assigned cluster IDs.
        """
        app_names = df_input['Application_Name'].to_numpy()
        df_values = df_input.drop(columns="Application_Name").to_numpy()

        # Initialize KMeans clustering model
        self.kmeans = KMeans(
            n_clusters=self.CLUSTER_NUM,
            init='k-means++',
            n_init=10,
            max_iter=300,
            tol=0.0001,
            random_state=42,
            algorithm='lloyd'
        )

        # Perform clustering
        labels = self.kmeans.fit_predict(df_values)

        # Create and save DataFrame with application names and cluster IDs
        df_output = pd.DataFrame({
            "Application_Name": app_names,
            "Cluster_Id": labels
        }).sort_values("Cluster_Id")

        fname = f"PC_{self.PRINCIPAL_COMPONENTS_NUM}_CLUSTER_NUM_{self.CLUSTER_NUM}.csv"
        df_output.to_csv(os.path.join(self.OUTPUT_DIR, fname), index=False)

        return df_output

    def _get_cluster_PO_distribution(self, df_current_cluster, cluster_id):
        """
        Retrieves the Pareto optimal distribution for a given cluster.

        Parameters:
        ----------
        df_current_cluster : pd.DataFrame
            DataFrame containing applications within the current cluster.
        cluster_id : int
            The ID of the cluster.

        Returns:
        -------
        pd.DataFrame
            DataFrame containing the Pareto optimal distribution of the current cluster.
        """
        df_cluster_pareto_optimal_distribution = pd.DataFrame()
        app_names = df_current_cluster['Application_Name'].to_numpy()

        for app_name in app_names:
            fpath = os.path.join(self.PARETO_OPTIMAL_DISTRIBUTIONS_DIR, f"{app_name}.csv")
            if os.path.exists(fpath):
                df_app_pareto_optimal_distribution = pd.read_csv(fpath)
                df_cluster_pareto_optimal_distribution = pd.concat([df_cluster_pareto_optimal_distribution, df_app_pareto_optimal_distribution])

        # Save the cluster Pareto optimal distribution to a CSV file
        fname = f"CLUSTER_{cluster_id}_PARETO_OPTIMAL_DISTRIBUTION.csv"
        df_cluster_pareto_optimal_distribution.to_csv(os.path.join(self.OUTPUT_DIR, fname), index=False)

        return df_cluster_pareto_optimal_distribution

    def _apply_directives(self, INPUT_FILE_PATH, OUTPUT_FILE_PATH, actual_proposed_directives):
        """
        Applies proposed directives to the source code and writes the optimized code to a new file.

        Parameters:
        ----------
        INPUT_FILE_PATH : str
            Path to the original source code file.
        OUTPUT_FILE_PATH : str
            Path to the output file where optimized code will be written.
        actual_proposed_directives : dict
            Dictionary containing action points and corresponding directives to be applied.
        """
        with open(INPUT_FILE_PATH, 'r') as fr, open(OUTPUT_FILE_PATH, 'w') as fw:
            cnt = 1
            for line in fr:
                stripped_line = line.replace(' ', '').replace('\n', '').replace('\t', '')

                pattern = f'L{cnt}'
                if pattern in stripped_line:
                    fw.write(line)
                    if pattern in actual_proposed_directives:
                        fw.write(actual_proposed_directives[pattern] + '\n')
                    cnt += 1
                    continue

                fw.write(line)

    def _get_top_level_function(self, APP_DIR):
        """
        Retrieves the top-level function name from the application's kernel info.

        Parameters:
        ----------
        APP_DIR : str
            Directory of the application.

        Returns:
        -------
        str
            Name of the top-level function.
        """
        with open(os.path.join(APP_DIR, 'Kernel-Info.txt'), 'r') as f:
            return f.readline().strip()

    def _get_top_level_function_fname(self, SOURCE_CODE_INPUT_APP_DIR):
        """
        Retrieves the filename containing the top-level function in the source code directory.

        Parameters:
        ----------
        SOURCE_CODE_INPUT_APP_DIR : str
            Directory containing the source code files.

        Returns:
        -------
        str
            Filename containing the top-level function.
        """
        for fname in os.listdir(SOURCE_CODE_INPUT_APP_DIR):
            if fname.endswith((".c", ".cpp")) and fname not in ["support.c", "local_support.c"]:
                return fname
        return ""

    def _write_output_command_line(self, qor_map):
        
        qor_map_key = "original_wVO" if self.VITIS_OPTIMIZATIONS_ENABLED else "original_woVO"
        
        synthesized = True
        try:
            design_latency_msec = qor_map[qor_map_key]["design_latency_msec"]
            synthesis_time_sec  = qor_map[qor_map_key]["synthesis_time_sec"]
            bram_utilization    = qor_map[qor_map_key]["bram_utilization"]
            dsp_utilization     = qor_map[qor_map_key]["dsp_utilization"]
            ff_utilization      = qor_map[qor_map_key]["ff_utilization"]
            lut_utilization     = qor_map[qor_map_key]["lut_utilization"]
        except:
            synthesized = False

        print("*******************************************************")
        print("*                   CollectiveHLS                     *")
        print("*******************************************************")
        print("* Number of PCs         =", self.PRINCIPAL_COMPONENTS_NUM)
        print("* Number of Clusters    =", self.CLUSTER_NUM)
        print("* Probability Threshold =", self.PROBABILITY_THRESHOLD)
        print("* VitisHLS Opt.         =", self.VITIS_OPTIMIZATIONS_ENABLED)
        print("* Re-propose Directives =", False)
        print("* FPGA Id               =", self.DEVICE_ID)
        print("* Target Clock Period   =", self.CLK_PERIOD)
        print("*******************************************************")
        print("* Optimized App. =", self.app_name_optimized)
        print("*******************************************************")
        
        if synthesized:
            print("* Design Latency =", design_latency_msec, "msec")
            print("* BRAM %         =", bram_utilization, "%")
            print("* DSP %          =", dsp_utilization, "%")
            print("* FF %           =", ff_utilization, "%")
            print("* LUT %          =", lut_utilization, "%")
            print("* Synthesis Time =", synthesis_time_sec, "sec")
        else:
            print("* The design suggested by CollectiveHLS could not be synthesized.")

        print("*******************************************************")

    def execute(self):
        """
        Executes the optimization process, which involves:
        1. Clustering the source code based on principal components.
        2. Proposing directives for each cluster.
        3. Applying the directives to the source code of the application to be optimized.
        4. Perform High-Level Synthesis for the optimized application.
        5. Write the Quality of Result (QoR) metrics of the optimized design to command line.
        """

        # Create a directory to store the optimized source code
        OPTIMIZED_SOURCE_CODE_OUTPUT_DIR = os.path.join(self.OUTPUT_DIR, "OPTIMIZED_SOURCE_CODE")
        utils.mkdir_p(OPTIMIZED_SOURCE_CODE_OUTPUT_DIR)

        # Exclude the current application to be optimized from the clustering process
        df_input = self.df[self.df['Application_Name'] != self.app_name_optimized]
        
        # Perform clustering on the remaining applications
        df_clustered = self._perform_source_code_clustering(df_input)

        # For each cluster, retrieve the Pareto optimal distribution and propose directives
        for cluster_id in range(self.CLUSTER_NUM):
            # Get the subset of applications belonging to the current cluster
            df_current_cluster = df_clustered[df_clustered['Cluster_Id'] == cluster_id]
            
            # Retrieve the Pareto optimal distribution for this cluster
            df_cluster_pareto_optimal_distribution = self._get_cluster_PO_distribution(df_current_cluster, cluster_id)

            # Propose directives based on the Pareto optimal distribution
            proposed_directives = self.directivesProposal.propose_directives_uncond(df_cluster_pareto_optimal_distribution)
            
            # Store the proposed directives for the current cluster
            self.proposed_directives_per_cluster_map[cluster_id] = proposed_directives

        # Identify the cluster to which the application to be optimized belongs
        df_app = self.df[self.df['Application_Name'] == self.app_name_optimized]
        
        # Extract the principal component values for the application
        app_pc_values = df_app.drop(columns="Application_Name").to_numpy()
        
        # Predict the cluster ID for the application
        predicted_cluster_id = self.kmeans.predict(app_pc_values)[0]

        # Retrieve the proposed directives for the predicted cluster
        predicted_cluster_proposed_directives = self.proposed_directives_per_cluster_map[predicted_cluster_id]
        
        # Filter and get the actual proposed directives for the application to be optimized
        actual_proposed_directives = self.directivesProposal.get_actual_proposed_directives(predicted_cluster_proposed_directives, self.app_name_optimized)

        # Apply the directives to the source code of the application
        SOURCE_CODE_INPUT_APP_DIR = os.path.join(self.APPLICATIONS_DIR, self.app_name_optimized)
        SOURCE_CODE_OUTPUT_APP_DIR = os.path.join(OPTIMIZED_SOURCE_CODE_OUTPUT_DIR, self.app_name_optimized)
        
        # Copy the source code to the output directory
        utils.cp_r(SOURCE_CODE_INPUT_APP_DIR, SOURCE_CODE_OUTPUT_APP_DIR)

        # Retrieve the top-level function name and the corresponding file name
        top_level_function = self._get_top_level_function(SOURCE_CODE_INPUT_APP_DIR)
        top_level_function_fname = self._get_top_level_function_fname(SOURCE_CODE_INPUT_APP_DIR)
        
        # Determine the file extension (C or C++)
        extension = '.cpp' if '.cpp' in top_level_function_fname else '.c'

        # Define the paths for the unoptimized and optimized source code files
        UNOPTIMIZED_SRC_CODE_FILE_PATH = os.path.join(SOURCE_CODE_OUTPUT_APP_DIR, top_level_function_fname)
        OPTIMIZED_SRC_CODE_FILE_PATH = os.path.join(SOURCE_CODE_OUTPUT_APP_DIR, f"optimized{extension}")

        # Apply the proposed directives to the source code
        self._apply_directives(UNOPTIMIZED_SRC_CODE_FILE_PATH, OPTIMIZED_SRC_CODE_FILE_PATH, actual_proposed_directives)

        # Initialize the HLSRunner to run the HLS process with the optimized code
        runner = HLSRunner (
            SOURCE_CODE_OUTPUT_APP_DIR, 
            f"optimized{extension}", 
            top_level_function, 
            self.DEVICE_ID, 
            self.CLK_PERIOD, 
            self.TIMEOUT, 
            self.VITIS_OPTIMIZATIONS_ENABLED
        )
        # Perform the High-Level Synthesis process for the optimized design
        runner.run()
        # Write the Quality of Result (QoR) metrics of the optimized design to command line
        qor_metrics = runner.get_synthesis_results()
        self._write_output_command_line(qor_metrics)