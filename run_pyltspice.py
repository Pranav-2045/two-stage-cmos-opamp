from PyLTSpice import SimRunner, RawRead
import os

runner = SimRunner(simulator=r"C:\Users\prana\AppData\Local\Programs\ADI\LTspice\LTspice.exe")
raw_file, log_file = runner.run_now("final_opamp.cir")

print("Log file path:", log_file)
if log_file and os.path.exists(log_file):
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        print("=== SPICE LOG CONTENT ===")
        print(f.read())

print("Raw file path:", raw_file)
if raw_file and os.path.exists(raw_file):
    raw = RawRead(str(raw_file))
    print("=== OPERATING POINT DATA ===")
    for trace_name in raw.get_trace_names():
        val = raw.get_trace(trace_name).get_point(0)
        print(f"{trace_name}: {val:.6e}")
