# Insights (set the rate)

> **Educational demos made to show an open-source tool. Not research.** Each sentence names the field of
> `results/set_the_rate.json` it comes from; a test checks the numbers.

1. In this model, a cost-push shock that adds 1 point a year to the Phillips curve raises inflation by 1.283 points on impact, because firms expect it to last, and lowers the output gap by 0.513 per cent; the rule raises the policy rate by 1.667 points. (fields: `calibration.shock_pp`, `cost_push_shock.baseline.impact`)
2. With a rule that responds twice as strongly to inflation, 3 instead of 1.5, inflation rises only 0.839 and the gap falls 0.839 per cent: in the model, less inflation comes with a deeper dip. (fields: `cost_push_shock.strong.phi_pi`, `cost_push_shock.baseline.phi_pi`, `cost_push_shock.strong.impact`)
3. If the rate rises less than one for one with inflation, at 0.8, only 1 of the 2 needed eigenvalues lies outside the unit circle, and the model no longer picks out a single path. (fields: `taylor_principle.passive.phi_pi`, `taylor_principle.passive.outside_unit_circle`, `taylor_principle.passive.forward_looking_variables`)
4. A promise to lower the rule by 1 point in quarter 8 only, with the rule on in every quarter, raises inflation today by 0.142 points in this model, because forward-looking firms and households act on the expected path; the rule already raises today's rate by 0.188 in answer, and the output gap today dips by 0.05 per cent. (fields: `forward_guidance.cut_pp`, `forward_guidance.quarter`, `forward_guidance.rule_on.today`)
5. If the nominal rate is instead held still until the promised quarter, the effect on inflation today grows with the horizon, to 236.519 times that of a cut made today for quarter 12: the forward guidance puzzle that many economists see as a limit of this textbook model. (fields: `forward_guidance.pegged_puzzle.last.inflation_ratio`, `forward_guidance.pegged_puzzle.last.quarter`)
