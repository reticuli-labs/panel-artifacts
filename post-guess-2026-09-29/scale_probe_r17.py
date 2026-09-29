"""Same probe as scale_probe.py, for the R17 wrapper: what plating rate constant does the solved model get?"""
import json, math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo", "results"))
import pybamm, cm_bat_sweep as sw
pybamm.set_logging_level("ERROR")
KEY = "Lithium plating kinetic rate constant [m.s-1]"
base = pybamm.ParameterValues("OKane2022"); k0 = float(base[KEY])
_orig_copy = pybamm.ParameterValues.copy
def _copy(self):                                   # the R17 wrapper's patch, as written there
    p = _orig_copy(self); p[KEY] = p[KEY] * SCALE; return p
pybamm.ParameterValues.copy = _copy
seen = []
_orig_pm = pybamm.ParameterValues.process_model
def _pm(self, *a, **k):
    seen.append(float(self[KEY]) / k0); return _orig_pm(self, *a, **k)
pybamm.ParameterValues.process_model = _pm
opts = {"SEI": "solvent-diffusion limited", "SEI porosity change": "true", "lithium plating": "partially reversible", "lithium plating porosity change": "true",
        "particle mechanics": ("swelling and cracking", "swelling only"), "SEI on cracks": "true"}
out = {"pybamm": pybamm.__version__, "key": KEY, "base_value": k0, "arms": {}}
for SCALE in (0.1, 10.0):
    seen.clear()
    p = base.copy()
    sim = pybamm.Simulation(pybamm.lithium_ion.DFN(opts), parameter_values=p, experiment=pybamm.Experiment([sw.CYCLE(0.5)] * 1), solver=pybamm.IDAKLUSolver())
    sim.build_for_experiment()
    out["arms"][str(SCALE)] = {"intended_scale": SCALE, "scale_after_run_copy": float(p[KEY]) / k0, "scale_seen_by_process_model": sorted(set(float(f"{s:.6g}") for s in seen)),
                               "power_of_scale": sorted(set(round(math.log(s) / math.log(SCALE), 3) for s in seen))}
json.dump(out, open("scale_probe_r17.json", "w"), indent=1); print(json.dumps(out, indent=1))
