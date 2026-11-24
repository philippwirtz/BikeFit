# Where the target ranges come from

BikeFit grades a position against dynamic ranges: angles measured on video while you pedal. They run a few degrees
higher than numbers taken with a goniometer on a stationary bike. Treat every range as a starting point.

BikeFit reports inner angles (180° is a straight leg). Some sources quote the bend instead, so
"knee bend 30–40° at the bottom" is the same as BikeFit's "knee extension 140–150°".

## Side view (road, TT, gravel)

| Reading | BikeFit range (endurance road) | Notes |
| --- | --- | --- |
| Knee extension at the bottom | 140–150° (bend 30–40°) | Holmes method; dynamic, so higher than the static 25–35° |
| Elbow | 150–165° (bend 15–30°) | Averages from the Holmes paper: knee ~36 ± 7°, elbow ~19 ± 8° |
| Shoulder (torso to upper arm) | 80–95° | Practitioner range |
| Hip at the top of the stroke | 50–65° | Fitter's reference (Burt, *Bike Fit*, 2014): 55–65° on a road bike. Lower for aggressive and TT positions, higher for upright bikes |
| Torso vs horizontal | 45–55° | Practitioner range; some sources use 40–50° for endurance |

**City / hybrid** has no published dynamic ranges. Its numbers are estimates for an upright position and are marked as such
in `fit_profiles.py`.

Sources:

- Holmes method, joint-angle averages: https://pmc.ncbi.nlm.nih.gov/articles/PMC9219349/
- Video angles read about 8° higher than static ones: https://pubmed.ncbi.nlm.nih.gov/24499342/
- Practitioner cross-check for torso, shoulder and hip: https://www.bikefitadviser.com/blog/not-basic-bike-fit-part-3-bike-fit-joint-angles

## Front and rear view (beta)

BikeFit flags three things, as hints only (no score):

| Reading | Definition | Flag at | Why that high |
| --- | --- | --- | --- |
| Knee tracking | Angle between thigh and shank in the image, 5th/95th percentile over the clip | 10° | Healthy knee coronal range is 6.6 ± 2.7° |
| Pelvic rock | Peak-to-peak tilt of the hip line | 12° | Healthy pelvis coronal range is 7.1 ± 2.5° (observed 2.0–11.7°) |
| Left/right difference | Difference of the two knees' median deviation | 9° | A 2D gap below ~7.5–8.9° is measurement noise |

The thresholds sit at the top of the healthy range on purpose. A correctly fitted rider already rocks and tracks a
little, so a threshold near the average would flag most people. The frontal code has not been run on real front or rear
footage yet, so the thresholds come from the literature alone.

Sources:

- Cycling kinematics in healthy adults (saddle at 85.5% of inseam): https://pmc.ncbi.nlm.nih.gov/articles/PMC8675512/
- Knee alignment and frontal-plane knee mechanics in cycling: https://pmc.ncbi.nlm.nih.gov/articles/PMC5950749/
- Reliability of 2D video for frontal-plane knee valgus (SEM 2.7–3.0°, smallest detectable difference 7.5–8.9°):
  https://pubmed.ncbi.nlm.nih.gov/22104115/

## Frame size and KOPS

BikeFit says "the bike may be too long/short" only when two readings agree: a long reach needs a large shoulder angle
*and* nearly locked elbows; a short reach needs a small shoulder angle *and* a closed hip. A single noisy angle never
blames the frame.

KOPS (the knee's horizontal offset from the pedal axle at 3 o'clock) is shown as a reference, never as a rule, and not
at all for triathlon/TT profiles where the knee sits well forward by design.

## Credit

The idea of a front/rear check, the source list and the green/amber/red presentation were inspired by
[bike-fit-analyzer](https://github.com/doniwirawan/bike-fit-analyzer) (PolyForm Shield license). No code or text from it
is used here: the code is written from the definitions above.
