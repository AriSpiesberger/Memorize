"""divergence.py with clear decisions only: a branch pair is kept when the chosen move has at least --min-chosen of the
branching point's rollouts, at least --min-node rollouts pass through that point, and the subpar move has at least
--min-subpar rollouts (so a share is not 3 of 4). Everything else is divergence.py's, unchanged; its arguments pass
through.

    python transcend/divergence_gap.py lp --model S --cc-run runs/transcend/crosscoder/mixed-L11 --cc L11-4096 --tag <tag>
    python transcend/divergence_gap.py report --cc-run ... --cc L11-4096 --tag <tag>

play does not depend on the pairs, so a new tag can reuse another tag's codes: copy runs/transcend/divergence/<tag>/<S|W>/
pos-*.npz and mu.json into the new tag's folders, then run lp and report here. The filter's settings are written to
results/transcend/divergence/<tag>/gap.json."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import divergence as dv

ap = argparse.ArgumentParser(add_help=False)
ap.add_argument("--min-chosen", type=float, default=0.75)
ap.add_argument("--min-node", type=int, default=20)
ap.add_argument("--min-subpar", type=int, default=3)
gap, rest = ap.parse_known_args()
_pairs_of = dv.pairs_of


def pairs_of(D, plies, min_share):
    return [p for p in _pairs_of(D, plies, min_share)
            if p["wc"] >= gap.min_chosen and p["node"] >= gap.min_node and p["ws"] * p["node"] >= gap.min_subpar - 1e-9]


dv.pairs_of = pairs_of
if __name__ == "__main__":
    tag = rest[rest.index("--tag") + 1] if "--tag" in rest else None
    if tag:
        (dv.RESULTS / tag).mkdir(parents=True, exist_ok=True)
        (dv.RESULTS / tag / "gap.json").write_text(json.dumps(vars(gap)), encoding="utf-8")
    sys.argv = [sys.argv[0]] + rest
    dv.main()
