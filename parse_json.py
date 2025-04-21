import json
from types import SimpleNamespace

def parse_jbmc_output(jbmc_output):
    status_messages = []
    passed = []
    failed = []
    traces = []
    json_output = json.loads(jbmc_output)
    for elem in json_output:
        if 'result' in elem.keys():
            for result in elem['result']:
                if 'V.assertion' in result['property']:
                        result['description'] = 'Assertion Check'
                if result['status'] == 'FAILURE':
                    failed.append(result)
                    if 'trace' in result.keys():
                        traces.append(result['trace'])
                        
                else:
                    passed.append(result)
        else:
            status_messages.append(elem)
    print("---------------------")
    print("Passed Tests: " + str(len(passed)) + "/" + str(len(passed) + len(failed)))
    print("Failed Tests: " + str(len(failed)) + ":")
    print_output(failed)
    print("---------------------")
    parse_traces(traces)
    
    return status_messages,passed, failed

def print_output(messages):
    for message in messages:
        if 'line' in message['sourceLocation'].keys():
            print(f"    {message['description']} : Line {message['sourceLocation']['line']}")
        else:
            print(f"    {message['description']}")        
            
def parse_traces(traces):
    for trace in traces:
        nondet_vars = []

        for step in trace:
            if step.get("stepType") == "assert-failed":
                print("Assertion Failed")
                break

            if step.get("stepType") != "assignment":
                continue

            # Capture var assignments from Verifier.nondetInt()
            var_name = step.get("lhs", "")
            val = step.get("value", {}).get("data", "<no data>")

            if "Verifier.nondetInt" in var_name and "#return_value" in var_name:
                # Store the variable assignment
                nondet_vars.append((var_name, val))
                print(f"{var_name} = {val}  # nondet value")

        # Print
        print("Captured nondet assignments:")
        for var, val in nondet_vars:
            print(f"  {var} = {val}")