"""R12 cells with the conductivity scale set DIRECTLY on the parameter set (no patch of ParameterValues.copy), so the
solved model gets exactly the scale named. Everything else is sw.run() from the repository, copied line for line,
plus: every PyBaMM summary variable is kept at the end, and the conductivity handed to process_model is recorded.
Usage: r12_kd.py <conductivity scale> <tau> <N> <outdir> <diffusivity scale>
This is r12_direct.py with one addition: the electrolyte diffusivity function is multiplied as well."""
import json, math, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo", "results"))
import pybamm, cm_bat_sweep as sw
pybamm.set_logging_level("ERROR")
SCALE, tau, N, outdir, DSCALE = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), sys.argv[4], float(sys.argv[5])
k, c, CH = 2.0, 0.5, 5
os.makedirs(outdir, exist_ok=True)
C_E, T = 1000.0, 298.15
base = pybamm.ParameterValues("OKane2022"); p = base.copy()
f0 = base["Electrolyte conductivity [S.m-1]"]; k0 = float(f0(pybamm.Scalar(C_E), pybamm.Scalar(T)).evaluate())
for side in ("Positive", "Negative"):
    p[f"{side} electrode thickness [m]"] = base[f"{side} electrode thickness [m]"] * k
    eps = base[f"{side} electrode porosity"]; b = 1 - math.log(tau) / math.log(eps)
    p[f"{side} electrode Bruggeman coefficient (electrolyte)"] = b; p[f"{side} electrode Bruggeman coefficient (electrode)"] = b
p["Nominal cell capacity [A.h]"] = base["Nominal cell capacity [A.h]"] * k
p["Electrolyte conductivity [S.m-1]"] = (lambda c_e, T, f=f0, s=SCALE: s * f(c_e, T))
d0 = base["Electrolyte diffusivity [m2.s-1]"]; dk0 = float(d0(pybamm.Scalar(C_E), pybamm.Scalar(T)).evaluate())
p["Electrolyte diffusivity [m2.s-1]"] = (lambda c_e, T, f=d0, s=DSCALE: s * f(c_e, T))
seen_d = []
seen = []
_orig_pm = pybamm.ParameterValues.process_model
def _pm(self, *a, **kw):
    seen.append(float(self["Electrolyte conductivity [S.m-1]"](pybamm.Scalar(C_E), pybamm.Scalar(T)).evaluate()) / k0)
    seen_d.append(float(self["Electrolyte diffusivity [m2.s-1]"](pybamm.Scalar(C_E), pybamm.Scalar(T)).evaluate()) / dk0)
    return _orig_pm(self, *a, **kw)
pybamm.ParameterValues.process_model = _pm
opts = {"SEI": "solvent-diffusion limited", "SEI porosity change": "true", "lithium plating": "partially reversible", "lithium plating porosity change": "true",
        "particle mechanics": ("swelling and cracking", "swelling only"), "SEI on cracks": "true"}
model = pybamm.lithium_ion.DFN(opts)
caps = {}; done = 0; start = None; summary = {}; err = None; t0 = time.time()
try:
    while done < N:
        n = min(CH, N - done)
        sim = pybamm.Simulation(model, parameter_values=p, experiment=pybamm.Experiment([sw.CYCLE(c)] * n), solver=pybamm.IDAKLUSolver())
        sol = sim.solve(starting_solution=start)
        cycles = sol.cycles[1:] if start is not None else sol.cycles
        for j, cyc in enumerate(cycles, start=done + 1):
            if j == 1 or j % 10 == 0 or j == N:
                st = cyc.steps[0]; caps[j] = float(abs(st["Discharge capacity [A.h]"].entries[-1] - st["Discharge capacity [A.h]"].entries[0]))
        sv = sol.summary_variables
        for name in sv.all_variables:
            try: summary[name] = float(sv[name][-1])
            except Exception: pass
        done += len(cycles)
        if len(cycles) < n:
            if cycles and done not in caps:
                st = cycles[-1].steps[0]; caps[done] = float(abs(st["Discharge capacity [A.h]"].entries[-1] - st["Discharge capacity [A.h]"].entries[0]))
            break
        start = cycles[-1].steps[-1]
except Exception as e:
    err = str(e)[:300]
ks = sorted(caps)
out = {"kind": "reticuli.cm-bat-r12.conductivity-and-diffusivity.v1", "pybamm": pybamm.__version__, "python": sys.version.split()[0], "platform": sys.platform,
       "conductivity_scale_set": SCALE, "conductivity_scale_seen_by_process_model": sorted(set(round(s, 6) for s in seen)),
       "diffusivity_scale_set": DSCALE, "diffusivity_scale_seen_by_process_model": sorted(set(round(s, 6) for s in seen_d)),
       "k": k, "tau": tau, "crate": c, "chunk": CH, "cycles_asked": N, "cycles_completed": done,
       "retention": (caps[ks[-1]] / caps[ks[0]]) if caps else None, "caps_at_cycles": {str(i): caps[i] for i in ks},
       "summary_at_end": summary, "error": err, "seconds": round(time.time() - t0, 1)}
json.dump(out, open(os.path.join(outdir, f"kd_kappa{SCALE:g}_D{DSCALE:g}_tau{tau:g}_N{N}.json"), "w"), indent=1)
print(json.dumps({k2: v for k2, v in out.items() if k2 != "summary_at_end"}))
