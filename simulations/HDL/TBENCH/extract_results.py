'''
extract_results.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import os
import sys
import xml.etree.ElementTree as ET

#This script is entirely vibe-coded

# ANSI escape codes for formatting
BOLD      = "\033[1m"
RESET     = "\033[0m"
GREEN     = "\033[32m"
RED       = "\033[31m"
YELLOW    = "\033[33m"
CYAN      = "\033[36m"
VIOLET    = "\033[35m"

def extract_results_from_xml(filepath):
    """Parse an XML file and return module name and a list of test results.
       For each testcase, the simulation time is extracted from the sim_time_ns attribute,
       converted to a float and rounded to two decimal places.
    """
    tree = ET.parse(filepath)
    root = tree.getroot()
    results = []
    # Loop over testsuites; assume simulation time is stored as attribute "sim_time_ns"
    for testsuite in root.findall("testsuite"):
        for testcase in testsuite.findall("testcase"):
            test_name = testcase.get("name")
            classname = testcase.get("classname")
            # Get simulation time from the testcase and convert to float rounded to 2 decimals.
            raw_time = testcase.get("sim_time_ns", testsuite.get("sim_time_ns"))
            try:
                sim_time = f"{float(raw_time):.1f}"
            except (TypeError, ValueError):
                sim_time = raw_time
            failure_element = testcase.find("failure")
            status = "FAIL" if failure_element is not None else "PASS"
            message = failure_element.get("message", "") if failure_element is not None else ""
            results.append((classname + "." + test_name, status, sim_time, message))
    
    # Get module name from the parent folder of the XML file
    module_name = os.path.basename(os.path.dirname(filepath))
    return module_name, results

def extract_all_results(root_folder):
    # Print header only once for all modules.
    print(f"{BOLD}{CYAN}Compilation of all results{RESET}:")
    header = "{:<50} {:<8} {:>13}      {:<}".format("Test", "Status", "Sim Time (ns)", "Message")
    print(f"{BOLD}{header}{RESET}")
    print("-" * len(header))
    
    for dirpath, dirnames, filenames in os.walk(root_folder):
        if os.path.abspath(dirpath) == os.path.abspath(root_folder):
            continue
        module_results = None
        for filename in filenames:
            if filename == "cocotb_results.xml":
                filepath = os.path.join(dirpath, filename)
                try:
                    module_name, results = extract_results_from_xml(filepath)
                    module_results = (module_name, results)
                except Exception as e:
                    print(f"{BOLD}{RED}Error processing {filepath}: {e}{RESET}")
        if module_results:
            module_name, results = module_results
            print(f"{BOLD}{VIOLET}Results for module: {module_name}{RESET}")
            for test, status, sim_time, message in results:
                # Remove module part if present
                short_test = test.split(".", 1)[1] if "." in test else test
                if status == "PASS":
                    status_formatted = f"{BOLD}{GREEN}{status}{RESET}"
                else:
                    status_formatted = f"{BOLD}{RED}{status}{RESET}"
                print("{:<50} {:<8} {:>13}      {:<}".format(short_test, status_formatted, sim_time, message))
        else:
            rel_path = os.path.relpath(dirpath, root_folder)
            print(f"{BOLD}{RED}ERROR! : No XML results file found in folder: {rel_path}. This is likely due to an error during {rel_path} module's or testcase's execution!{RESET}")
        print("")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_results.py <output_folder>")
        sys.exit(1)
    output_folder = sys.argv[1]
    extract_all_results(output_folder)