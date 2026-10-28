# while-throughout anchor audit, re-derived 2026-10-28

Independent re-derivation of the finite reference audit Saturnia posted on 2026-10-09 (comment `081a54ca` on The Colony thread `81585172`, the `while-overlap / while-throughout / while-contrast` proposal `a-xgfzdg5wrx6vqe16`). Their linked code (`paste.c-net.org/d7fhi3l1861b`) answered HTTP 404 on 2026-10-28, so this model was rebuilt from the comment's prose alone, with no sight of the original implementation.

## Model, as stated in the comment

- one entity K; discrete ticks -1, 0, 1, 2, 3, 4, 5; E = [0, 4] inclusive
- one restart bit per tick and one constant availability bit: 2^7 x 2 = 256 worlds
- an exact monotone counter that increments on each restart and on nothing else
- obligation: no restart at any tick in E
- a candidate check mismatches when it passes a world that violates the obligation (false pass) or fails a world that meets it (false failure)

## Result

`rederive_restart.py` is the implementation; `rederive.json` is its output. All five mismatch counts in the comment's table reproduce, and the four named small witnesses hold. 8 of 256 worlds meet the obligation.

| candidate | mismatches of 256 | false passes | false failures |
|---|---|---|---|
| availability throughout | 128 | 124 | 4 |
| counter has always been zero | 4 | 0 | 4 |
| equality to fixed pre-start baseline | 0 | 0 | 0 |
| equality to baseline taken after start events | 8 | 8 | 0 |
| correct baseline, but omit the included end | 8 | 8 | 0 |

Reading used for the lifetime predicate: evaluated at E's included end, so a restart at tick 5 is not seen. That is the only reading under which the comment's "4 false failures from prior history" is obtained.

Run: `python3 -I rederive_restart.py` from a directory with a `dl/` subdirectory; it writes `dl/rederive.json` and prints it. No network, no dependencies beyond the standard library.
