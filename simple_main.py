import ConfigParser
import os
import tempfile
import Netlist_to_Z3_latency_nor2

def main():

    # Read configuration parameters
    config = ConfigParser.ConfigParser()
    config.readfp(open('simple_conf.cfg'))
    input_path = config.get('input_output', 'input_path')
    input_format = config.get('input_output', 'input_format')
    abc_dir_path = config.get('abc', 'abc_dir_path')
    Z3_path = config.get('Z3', 'Z3_path')
    output_path = config.get('input_output', 'output_path')

    abc_exe_path = os.path.join(abc_dir_path, "abc")
    abc_rc_path = os.path.join(abc_dir_path, "abc.rc")

    # Create abc script
    abc_script = file('abc_script_template.abc', 'rb').read()
    abc_script = abc_script.replace('abc_rc_path', abc_rc_path)
    abc_script = abc_script.replace('input.blif', input_path)
    if input_format == 'verilog':
        abc_script = abc_script.replace('read_blif', 'read_verilog')
    abc_script = abc_script.replace('lib.genlib', 'mcnc1_nor2.genlib')
    abc_output_path = tempfile.mktemp()
    abc_script = abc_script.replace('output.v', abc_output_path)

    # Run abc script
    abc_script_path = tempfile.mktemp()
    file(abc_script_path, "wb").write(abc_script)
    os.system('%s -f "%s"' % (abc_exe_path, abc_script_path))

    # Create constraints file (smt2 format)
    
    Z3_input = Netlist_to_Z3_latency_nor2.netlist_to_z3(abc_output_path)    
    
    # Run Z3
    os.system('%s -smt2 %s > %s' % (Z3_path, Z3_input, output_path))

    # Clean files
    os.remove(abc_script_path)
    os.remove(abc_output_path)
    os.remove(Z3_input)

if __name__ == "__main__":
    main()
