import os
import json
import time
import psutil
import subprocess
from threading import Lock

class HLSRunner:
    """
    Manages the High-Level Synthesis (HLS) process, including code preparation, TCL script generation,
    synthesis execution, and results collection. Supports synchronized multi-threaded execution.

    Attributes:
        DIRECTORY_PATH (str): Directory path where source files are located.
        SRC_FILE_NAME (str): Name of the source code file.
        TOP_LEVEL_FUNC_NAME (str): The top-level function to be synthesized.
        TARGET_DEVICE (str): Target FPGA device for synthesis.
        CLOCK_PERIOD_NS (str): Clock period for synthesis in nanoseconds.
        SYNTHESIS_TIMEOUT_SEC (int): Maximum time to wait for synthesis completion, in seconds.
        VITIS_OPTIMIZATIONS_ENABLED (bool): Flag to enable/disable Vitis HLS options.
        SOURCE_CODE_LINES (list): List of lines read from the source code file.
        SYNTHESIS_RESULTS (dict): Dictionary storing the results of the synthesis experiments.
        CHECK_INTERVAL_SEC (int): Time interval (in seconds) to check synthesis status.
        OUTPUT_DIR_NAME (str): Directory for storing synthesis outputs and logs.
        LOCK (Lock): Lock object to synchronize access to shared resources in a multi-threaded environment.
    """

    def __init__(self, DIRECTORY_PATH, SRC_FILE_NAME, TOP_LEVEL_FUNC_NAME, TARGET_DEVICE, CLOCK_PERIOD_NS, SYNTHESIS_TIMEOUT_SEC, VITIS_OPTIMIZATIONS_ENABLED):
        """
        Initializes the HLSRunner with the provided parameters.

        Args:
            DIRECTORY_PATH (str): Directory path where source files are located.
            SRC_FILE_NAME (str): Name of the source code file.
            TOP_LEVEL_FUNC_NAME (str): The top-level function to be synthesized.
            TARGET_DEVICE (str): Target FPGA device for synthesis.
            CLOCK_PERIOD_NS (str): Clock period for synthesis in nanoseconds.
            SYNTHESIS_TIMEOUT_SEC (int): Maximum time to wait for synthesis to complete, in seconds.
            VITIS_OPTIMIZATIONS_ENABLED (bool): Flag to enable/disable Vitis HLS options.
        """
        self.DIRECTORY_PATH = DIRECTORY_PATH
        self.SRC_FILE_NAME = SRC_FILE_NAME
        self.TOP_LEVEL_FUNC_NAME = TOP_LEVEL_FUNC_NAME
        self.TARGET_DEVICE = TARGET_DEVICE
        self.CLOCK_PERIOD_NS = CLOCK_PERIOD_NS
        self.SYNTHESIS_TIMEOUT_SEC = SYNTHESIS_TIMEOUT_SEC
        self.VITIS_OPTIMIZATIONS_ENABLED = VITIS_OPTIMIZATIONS_ENABLED
        self.SOURCE_CODE_LINES = []
        self.SYNTHESIS_RESULTS = {}
        self.CHECK_INTERVAL_SEC = 1  # Time interval to check synthesis status (in seconds)
        self.OUTPUT_DIR_NAME = f"{TARGET_DEVICE}_{CLOCK_PERIOD_NS}"
        self.LOCK = Lock()

        # Create output directory
        os.makedirs(os.path.join(self.DIRECTORY_PATH, self.OUTPUT_DIR_NAME), exist_ok=True)

    def _read_source_code(self):
        """Reads the source code from the specified file and stores it in the SOURCE_CODE_LINES attribute."""
        with open(os.path.join(self.DIRECTORY_PATH, self.SRC_FILE_NAME), "r") as source_file:
            self.SOURCE_CODE_LINES = source_file.readlines()

    def _remove_hls_directives(self):
        """
        Removes HLS-specific directives from the source code and writes the cleaned code
        to a new file named "noDirectives.cpp".
        """
        no_directives_file_path = os.path.join(self.DIRECTORY_PATH, "noDirectives.cpp")
        with open(no_directives_file_path, "w") as cleaned_file:
            for line in self.SOURCE_CODE_LINES:
                if "#pragma HLS" not in line:
                    cleaned_file.write(line)

    def _create_tcl_script(self, project_name, src_file_path, enable_vitis_opts):
        """
        Creates a TCL script for Vitis HLS synthesis with the specified project name and options.

        Args:
            project_name (str): Name of the HLS project.
            src_file_path (str): Path to the source code file.
            enable_vitis_opts (bool): Flag to enable/disable default Vitis optimizations.
        """
        tcl_script_path = "script.tcl"
        with open(tcl_script_path, "w") as tcl_file:
            tcl_file.write(f"open_project {project_name}\n")
            tcl_file.write(f"set_top {self.TOP_LEVEL_FUNC_NAME}\n")
            tcl_file.write(f"add_files {src_file_path}\n")
            tcl_file.write('open_solution "solution1" -flow_target vivado\n')
            tcl_file.write(f"set_part {{{self.TARGET_DEVICE}}}\n")
            tcl_file.write(f"create_clock -period {self.CLOCK_PERIOD_NS} -name default\n")

            if not enable_vitis_opts:
                tcl_file.write("config_array_partition -complete_threshold 0 -throughput_driven off\n")
                tcl_file.write("config_compile -pipeline_loops 0\n")

            tcl_file.write("csynth_design\n")
            tcl_file.write("export_design -format ip_catalog\n")
            tcl_file.write("exit\n")

    def _run_synthesis(self):
        """
        Executes the synthesis process using the Vitis HLS tool. Monitors the process to ensure
        it completes within the specified timeout period.
        """
        with self.LOCK:
            synthesis_process = subprocess.Popen(['vitis_hls', '-f', 'script.tcl', '-l', 'vitis_hls.log'])

        start_time = time.time()
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time >= self.SYNTHESIS_TIMEOUT_SEC or synthesis_process.poll() is not None:
                if synthesis_process.poll() is not None:
                    print("Synthesis completed!")
                try:
                    proc = psutil.Process(synthesis_process.pid)
                    for child_proc in proc.children(recursive=True):
                        child_proc.kill()
                    proc.kill()
                except psutil.NoSuchProcess:
                    print("Process already terminated!")
                break

    def _extract_synthesis_results(self, project_name):
        """
        Extracts synthesis results from the JSON data generated by Vitis HLS.

        Args:
            project_name (str): Name of the HLS project.

        Returns:
            dict: A dictionary containing latency and resource utilization metrics.
        """
        results = {}

        try:
            with open(os.path.join(project_name, 'solution1', 'solution1_data.json'), 'r') as json_file:
                synthesis_data = json.load(json_file)
        except FileNotFoundError:
            print("No synthesis data were found.")
            return results

        try:
            latency_cycles = int(synthesis_data["ClockInfo"]["Latency"])
        except KeyError:
            latency_cycles = -1
            print("Latency is undefined.")

        clock_period = float(synthesis_data["ClockInfo"]["ClockPeriod"])
        latency_ms = (latency_cycles * clock_period) / 1_000_000  # Convert to milliseconds

        module_info = synthesis_data['ModuleInfo']['Metrics'][self.TOP_LEVEL_FUNC_NAME]['Area']
        results['design_latency_msec'] = latency_ms
        results['bram_utilization'] = int(module_info.get("UTIL_BRAM", "0").strip('~') or 0)
        results['dsp_utilization'] = int(module_info.get("UTIL_DSP", "0").strip('~') or 0)
        results['ff_utilization'] = int(module_info.get("UTIL_FF", "0").strip('~') or 0)
        results['lut_utilization'] = int(module_info.get("UTIL_LUT", "0").strip('~') or 0)

        return results

    def _move_synthesis_output(self, project_name):
        """
        Moves the synthesis output directory and related files to the specified output directory.

        Args:
            project_name (str): Name of the HLS project.
        """
        output_project_dir = os.path.join(self.DIRECTORY_PATH, self.OUTPUT_DIR_NAME, project_name)
        os.makedirs(output_project_dir, exist_ok=True)
        os.rename(project_name, output_project_dir)
        os.rename("script.tcl", os.path.join(output_project_dir, "script.tcl"))
        os.rename("vitis_hls.log", os.path.join(output_project_dir, "vitis_hls.log"))

    def _save_experiment_results(self):
        """Writes the experiment results to a JSON file in the output directory."""
        with open(os.path.join(self.DIRECTORY_PATH, self.OUTPUT_DIR_NAME, "results.json"), "w") as result_file:
            json.dump(self.SYNTHESIS_RESULTS, result_file, indent=4, sort_keys=True)

    def run(self):
        """
        Executes the synthesis process, including reading the source code, removing directives,
        generating TCL scripts, running synthesis, and collecting results. All results are stored
        in the specified output directory.
        """
        self._read_source_code()
        self._remove_hls_directives()
        
        for is_original_code in [True]:
            enable_vitis_opts = self.VITIS_OPTIMIZATIONS_ENABLED
            code_variant = "original" if is_original_code else "no_directives"
            src_file_path = os.path.join(self.DIRECTORY_PATH, self.SRC_FILE_NAME) if is_original_code else os.path.join(self.DIRECTORY_PATH, "noDirectives.cpp")

            project_name = f"{code_variant}_{'wVO' if enable_vitis_opts else 'woVO'}"

            self._create_tcl_script(project_name, src_file_path, enable_vitis_opts)

            start_time = time.time()
            self._run_synthesis()
            end_time = time.time()
            synthesis_duration_sec = end_time - start_time

            self.SYNTHESIS_RESULTS[project_name] = self._extract_synthesis_results(project_name)
            self.SYNTHESIS_RESULTS[project_name]["synthesis_time_sec"] = synthesis_duration_sec

            self._move_synthesis_output(project_name)

        self._save_experiment_results()

    def get_synthesis_results(self):
        """
        Returns the results of the synthesis experiments.

        Returns:
            dict: A dictionary containing results for all synthesis experiments.
        """
        return self.SYNTHESIS_RESULTS
