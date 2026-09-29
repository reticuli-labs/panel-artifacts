"""What conductivity does the solved model actually get under the R12 wrapper?

The wrapper replaces ParameterValues.copy with a version that multiplies the conductivity function by SCALE.
PyBaMM 26.8 calls .copy() on parameter values inside Simulation as well. This probe installs the SAME patch,
builds the same simulation for one cycle, and reads the conductivity function out of every ParameterValues
object that PyBaMM hands to process_model. It solves nothing beyond what building needs."""
import json, math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo", "results"))
import pybamm, cm_bat_sweep as sw
pybamm.set_logging_level("ERROR")
C_E, T = 1000.0, 298.15
base = pybamm.ParameterValues("OKane2022")
f0 = base["Electrolyte conductivity [S.m-1]"]
k0 = float(f0(pybamm.Scalar(C_E), pybamm.Scalar(T)).evaluate())

_orig_copy = pybamm.ParameterValues.copy
calls = {"n": 0}
def _copy(self):                                   # byte-for-byte the wrapper's patch, plus a counter
    p = _orig_copy(self); f = p["Electrolyte conductivity [S.m-1]"]
    p["Electrolyte conductivity [S.m-1]"] = (lambda c_e, T, f=f, s=SCALE: s * f(c_e, T)) if callable(f) else SCALE * f
    calls["n"] += 1
    return p
pybamm.ParameterValues.copy = _copy

seen = []
_orig_pm = pybamm.ParameterValues.process_model
def _pm(self, *a, **k):
    f = self["Electrolyte conductivity [S.m-1]"]
    seen.append(float(f(pybamm.Scalar(C_E), pybamm.Scalar(T)).evaluate()) / k0)
    return _orig_pm(self, *a, **k)
pybamm.ParameterValues.process_model = _pm

out = {"pybamm": pybamm.__version__, "probe_point": {"c_e_mol_m3": C_E, "T_K": T}, "kappa_base_S_per_m": k0, "arms": {}}
opts = {"SEI": "solvent-diffusion limited", "SEI porosity change": "true", "lithium plating": "partially reversible", "lithium plating porosity change": "true",
        "particle mechanics": ("swelling and cracking", "swelling only"), "SEI on cracks": "true"}
for SCALE in (0.5, 2.0):
    calls["n"] = 0; seen.clear()
    p = base.copy()                                # as sw.run() does; the patch fires here once
    after_run_copy = float(p["Electrolyte conductivity [S.m-1]"](pybamm.Scalar(C_E), pybamm.Scalar(T)).evaluate()) / k0
    model = pybamm.lithium_ion.DFN(opts)
    sim = pybamm.Simulation(model, parameter_values=p, experiment=pybamm.Experiment([sw.CYCLE(0.5)] * 1), solver=pybamm.IDAKLUSolver())
    sim.build_for_experiment()
    out["arms"][str(SCALE)] = {"intended_scale": SCALE, "scale_after_run_copy": after_run_copy, "copy_calls_until_built": calls["n"],
                               "scale_seen_by_process_model": sorted(set(round(s, 6) for s in seen)), "process_model_calls": len(seen),
                               "power_of_scale": sorted(set(round(math.log(s) / math.log(SCALE), 3) for s in seen))}
json.dump(out, open("scale_probe.json", "w"), indent=1)
print(json.dumps(out, indent=1))
