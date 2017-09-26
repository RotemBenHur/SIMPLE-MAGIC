# SIMPLE-MAGIC
SIMPLE MAGIC: Synthesis and In-memory MaPping of Logic Execution for Memristor Aided loGIC

## Dependencies
In order to use SIMPLE-MAGIC, you will need a Linux machine with:
1. Python 2.7
2. [Z3](https://github.com/Z3Prover/z3): Run the following commands to install it:
```sh
git clone --recursive https://github.com/Z3Prover/z3.git
cd z3
python scripts/mk_make.py --python
cd build
make
make install
```
3. [ABC Synthesis Tool](https://bitbucket.org/alanmi/abc)

## Manual
1. Configure: in the file simple_conf.cfg you will find the following content:
```ini
[input_output]
input_path=cm138a.blif
; input_format can get one of the values: verilog, blif
input_format=blif
output_path=cm138a_output

[optimization]
; parameter can get one of the values: latency, area, energy.
parameter=area

; the latency value is used only when optimizing area or energy.
latency=20

[abc]
abc_dir_path=/home/adi/abc/alanmi-abc-eac02745facf

; gates can get one of the values: not_nor2, not_nor2_nor3.
gates=not_nor2

[Z3]
Z3_path=/usr/bin/z3

```
Change the parameters according to your needs.

2. Run:
```sh
python simple_main.py
```
