from PyLTSpice import SimRunner
import os

runner = SimRunner(simulator=r"C:\Users\prana\AppData\Local\Programs\ADI\LTspice\LTspice.exe")
raw_file, log_file = runner.run_now("pz_analysis.cir")

print("Log file path:", log_file)
if log_file and os.path.exists(log_file):
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        print("=== SPICE PZ LOG CONTENT ===")
        print(f.read())
