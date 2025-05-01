import re
import json

def _get_assignment_var(step, trace):
    if not step['hidden']:
        if step['lhs'].startswith('arg'):
            return _get_variable_type(step, trace)
    return ''

def _get_variable_type(step, trace):
    if step['value']['type'].startswith('struct java::array'):
        return f"       {_parse_array_type(step['value']['type'])} {step['lhs']} = {_get_array_value(step, trace)};"
    return f"       {step['value']['type']} {step['lhs']} = {step['value']['data']};"
    
def _parse_array_type(array_def_string):
    array_type = re.search(r'struct java::array\[(.*)\]', array_def_string).groups()[0]
    return f'{array_type}[]'

def _add_function_to_code(function_details):
    return f"       {function_details['name']}({','.join(function_details['args'])});"

def _get_array_value(elem, trace):
        data = []
        if elem['value']['data'].startswith('dynamic_object'):
            dynamic_object = elem['value']['data']
            for elem2 in trace:
                if elem2['stepType'] != 'assignment':
                    continue
                if elem2['lhs'] == f'{dynamic_object}.data' and elem2['value']['data'].startswith('dynamic_object'):
                    dynamic_data_obj = elem2['value']['data']
                    for elem3 in trace:
                        if elem3['stepType'] != 'assignment':
                            continue
                        if elem3['lhs'] == dynamic_data_obj:
                            data = [x['value']['data'] for x in elem3['value']['elements']]
            return f"{{ {",".join(data)} }}"
        else:
            return elem['value']['data']

def parse_jbmc_without_nondet(traces):
    counterexamples = []
    for trace in traces:
        functions = []
        code = []
        for step in trace:
            if step['stepType'] == 'assignment': 
                if step['assignmentType'] == 'variable':
                    assignment = _get_assignment_var(step, trace)
                    if assignment != '':
                        code.append(assignment)
                elif step['assignmentType'] == 'actual-parameter':
                    if len(functions):
                        functions[0]['args'].append(step['lhs'])
                        if functions[0]['args_count'] == len(functions[0]['args']):
                            code.append(_add_function_to_code(functions[0]))
            if step['stepType'] == 'function-call':
                function_signature = step['function']['displayName'].split('(')
                if len(function_signature) < 2:
                    continue
                function_details = {}
                function_details['name'] = function_signature[0]
                function_details['args_count'] = len(function_signature[1].split(','))
                function_details['args'] = []
                functions.append(function_details)
        counterexamples.append(code)
    return counterexamples

def parse_nondet_traces(traces):
    counter_examples = []
    for trace in traces:
        nondet_vars = []
        last_known_line = "<no line>"

        for step in trace:
            # Save the most recent line number if this step has it
            source_line = step.get("sourceLocation", {}).get("line")
            if source_line is not None:
                last_known_line = source_line

            if step.get("stepType") == "assert-failed":
                print("Assertion Failed")
                break

            if step.get("stepType") != "assignment":
                continue
                
            var_name = step.get("lhs", "")
            val = step.get("value", {}).get("data", "<no data>")

            if "Verifier.nondetInt" in var_name and "#return_value" in var_name:
                nondet_vars.append((var_name, val, last_known_line))
                print(f"{var_name} = {val}  # nondet value (line {last_known_line})")

        print("Captured nondet assignments:")
        for var, val, line in nondet_vars:
            print(f"  {var} = {val}  (line {line})")
        counter_examples.append(nondet_vars)
    return counter_examples