import argparse
import subprocess
import os
import sys
import re
import json
import parse_json
from pathlib import Path

def compile_java(java_file, output_dir, classpath):
    """Compile a Java file into the given output directory."""
    os.makedirs(output_dir, exist_ok=True)
    try:
        subprocess.run([
            "javac", "-d", output_dir, "-cp", classpath,java_file
        ], check=True)
    except subprocess.CalledProcessError:
        print("Error: Failed to compile Java file.")
        sys.exit(1)

def extract_main_class(java_file):
    """Extract the fully qualified main class name from a Java file."""
    package_name = None
    with open(java_file, "r") as f:
        for line in f:
            match = re.match(r'\s*package\s+([\w\.]+)\s*;', line)
            if match:
                package_name = match.group(1)
                break
    
    class_name = os.path.splitext(os.path.basename(java_file))[0]
    return f"{package_name}.{class_name}" if package_name else class_name

def run_jbmc(jbmc_path, classpath, java_class, output_file):
    """Run JBMC on the given compiled Java class and save output as JSON."""
    try:
        result = subprocess.run(
            [jbmc_path, "--classpath", classpath, java_class, "--json-ui"],
            capture_output=True,
            text=True
        )

        status, passed, failed = parse_json.parse_jbmc_output(result.stdout.strip())

        output_data = {
            "status_messages": status,
            "passed": passed,
            "failed": failed,
            "stderr": result.stderr.strip(),
            "return_code": result.returncode
        }
        
        with open(output_file, "w") as f:
            json.dump(output_data, f, indent=4)
        
        print(f"JBMC output saved to {output_file}")
    
    except Exception as e:
        print(f"Failed to run JBMC: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile and Run JBMC on a Java file.")
    parser.add_argument("java_file", help="Path to the Java file", type=Path)
    parser.add_argument("--jbmc", default='jbmc',help="Path to the JBMC executable", type=Path)
    parser.add_argument("--classpath",default='', help="Classpath", type=Path)
    parser.add_argument("--output", default="jbmc_output.json", help="JSON output file (default: jbmc_output.json)")
    
    args = parser.parse_args()
    print(args)

    output_dir = "classes"
    
    compile_java(args.java_file, output_dir, args.classpath)
    java_class = extract_main_class(args.java_file)
    print(f"Detected main class: {java_class}")
    
    run_jbmc(args.jbmc, output_dir, java_class, args.output)
