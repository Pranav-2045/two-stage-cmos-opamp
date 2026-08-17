import os
from PyLTSpice import SimRunner, RawRead

def run_stage2():
    sim_path = r"C:\Users\prana\AppData\Local\Programs\ADI\LTspice\LTspice.exe"
    runner = SimRunner(simulator=sim_path if os.path.exists(sim_path) else None)
    
    print("Running Two-Stage Op-Amp DC Operating Point Analysis (stage2.cir)...")
    raw_file, log_file = runner.run_now("stage2.cir")
    
    if not raw_file or not os.path.exists(raw_file):
        print("Simulation failed. Check log file:", log_file)
        return
        
    raw = RawRead(str(raw_file))
    traces = {t.lower(): raw.get_trace(t).get_point(0) for t in raw.get_trace_names()}
    
    print("\n========================================================")
    print("    TWO-STAGE OP-AMP DC OPERATING POINT (stage2.cir)    ")
    print("========================================================")
    
    # Node Voltages
    print("\n--- Key Node Voltages ---")
    nodes = [
        ("V(vdd)", "Positive Supply"),
        ("V(vbias)", "Bias Generator Node"),
        ("V(vtail)", "Stage 1 Tail Node"),
        ("V(vout_stage1)", "Stage 1 Output / M11 Gate"),
        ("V(out)", "Stage 2 Output Node"),
    ]
    for n, desc in nodes:
        val = traces.get(n.lower(), None)
        if val is not None:
            print(f"  {n:<16} : {val:8.4f} V  ({desc})")
            
    # Branch Currents & Power
    print("\n--- Branch Currents & Total Power ---")
    currents = [
        ("I(Iref)", "Reference Branch"),
        ("Id(M0)", "Stage 1 Tail Branch (I0)"),
        ("Id(M11)", "Stage 2 Driver Branch (I1)"),
    ]
    total_curr = 0.0
    for c, desc in currents:
        val = traces.get(c.lower(), None)
        if val is not None:
            curr_abs = abs(val)
            total_curr += curr_abs
            print(f"  {c:<16} : {curr_abs*1e6:8.2f} µA ({desc})")
            
    vdd_val = traces.get('v(vdd)', 1.8)
    p_diss = total_curr * vdd_val
    print(f"  {'Total Supply Current':<16} : {total_curr*1e6:8.2f} µA")
    print(f"  {'Total Power Diss':<16} : {p_diss*1e6:8.2f} µW (Spec <= 500 µW: {'PASS' if p_diss <= 500e-6 else 'FAIL'})")
    
    # Saturation checks for all 8 transistors
    vtail = traces.get('v(vtail)', 0)
    vbias = traces.get('v(vbias)', 0)
    vout1 = traces.get('v(vout1)', 0)
    vout_s1 = traces.get('v(vout_stage1)', 0)
    vout = traces.get('v(out)', 0)
    vdd = vdd_val
    
    vth_n = 0.366
    vth_p = 0.391
    
    print("\n--- Transistor Saturation Verification (All 8 Devices) ---")
    devices = [
        ("Mbias", vbias, vbias - vth_n, "NMOS"),
        ("M0", vtail, vbias - vth_n, "NMOS"),
        ("M1", vout1 - vtail, 1.2 - vtail - vth_n, "NMOS"),
        ("M2", vout_s1 - vtail, 1.2 - vtail - vth_n, "NMOS"),
        ("M3", vdd - vout1, (vdd - vout1) - vth_p, "PMOS"),
        ("M4", vdd - vout_s1, (vdd - vout1) - vth_p, "PMOS"),
        ("M11", vdd - vout, (vdd - vout_s1) - vth_p, "PMOS"),
        ("M12", vout, vbias - vth_n, "NMOS"),
    ]
    
    for name, vds, vov, dtype in devices:
        sat = vds > vov and vov > 0
        vds_lbl = "Vsd" if dtype == "PMOS" else "Vds"
        print(f"  {name:<6} ({dtype}): {vds_lbl}={vds:.3f}V, Vov={vov:.3f}V -> {'SATURATED (PASS)' if sat else 'TRIODE (FAIL)'}")
        
    print("========================================================\n")

if __name__ == "__main__":
    run_stage2()
