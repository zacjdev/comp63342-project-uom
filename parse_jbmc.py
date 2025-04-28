import json
import parse_trace
import java_gen

def parse_jbmc_output(jbmc_output, parse_nondet, java_file_path):
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
    if parse_nondet:
        counterexample = parse_trace.parse_nondet_traces(traces)
        java_gen.gen_nondet_code(counterexample, java_file_path)
    else: 
        counterexample = parse_trace.parse_jbmc_without_nondet(traces)
        java_gen.gen_code(counterexample, java_file_path)
    return status_messages,passed, failed

def print_output(messages):
    for message in messages:
        if 'line' in message['sourceLocation'].keys():
            print(f"    {message['description']} : Line {message['sourceLocation']['line']}")
        else:
            print(f"    {message['description']}")        

