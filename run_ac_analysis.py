"""
Phase 5: AC Analysis - Extract Bode Plot Data, DC Gain, GBW, Phase Margin
Runs LTspice simulation and parses the .raw file to extract AC performance metrics.
"""
from PyLTSpice import SimRunner, RawRead
import numpy as np
import os

print("=" * 70)
print("  PHASE 5: AC OPEN-LOOP BODE PLOT ANALYSIS")
print("=" * 70)

# Run simulation
runner = SimRunner(simulator=r"C:\Users\prana\AppData\Local\Programs\ADI\LTspice\LTspice.exe")
raw_file, log_file = runner.run_now("ac_analysis.cir")

# Print log
print("\n--- SPICE Log ---")
if log_file and os.path.exists(log_file):
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        log_content = f.read()
        print(log_content)
        if "error" in log_content.lower() or "abort" in log_content.lower():
            print("ERROR: Simulation failed!")
            exit(1)

# Parse raw file
if not raw_file or not os.path.exists(raw_file):
    print("ERROR: Raw file not found!")
    exit(1)

raw = RawRead(str(raw_file))
print("\n--- Available Traces ---")
trace_names = raw.get_trace_names()
for t in trace_names:
    print(f"  {t}")

# Get frequency and output voltage
freq_trace = raw.get_trace("frequency")
freq = np.array([freq_trace.get_point(i) for i in range(len(freq_trace))])
freq_real = np.abs(freq)

# Get output voltage (complex)
out_trace = raw.get_trace("V(out)")
vout = np.array([out_trace.get_point(i) for i in range(len(out_trace))])

# Calculate gain magnitude in dB and phase in degrees
gain_mag = np.abs(vout)
gain_db = 20 * np.log10(gain_mag + 1e-30)  # avoid log(0)
phase_deg = np.angle(vout, deg=True)

# ===== EXTRACT KEY METRICS =====

# 1. DC Gain (at lowest frequency)
dc_gain_db = gain_db[0]
dc_gain_vv = gain_mag[0]
print(f"\n{'=' * 70}")
print(f"  KEY AC PERFORMANCE METRICS")
print(f"{'=' * 70}")
print(f"\n  1. DC Gain:")
print(f"     |A_o| = {dc_gain_db:.2f} dB  ({dc_gain_vv:.1f} V/V)")
print(f"     Target: >= 70 dB  -->  {'PASS' if dc_gain_db >= 70 else 'FAIL - NEEDS TUNING'}")

# 2. Unity-Gain Frequency (0dB crossover = GBW)
gbw_freq = None
for i in range(len(gain_db) - 1):
    if gain_db[i] >= 0 and gain_db[i + 1] < 0:
        # Linear interpolation for more accuracy
        f1, f2 = freq_real[i], freq_real[i + 1]
        g1, g2 = gain_db[i], gain_db[i + 1]
        gbw_freq = f1 * (f2 / f1) ** (g1 / (g1 - g2))
        break

if gbw_freq:
    print(f"\n  2. Unity-Gain Bandwidth (GBW):")
    print(f"     f_u = {gbw_freq / 1e6:.2f} MHz")
    print(f"     Target: >= 50 MHz  -->  {'PASS' if gbw_freq >= 50e6 else 'FAIL - NEEDS TUNING'}")
else:
    print(f"\n  2. Unity-Gain Bandwidth: NOT FOUND (gain never crosses 0dB)")

# 3. Phase Margin (phase at 0dB crossover + 180)
pm = None
if gbw_freq:
    # Find phase at GBW frequency
    for i in range(len(freq_real) - 1):
        if freq_real[i] <= gbw_freq <= freq_real[i + 1]:
            # Interpolate phase
            ratio = np.log(gbw_freq / freq_real[i]) / np.log(freq_real[i + 1] / freq_real[i])
            phase_at_gbw = phase_deg[i] + ratio * (phase_deg[i + 1] - phase_deg[i])
            pm = 180 + phase_at_gbw
            break

    if pm is not None:
        print(f"\n  3. Phase Margin:")
        print(f"     Phase at f_u = {phase_at_gbw:.2f} deg")
        print(f"     PM = 180 + ({phase_at_gbw:.2f}) = {pm:.2f} deg")
        print(f"     Target: >= 60 deg  -->  {'PASS' if pm >= 60 else 'FAIL - NEEDS TUNING'}")

# 4. -3dB Bandwidth
bw_3db = None
target_3db = dc_gain_db - 3
for i in range(len(gain_db) - 1):
    if gain_db[i] >= target_3db and gain_db[i + 1] < target_3db:
        f1, f2 = freq_real[i], freq_real[i + 1]
        g1, g2 = gain_db[i], gain_db[i + 1]
        bw_3db = f1 * (f2 / f1) ** ((g1 - target_3db) / (g1 - g2))
        break

if bw_3db:
    print(f"\n  4. -3dB Bandwidth:")
    print(f"     f_3dB = {bw_3db:.2f} Hz ({bw_3db / 1e3:.2f} kHz)")

# 5. Gain Margin
gm_db = None
for i in range(len(phase_deg) - 1):
    if phase_deg[i] >= -180 and phase_deg[i + 1] < -180:
        f1, f2 = freq_real[i], freq_real[i + 1]
        p1, p2 = phase_deg[i], phase_deg[i + 1]
        f_180 = f1 * (f2 / f1) ** ((p1 + 180) / (p1 - p2))
        # Find gain at this frequency
        for j in range(len(freq_real) - 1):
            if freq_real[j] <= f_180 <= freq_real[j + 1]:
                ratio = np.log(f_180 / freq_real[j]) / np.log(freq_real[j + 1] / freq_real[j])
                gain_at_180 = gain_db[j] + ratio * (gain_db[j + 1] - gain_db[j])
                gm_db = -gain_at_180
                break
        break

if gm_db is not None:
    print(f"\n  5. Gain Margin:")
    print(f"     GM = {gm_db:.2f} dB")

# 6. Power Summary
print(f"\n  6. Power Summary:")
print(f"     I_supply = 258.64 uA (from Phase 4 .op)")
print(f"     P_diss = 465.55 uW (<= 500 uW target)")

print(f"\n{'=' * 70}")
print(f"  BODE PLOT DATA SUMMARY (sampled)")
print(f"{'=' * 70}")
print(f"{'Frequency':>14s} {'Gain (dB)':>12s} {'Phase (deg)':>14s}")
print(f"{'-' * 42}")

# Print sampled data points for verification
sample_freqs = [1, 10, 100, 1e3, 10e3, 100e3, 1e6, 5e6, 10e6, 50e6, 100e6, 500e6, 1e9]
for sf in sample_freqs:
    idx = np.argmin(np.abs(freq_real - sf))
    if sf >= 1e6:
        freq_str = f"{sf/1e6:.0f} MHz"
    elif sf >= 1e3:
        freq_str = f"{sf/1e3:.0f} kHz"
    else:
        freq_str = f"{sf:.0f} Hz"
    print(f"{freq_str:>14s} {gain_db[idx]:>12.2f} {phase_deg[idx]:>14.2f}")

print(f"\n{'=' * 70}")
print(f"  SIMULATION COMPLETE")
print(f"{'=' * 70}")
