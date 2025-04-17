import json
from types import SimpleNamespace

def parse_jbmc_output(jbmc_output):
    status_messages = []
    passed = []
    failed = []
    json_output = json.loads(jbmc_output)
    for elem in json_output:
        if 'result' in elem.keys():
            for result in elem['result']:
                if 'V.assertion' in result['property']:
                        result['description'] = 'Assertion Check'
                if result['status'] == 'FAILURE':
                    failed.append(result)
                    # if 'trace' in result.keys():
                        # with open('sample_output.json', 'w') as f:
                        #     json.dump(result['trace'], f, indent=4)
                else:
                    passed.append(result)
        else:
            status_messages.append(elem)
    print("Passed Tests: \n")
    print_output(passed)
    print("\nFailed Tests: \n")
    print_output(failed)
    return status_messages,passed, failed

def print_output(messages):
    for message in messages:
        if 'line' in message['sourceLocation'].keys():
            print(f'    {message['description']} : Line {message['sourceLocation']['line']}')
        else:
            print(f'    {message['description']}')        