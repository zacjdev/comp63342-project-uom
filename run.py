import argparse
import subprocess
import os
import sys
import re
import json
import parse_json
from pathlib import Path

# Compile a Java file into the given output directory.
def compile_java(java_file, output_dir, classpath):
    # Make sure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    try:
        # Run javac to compile the Java file with the specified classpath
        subprocess.run(["javac", "-d", output_dir, "-cp", classpath,java_file], check=True)
    except subprocess.CalledProcessError:
        print("Error: Failed to compile Java file.")
        sys.exit(1)
        
# Extract the fully qualified main class name from a Java file.
def extract_main_class(java_file):
    package_name = None
    with open(java_file, "r") as f:
        for line in f:
            # Look for the package declaration
            match = re.match(r'\s*package\s+([\w\.]+)\s*;', line)
            if match:
                package_name = match.group(1)
                break
    # If no package declaration is found, use the default package
    class_name = os.path.splitext(os.path.basename(java_file))[0]
    # If a package name was found, prepend it to the class name
    return f"{package_name}.{class_name}" if package_name else class_name


# Run JBMC on the compiled Java class and save the output as JSON.
def run_jbmc(jbmc_path, classpath, java_class, output_file):
    try:
        # Run JBMC with the specified classpath and Java class
        result = subprocess.run(
            [jbmc_path, "--classpath", classpath, java_class, "--json-ui"], capture_output=True, text=True
        ).stdout.strip()
        return result
    
    except Exception as e:
        print(f"Failed to run JBMC: {e}")
        sys.exit(1)
        
# Parse the JBMC output and print the results.
def parse_jbmc_output(result, output_file):

    status, passed, failed = parse_json.parse_jbmc_output(result)
    output_data = {
        "status_messages": status,
        "passed": passed,
        "failed": failed,
    }
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=4)

    print(f"JBMC output saved to {output_file}")

# Main function
if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Compile and Run JBMC on a Java file.")
    parser.add_argument("java_file", help="Path to the Java file", type=Path)
    parser.add_argument("--jbmc", default='jbmc',help="Path to the JBMC executable", type=Path)
    parser.add_argument("--classpath",default='', help="Classpath", type=Path)
    parser.add_argument("--output", default="jbmc_output.json", help="JSON output file (default: jbmc_output.json)")
    
    # Parse the command-line arguments
    args = parser.parse_args()
    output_dir = "classes"
    
    # Compile the Java file
    print(f"Compiling {args.java_file}...")
    compile_java(args.java_file, output_dir, args.classpath)
    # Extract the main class name
    print(f"Extracting main class from {args.java_file}...")
    java_class = extract_main_class(args.java_file)
    print(f"Detected main class: {java_class}")
    
    # Run JBMC on the compiled Java class
    print(f"Running JBMC on {java_class}...")
    result = run_jbmc(args.jbmc, output_dir, java_class, args.output)
    # Parse the JBMC output and save it to a JSON file
    print(f"Parsing JBMC output...")
    parse_jbmc_output(result, args.output)
    print("JBMC analysis completed.")
