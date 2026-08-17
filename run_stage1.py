import os
from PyLTSpice import SimRunner, RawRead

def run_stage1():
    sim_path = r"C:\Users\prana\AppData\Local\Programs\ADI\LTspice\LTspice.exe"
    runner = SimRunner(simulator=sim_path if os.path.exists(sim_path) else None)
    
    print("Running Stage 1 DC Operating Point Analysis (stage1.cir)...")
    raw_file, log_file = runner.run_now("stage1.cir")
    
    if not raw_file or not os.path.exists(raw_file):
        print("Simulation failed. Check log file:", log_file)
        return
        
    raw = RawRead(str(raw_file))
    traces = {t.lower(): raw.get_trace(t).get_point(0) for t in raw.get_trace_names()}
    
    print("\n========================================================")
    print("      STAGE 1 DC OPERATING POINT SIMULATION RESULTS      ")
    print("========================================================")
    
    # Node Voltages
    print("\n--- Node Voltages ---")
    nodes = [
        ("V(vdd)", "Positive Supply"),
        ("V(vbias)", "Bias Generator Node"),
        ("V(vtail)", "Tail Node (M0 Drain)"),
        ("V(vinn)", "Inverting Input"),
        ("V(vinp)", "Non-Inverting Input"),
        ("V(vout1)", "M1 Drain / M3 Gate & Drain"),
        ("V(vout_stage1)", "Stage 1 Output (M2 Drain)"),
    ]
    for n, desc in nodes:
        val = traces.get(n.lower(), None)
        if val is not None:
            print(f"  {n:<16} : {val:8.4f} V  ({desc})")
            
    # Branch Currents
    print("\n--- Transistor & Branch Currents ---")
    currents = [
        ("I(Iref)", "Reference Current"),
        ("Id(Mbias)", "Mbias Current"),
        ("Id(M0)", "Tail Current (I0)"),
        ("Id(M1)", "Input Pair M1 Current"),
        ("Id(M2)", "Input Pair M2 Current"),
        ("Id(M3)", "Load M3 Current"),
        ("Id(M4)", "Load M4 Current"),
    ]
    for c, desc in currents:
        val = traces.get(c.lower(), None)
        if val is not None:
            print(f"  {c:<16} : {abs(val)*1e6:8.2f} µA ({desc})")
            
    # Saturation checks
    vtail = traces.get('v(vtail)', 0)
    vbias = traces.get('v(vbias)', 0)
    vout1 = traces.get('v(vout1)', 0)
    vout_s1 = traces.get('v(vout_stage1)', 0)
    vdd = traces.get('v(vdd)', 1.8)
    
    vth_n = 0.366
    vth_p = 0.391
    
    print("\n--- Transistor Saturation Verification ---")
    # Mbias: Vds = Vbias, Vgs = Vbias
    sat_mbias = vbias > (vbias - vth_n)
    print(f"  Mbias : Vds={vbias:.3f}V, Vgs-Vth={vbias-vth_n:.3f}V -> {'SATURATED (PASS)' if sat_mbias else 'TRIODE (FAIL)'}")
    
    # M0: Vds = Vtail, Vgs = Vbias
    sat_m0 = vtail > (vbias - vth_n)
    print(f"  M0    : Vds={vtail:.3f}V, Vgs-Vth={vbias-vth_n:.3f}V -> {'SATURATED (PASS)' if sat_m0 else 'TRIODE (FAIL)'}")
    
    # M1: Vds = Vout1 - Vtail, Vgs = 1.2 - Vtail
    vds_m1 = vout1 - vtail
    vov_m1 = 1.2 - vtail - vth_n
    print(f"  M1    : Vds={vds_m1:.3f}V, Vgs-Vth={vov_m1:.3f}V -> {'SATURATED (PASS)' if vds_m1 > vov_m1 else 'TRIODE (FAIL)'}")
    
    # M2: Vds = Vout_s1 - Vtail, Vgs = 1.2 - Vtail
    vds_m2 = vout_s1 - vtail
    vov_m2 = 1.2 - vtail - vth_n
    print(f"  M2    : Vds={vds_m2:.3f}V, Vgs-Vth={vov_m2:.3f}V -> {'SATURATED (PASS)' if vds_m2 > vov_m2 else 'TRIODE (FAIL)'}")
    
    # M3: Vsd = Vdd - Vout1, Vsg = Vdd - Vout1
    vsd_m3 = vdd - vout1
    vov_m3 = (vdd - vout1) - vth_p
    print(f"  M3    : Vsd={vsd_m3:.3f}V, Vsg-Vth={vov_m3:.3f}V -> {'SATURATED (PASS)' if vsd_m3 > vov_m3 else 'TRIODE (FAIL)'}")
    
    # M4: Vsd = Vdd - Vout_s1, Vsg = Vdd - Vout1
    vsd_m4 = vdd - vout_s1
    vov_m4 = (vdd - vout1) - vth_p
    print(f"  M4    : Vsd={vsd_m4:.3f}V, Vsg-Vth={vov_m4:.3f}V -> {'SATURATED (PASS)' if vsd_m4 > vov_m4 else 'TRIODE (FAIL)'}")
    
    print("========================================================\n")

if __name__ == "__main__":
    run_stage1()
