
import os

def gen_code(code_arr, java_file_path):
    for index, code in enumerate(code_arr):
        final_code = []
        classname = f"{get_classname_from_path(java_file_path)}_counterexample_{index}"
        final_code.append(f"public class {classname} {{")
        final_code.append(f"    public static void main() {{")
        final_code += code
        final_code.append(f'    }}')
        final_code.append('}')
        write_code_to_file(final_code, classname, java_file_path)

def gen_nondet_code(counterexamples, java_file_path): 
    benchmark_code = read_example(java_file_path)
    classname = get_classname_from_path(java_file_path)
    for counterexample in counterexamples:
        for i in range(len(benchmark_code)):
            if f"public class {classname}" in benchmark_code[i]:
                benchmark_code[i] = benchmark_code[i].replace(classname, classname +"_counterexample")
            if "Verifier.nondetInt()" in benchmark_code[i]:
                benchmark_code[i] = benchmark_code[i].replace("Verifier.nondetInt()", counterexample[0][1])
        classname = f'{classname}_counterexample'
        write_code_to_file(benchmark_code, classname, java_file_path)

def write_code_to_file(benchmark_code, classname, java_file_path):
    with open(f"{java_file_path.parent}/{classname}.java", "w") as exmple_file:
        exmple_file.write("\n".join(benchmark_code))

def get_classname_from_path(java_file_path):
    filename = os.path.basename(java_file_path)
    classname = filename.split('.')[0]
    return classname

def get_type(var):
    return ''

def read_example(java_filename):
    code = []
    with open(java_filename, "r") as f:
        for line in f:
            if "import org.sosy_lab.sv_benchmarks.Verifier;" in line:
                continue
            code.append(line)
    return code