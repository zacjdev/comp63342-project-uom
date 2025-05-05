import argparse
import subprocess
import os
import sys
import re
import json
import parse_jbmc
from java_gen import gen_nondet_code, gen_code
from pathlib import Path
import parse_trace

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
            [jbmc_path, "--classpath", classpath, java_class, "--json-ui", '--unwind', '10'], capture_output=True, text=True
        ).stdout.strip()
        return result
    
    except Exception as e:
        print(f"Failed to run JBMC: {e}")
        sys.exit(1)
        
# Parse the JBMC output and print the results.
def parse_jbmc_output(result, output_file, parse_nondet, java_file_path):

    status, passed, failed = parse_jbmc.parse_jbmc_output(result, parse_nondet, java_file_path)
    output_data = {
        "status_messages": status,
        "passed": passed,
        "failed": failed,
    }
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=4)

    print(f"JBMC output saved to {output_file}")

# Driver function for each file
def compile_and_execute_jbmc(java_file, args):

    # Compile the Java file
    print(f"Compiling {java_file}...")
    compile_java(java_file, output_dir, args.classpath)
    # Extract the main class name
    print(f"Extracting main class from {java_file}...")
    java_class = extract_main_class(java_file)
    print(f"Detected main class: {java_class}")
    
    if args.entry != '':
        print(f"Entry point: {args.entry}")
        java_class = java_class + '.' + args.entry

    # Run JBMC on the compiled Java class
    print(f"Running JBMC on {java_class}...")

    result = run_jbmc(args.jbmc, output_dir, java_class, args.output)
    # Parse the JBMC output and save it to a JSON file
    print(f"Parsing JBMC output...")
    print(f"Nondet flag: {args.nondet}")

    parse_jbmc_output(result, args.output, args.nondet, java_file)
    print("JBMC analysis completed.")

# Main function
if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Compile and Run JBMC on a Java file.")
    parser.add_argument("java_file", help="Path to the Java file", type=Path)
    parser.add_argument("--jbmc", default='jbmc',help="Path to the JBMC executable", type=Path)
    parser.add_argument("--classpath",default='', help="Classpath", type=Path)
    parser.add_argument("--output", default="jbmc_output.json", help="JSON output file (default: jbmc_output.json)")
    parser.add_argument("--nondet", default=False, help='Enable flag if code contains nondet calls', action='store_true')
    parser.add_argument("--entry", default='', help='Entry point')
    
    # Parse the command-line arguments
    args = parser.parse_args()
    output_dir = "classes"

    if args.java_file.is_dir():
        print(sorted(args.java_file.rglob('*.java')))
        for java_file in args.java_file.rglob('*.java'):
            compile_and_execute_jbmc(java_file, args)
    else:
        compile_and_execute_jbmc(args.java_file, args)

    
