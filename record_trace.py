import sys, re, json 
from collections import defaultdict

objdump_file, cfg_file = sys.argv[1], sys.argv[2]
"""
for every line in the program
    if trace call 
        save in map as callsite name -> trace_addr + 5 
    if function start 
        save in map as function name -> addr 

for every pc, callee pair in file:
    add function name to callsite list in map

print callsite list 
"""

def scan_objdump(objdump_file):

    """
    Map from address to callsite ID. For example:
    {0x2018d0: "foo_call:0", 
     0x2019d0: "foo_call:1"}
    """
    callsite_names = {}

    """
    Map from address to start of function. For example:

    {0x2009d4: "foo", 
     0x200849: "bar"}
    """
    func_names = {}

    function_start_pattern = re.compile(r'([0-9a-f]+)\s<([\w.]+)>:\s*')

    current_function = "" 
    callsites_in_func = 0 
    function_addr = 0

    with open(objdump_file, 'r') as f:
        contents = f.read().split('\n')
        for line in contents:
            if function_start_pattern.match(line.strip()):
                pattern_match = function_start_pattern.match(line.strip())
                function_addr = int(pattern_match.group(1), 16)
                current_function = pattern_match.group(2)
                callsites_in_func = 0

                func_names[function_addr] = current_function
            elif "callq" in line and "__trace" in line:
                addr, _ = line.split(':')
                callsite_addr = int(addr, 16) + 5 # call instrs are 5 bytes long 

                callsite_names[callsite_addr] = "{}:{}".format(current_function, callsites_in_func)
                callsites_in_func += 1 

    return callsite_names, func_names



def build_cfg(cfg_file):
    """
    Map from callsite ID to functions called from this callsite. 
    For example: 

    {
        "foo_call:0" : ["foo", "bar"], 
        "foo_call:1" : ["bar", "baz"]
    }
    """
    cfg = defaultdict(list)

    callsite_names, func_names = scan_objdump(objdump_file)

    with open(cfg_file, 'r') as f:
        contents = f.read().split('\n')
        for i in range(1, len(contents), 2):
            pc_line = contents[i - 1]
            callee_line = contents[i]

            _, pc = pc_line.split(':')
            _, callee = callee_line.split(':')

            callsite_name = callsite_names[int(pc, 16)]
            func_name = func_names[int(callee, 16)]

            cfg[callsite_name].append(func_name)

    print(json.dumps(cfg, sort_keys=True, indent=4))




def record_objdump():
    current_function = "" 
    callsites_in_func = 0 

    total = 0

    num_callsites_per_func = {}

    function_start_pattern = re.compile(r'[0-9a-f]+\s<([\w.]+)>:\s*')

    with open(input_file, 'r') as f:
        contents = f.read().split('\n')
        for line in contents:
            if function_start_pattern.match(line.strip()):
                if current_function != "" and callsites_in_func > 0:
                    num_callsites_per_func[current_function] = callsites_in_func 
                    total += callsites_in_func

                current_function = function_start_pattern.match(line.strip()).group(1)
                callsites_in_func = 0
            elif "callq" in line and "__trace" in line:
                callsites_in_func += 1


    for key in num_callsites_per_func:
        num_callsites_per_func[key] = "{} callsites".format(num_callsites_per_func[key])
    print(json.dumps(num_callsites_per_func, sort_keys=True, indent=0))

    print(total)


def record_llvm():
    current_function = "" 
    callsites_in_func = 0

    total = 0 

    num_callsites_per_func = {}

    with open(input_file, 'r') as f:
        contents = f.read().split('\n')
        for line in contents:
            line = line.strip()
            if "define" in line and "@" in line and "(" in line:
                if current_function != "" and callsites_in_func > 0:
                    num_callsites_per_func[current_function] = callsites_in_func 
                    total += callsites_in_func

                at_ind = line.index("@")
                open_ind = line.index("(")
                current_function = line[at_ind + 1:open_ind]

                callsites_in_func = 0
            elif "call void @__trace" in line:
                callsites_in_func += 1


    for key in num_callsites_per_func:
        num_callsites_per_func[key] = "{} callsites".format(num_callsites_per_func[key])
    print(json.dumps(num_callsites_per_func, sort_keys=True, indent=0))

    print(total)


build_cfg(cfg_file)