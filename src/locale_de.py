"""German catalog for server-written text (recommendations, warnings, PDF). Keys are the English templates."""

DE = {
    # Coach
    "Position summary for {p}.": "Positionsübersicht für {p}.",
    "Golden rule: change one thing at a time, in small steps, ride for a few days, then re-test. Comfort and pain-free riding always beat textbook numbers.":
        "Goldene Regel: Ändere immer nur eine Sache, in kleinen Schritten, fahre ein paar Tage damit und miss dann neu. "
        "Komfort und schmerzfreies Fahren gehen immer vor Lehrbuchwerten.",
    "All measured angles are within the typical range for this riding style. If you're comfortable and pain-free, leave it alone. Great fit!":
        "Alle gemessenen Winkel liegen im typischen Bereich für diesen Fahrstil. Wenn du bequem und schmerzfrei fährst, "
        "lass es so. Sehr gute Position!",
    "Here is what to work on, in order of importance:": "Daran solltest du arbeiten, nach Wichtigkeit geordnet:",

    # Warnings
    "Cadence was {c:.0f} rpm. Film at a steady {lo}–{hi} rpm: very low or very high cadence changes hip rocking and upper-body movement, so those readings are less comparable.":
        "Die Trittfrequenz lag bei {c:.0f} U/min. Filme bei gleichmäßigen {lo}–{hi} U/min: Sehr niedrige oder sehr hohe "
        "Trittfrequenz verändert Beckenkippen und Oberkörperbewegung, diese Werte sind dann schlechter vergleichbar.",
    "The rider was found in only {p:.0%} of frames. Brighter, even light and a plain background will make results steadier.":
        "Der Fahrer wurde nur in {p:.0%} der Bilder erkannt. Helleres, gleichmäßiges Licht und ein ruhiger Hintergrund "
        "machen die Ergebnisse stabiler.",
    "Tracking is noisy (knee scatter ±{sd:.0f}° around the model). Results are approximate: film side-on, steady, in good light, with the rider seated and pedalling.":
        "Das Tracking ist unruhig (Kniestreuung ±{sd:.0f}° um das Modell). Die Ergebnisse sind Näherungen: Filme genau von "
        "der Seite, ruhig, bei gutem Licht, sitzend und tretend.",
    "Both legs were found in only {p:.0%} of frames. Better light and a plain background will help.":
        "Beide Beine wurden nur in {p:.0%} der Bilder erkannt. Besseres Licht und ein ruhiger Hintergrund helfen.",
    "Front/rear analysis is a beta. The hints come from published ranges and haven't been checked against real clips yet. Treat them as a prompt to look closer, not as a verdict.":
        "Die Analyse von vorne/hinten ist eine Beta. Die Hinweise beruhen auf publizierten Bereichen und wurden noch nicht an "
        "echten Clips geprüft. Verstehe sie als Anlass, genauer hinzusehen, nicht als Urteil.",
    "A photo represents a static snapshot. For dynamic pedalling biomechanics, upload a 10–30s video.":
        "Ein Foto ist eine statische Momentaufnahme. Für die Biomechanik beim Treten lade ein Video von 10–30 s hoch.",
    "The clip is shorter than 8 s. Record 20–30 s of steady pedalling for tighter results.":
        "Der Clip ist kürzer als 8 s. Nimm 20–30 s gleichmäßiges Treten auf, dann werden die Ergebnisse genauer.",
    "The clip is shorter than 8 s. Record 20–30 s of steady pedalling.":
        "Der Clip ist kürzer als 8 s. Nimm 20–30 s gleichmäßiges Treten auf.",
    "The knee barely changed angle. Pedal continuously while recording.":
        "Der Kniewinkel hat sich kaum verändert. Tritt während der Aufnahme durchgehend.",
    "The camera doesn't look fully side-on (both shoulders are visible). Place it square to the bike, at 90°.":
        "Die Kamera steht nicht ganz seitlich (beide Schultern sind sichtbar). Stelle sie im rechten Winkel zum Rad auf.",
    "The pedal stroke couldn't be modelled, so angles use whole-clip percentiles. Make sure the near foot and pedal are visible through the full stroke.":
        "Der Tretzyklus ließ sich nicht modellieren, die Winkel stammen deshalb aus Perzentilen des ganzen Clips. Achte darauf, "
        "dass der kameranahe Fuß und das Pedal über die ganze Umdrehung sichtbar sind.",
    "No millimetre scale: the crank circle wasn't clear and no rider height was given, so adjustments are shown in degrees only.":
        "Kein Millimetermaßstab: Der Kurbelkreis war nicht klar erkennbar und es wurde keine Körpergröße angegeben, daher "
        "stehen Anpassungen nur in Grad da.",
    "The Ultralytics engine has no heel or toe points, so the foot is estimated from the shank. Ankle and foot-angle readings are approximate; knee, hip and saddle height are unaffected.":
        "Die Ultralytics-Engine liefert keine Ferse und Zehe, der Fuß wird daher aus dem Unterschenkel geschätzt. Sprunggelenk- "
        "und Fußwinkel sind Näherungen; Knie, Hüfte und Sattelhöhe sind nicht betroffen.",
    "Back roundness needs the MediaPipe engine (it reads the rider's silhouette). Re-run with MediaPipe to see the back and posture analysis.":
        "Die Rückenrundung braucht die MediaPipe-Engine (sie liest die Silhouette). Analysiere erneut mit MediaPipe, um Rücken "
        "und Haltung zu sehen.",
    "Pedals aren't at 6 o'clock (BDC) or 12 o'clock (TDC). For saddle height measurement, take a photo with the pedal nearest the camera at 6 o'clock.":
        "Die Pedale stehen weder auf 6 Uhr (UT) noch auf 12 Uhr (OT). Für die Sattelhöhe fotografiere mit dem kameranahen "
        "Pedal auf 6 Uhr.",
    "Pedal is at TDC (12 o'clock). For complete saddle height verification, capture at 6 o'clock.":
        "Das Pedal steht im oberen Totpunkt (12 Uhr). Für die Prüfung der Sattelhöhe fotografiere auf 6 Uhr.",
    "Couldn't see the leg clearly (hip / knee / ankle).": "Das Bein war nicht klar erkennbar (Hüfte / Knie / Sprunggelenk).",

    # Range notes
    "Limited flexibility: hip and torso targets opened by 5°.": "Eingeschränkte Beweglichkeit: Zielwerte für Hüfte und Oberkörper um 5° geöffnet.",
    "Good flexibility: hip and torso targets lowered by 3°.": "Gute Beweglichkeit: Zielwerte für Hüfte und Oberkörper um 3° abgesenkt.",
    "Front-of-knee pain: favour a slightly higher saddle (less knee bend).": "Schmerzen vorne am Knie: eher etwas höherer Sattel (weniger Kniebeugung).",
    "Back-of-knee pain: avoid over-extension at the bottom of the stroke.": "Schmerzen in der Kniekehle: Überstreckung unten im Tretzyklus vermeiden.",
    "Lower-back pain: hip and torso targets opened by 3°.": "Schmerzen im unteren Rücken: Zielwerte für Hüfte und Oberkörper um 3° geöffnet.",
    "Neck, shoulder or hand pain: shorter reach and a slightly higher front end.": "Nacken-, Schulter- oder Handbeschwerden: kürzerer Reach und etwas höhere Front.",
    "These targets are estimates: no published dynamic ranges exist for this riding style.": "Diese Zielwerte sind Schätzungen: Für diesen Fahrstil gibt es keine publizierten dynamischen Bereiche.",

    # Recommendations
    "Raise your saddle ~{mm:.0f} mm": "Sattel ca. {mm:.0f} mm höher",
    "Your knee only opens to {ke:.0f}° at the bottom (target {lo}–{hi}°). A low saddle overloads the front of the knee and wastes power. Raise it in 3–5 mm steps and re-test.":
        "Dein Knie öffnet unten nur bis {ke:.0f}° (Ziel {lo}–{hi}°). Ein zu tiefer Sattel überlastet das vordere Knie und "
        "kostet Kraft. Erhöhe ihn in Schritten von 3–5 mm und miss neu.",
    "Lower your saddle ~{mm:.0f} mm": "Sattel ca. {mm:.0f} mm tiefer",
    "Your knee opens to {ke:.0f}° at the bottom (target {lo}–{hi}°). Over-extension often causes hip rocking and pain behind the knee. Lower it in 3–5 mm steps and re-test.":
        "Dein Knie öffnet unten bis {ke:.0f}° (Ziel {lo}–{hi}°). Überstreckung führt oft zu Beckenkippen und Schmerzen in der "
        "Kniekehle. Senke ihn in Schritten von 3–5 mm und miss neu.",
    "Toes point down hard at the bottom: saddle may be high": "Fußspitze unten stark nach unten: Sattel evtl. zu hoch",
    "Your foot is {pf:.0f}° toe-down at the bottom of the stroke (typical 5–15°). Pointing the toes reaches for a pedal that is too far away, so the knee angle ({ke:.0f}°) can look fine while the saddle is too high. Lower the saddle 3–5 mm and re-test: if the toes level out and the knee stays in range, keep it.":
        "Dein Fuß ist unten im Tretzyklus {pf:.0f}° nach unten gestreckt (typisch 5–15°). Mit der Fußspitze greifst du nach "
        "einem Pedal, das zu weit weg ist – der Kniewinkel ({ke:.0f}°) kann dann gut aussehen, obwohl der Sattel zu hoch ist. "
        "Senke den Sattel um 3–5 mm und miss neu: Wird der Fuß flacher und bleibt das Knie im Bereich, behalte es bei.",
    "Your heel drops at the bottom of the stroke": "Deine Ferse sinkt unten im Tretzyklus ab",
    "Your foot is {pfa:.0f}° heel-down at the bottom. A dropped heel straightens the knee, so part of the over-extension ({ke:.0f}°) is pedalling style rather than saddle height. Lower the saddle in small steps and re-check the ankle with each step.":
        "Dein Fuß steht unten {pfa:.0f}° fersenabwärts. Eine abgesenkte Ferse streckt das Knie, ein Teil der Überstreckung "
        "({ke:.0f}°) ist also Tretstil und nicht Sattelhöhe. Senke den Sattel in kleinen Schritten und prüfe das "
        "Sprunggelenk jedes Mal mit.",
    "Knee is cramped at the top of the stroke": "Knie ist oben im Tretzyklus stark gebeugt",
    "Knee closes to {kf:.0f}° (target {lo}–{hi}°). The stroke model predicts {crank:g} mm cranks would open it, with the saddle raised by the difference. Sliding the saddle back a few mm also helps.":
        "Das Knie schließt sich bis {kf:.0f}° (Ziel {lo}–{hi}°). Laut Tretmodell öffnen es {crank:g}-mm-Kurbeln, wenn der "
        "Sattel um die Differenz höher kommt. Den Sattel ein paar mm nach hinten zu schieben hilft ebenfalls.",
    "Knee closes to {kf:.0f}° (target {lo}–{hi}°). Consider sliding the saddle back a few mm or trying shorter cranks (e.g. 165–170 mm).":
        "Das Knie schließt sich bis {kf:.0f}° (Ziel {lo}–{hi}°). Schiebe den Sattel ein paar mm zurück oder probiere kürzere "
        "Kurbeln (z. B. 165–170 mm).",
    "Open up your hip angle": "Hüftwinkel öffnen",
    "Your hip closes to {hc:.0f}° (target {lo}–{hi}°). Raise the bars (spacers / stem flip) or try {crank:g} mm cranks: the stroke model predicts about {gain:.0f}° more hip angle with them (raise the saddle {dh:.0f} mm at the same time).":
        "Deine Hüfte schließt sich bis {hc:.0f}° (Ziel {lo}–{hi}°). Lenker höher (Spacer / Vorbau drehen) oder "
        "{crank:g}-mm-Kurbeln: Laut Tretmodell bringen sie etwa {gain:.0f}° mehr Hüftwinkel (Sattel gleichzeitig "
        "{dh:.0f} mm höher).",
    "Your hip closes to {hc:.0f}° (target {lo}–{hi}°). Try raising the bars (spacers / stem flip), shorter cranks, or (on a tri bike) moving the saddle slightly forward.":
        "Deine Hüfte schließt sich bis {hc:.0f}° (Ziel {lo}–{hi}°). Probiere einen höheren Lenker (Spacer / Vorbau drehen), "
        "kürzere Kurbeln oder (am Triathlonrad) den Sattel etwas nach vorne.",
    "You have room to get lower": "Du hast Spielraum für eine tiefere Position",
    "Hip angle of {hc:.0f}° is more open than needed for this style (target {lo}–{hi}°). If you want more speed, drop the bars gradually.":
        "Ein Hüftwinkel von {hc:.0f}° ist offener als für diesen Stil nötig (Ziel {lo}–{hi}°). Wenn du schneller werden "
        "willst, senke den Lenker schrittweise.",
    "Position is more upright than typical for this style": "Position ist aufrechter als für diesen Stil üblich",
    "Torso at {to:.0f}° (typical {lo}–{hi}°). Fine if comfort is the goal; otherwise lower the bars 5–10 mm at a time. Rough estimate: 5° lower saves about {w:.0f} W at {v:.0f} km/h.":
        "Oberkörper bei {to:.0f}° (typisch {lo}–{hi}°). In Ordnung, wenn Komfort das Ziel ist; sonst den Lenker in Schritten "
        "von 5–10 mm senken. Grobe Schätzung: 5° tiefer spart etwa {w:.0f} W bei {v:.0f} km/h.",
    "Torso at {to:.0f}° (typical {lo}–{hi}°). Fine if comfort is the goal; otherwise lower the bars 5–10 mm at a time.":
        "Oberkörper bei {to:.0f}° (typisch {lo}–{hi}°). In Ordnung, wenn Komfort das Ziel ist; sonst den Lenker in Schritten "
        "von 5–10 mm senken.",
    "Position is very low: check it's sustainable": "Position ist sehr tief: Prüfe, ob du sie halten kannst",
    "Torso at {to:.0f}° (typical {lo}–{hi}°). If you feel neck/back strain or can't hold it for long, raise the bars slightly.":
        "Oberkörper bei {to:.0f}° (typisch {lo}–{hi}°). Wenn Nacken oder Rücken belastet sind oder du sie nicht lange hältst, "
        "Lenker etwas höher.",
    "Reach looks short": "Reach wirkt kurz",
    "Shoulder angle {sh:.0f}° (target {lo}–{hi}°). You may feel cramped. A 10 mm longer stem (or extending aerobar pads forward) is a common fix.":
        "Schulterwinkel {sh:.0f}° (Ziel {lo}–{hi}°). Du sitzt vermutlich gedrungen. Üblich ist ein 10 mm längerer Vorbau "
        "(oder die Aufliegerpads weiter nach vorne).",
    "Reach looks long": "Reach wirkt lang",
    "Shoulder angle {sh:.0f}° (target {lo}–{hi}°). Stretching for the bars loads the neck and shoulders. Try a 10 mm shorter stem or move pads back.":
        "Schulterwinkel {sh:.0f}° (Ziel {lo}–{hi}°). Das Strecken zum Lenker belastet Nacken und Schultern. Probiere einen "
        "10 mm kürzeren Vorbau oder setze die Pads zurück.",
    "Soften your elbows": "Ellbogen lockerer",
    "Elbows are nearly locked ({el:.0f}°). Keep a slight bend to absorb bumps; if you can't, reach is probably too long.":
        "Die Ellbogen sind fast durchgestreckt ({el:.0f}°). Halte sie leicht gebeugt, um Stöße abzufangen; geht das nicht, "
        "ist der Reach vermutlich zu lang.",
    "Hips rock on the saddle": "Becken kippt auf dem Sattel",
    "Your hips move about {rock:.0f} mm up and down each stroke. More than ~15 mm usually means the saddle is a touch high or the cleats are too far forward.":
        "Dein Becken bewegt sich pro Umdrehung etwa {rock:.0f} mm auf und ab. Mehr als ~15 mm heißt meist: Sattel etwas zu "
        "hoch oder Cleats zu weit vorne.",
    "You slide forward and back on the saddle": "Du rutschst auf dem Sattel vor und zurück",
    "Your hips shift about {sway:.0f} mm fore-aft each stroke. Riders usually creep forward when the reach is long or the saddle nose tilts down, and back when the saddle is low. Check saddle tilt (start level) and reach. This flag is a heuristic, not a published limit.":
        "Dein Becken verschiebt sich pro Umdrehung etwa {sway:.0f} mm nach vorne und hinten. Nach vorne rutscht man meist bei "
        "langem Reach oder nach unten geneigter Sattelspitze, nach hinten bei zu tiefem Sattel. Prüfe Sattelneigung (waagrecht "
        "beginnen) und Reach. Diese Schwelle ist eine Faustregel, kein publizierter Grenzwert.",
    "The bike may be too long for you": "Das Rad ist dir möglicherweise zu lang",
    "Shoulder and elbow angles both point the same way. Adjust the stem first, and if that isn't enough consider a shorter stem, or a smaller frame if the stem is already short.":
        "Schulter- und Ellbogenwinkel weisen in dieselbe Richtung. Passe zuerst den Vorbau an; reicht das nicht, nimm einen "
        "kürzeren Vorbau oder, wenn er schon kurz ist, einen kleineren Rahmen.",
    "The bike may be too short for you": "Das Rad ist dir möglicherweise zu kurz",
    "Shoulder and hip angles both point the same way. Adjust the stem first, and if that isn't enough consider a longer stem, or a larger frame if the stem is already long.":
        "Schulter- und Hüftwinkel weisen in dieselbe Richtung. Passe zuerst den Vorbau an; reicht das nicht, nimm einen "
        "längeren Vorbau oder, wenn er schon lang ist, einen größeren Rahmen.",
    "Knee is {k:.0f} mm ahead of the pedal axle at 3 o'clock": "Knie {k:.0f} mm vor der Pedalachse bei 3 Uhr",
    "Knee is {k:.0f} mm behind the pedal axle at 3 o'clock": "Knie {k:.0f} mm hinter der Pedalachse bei 3 Uhr",
    "A knee roughly above the pedal axle is a common starting point, but riders differ. If you have knee pain, try moving the saddle back a few mm and re-test. Saddle height comes first.":
        "Ein Knie etwa über der Pedalachse ist ein üblicher Ausgangspunkt, aber Fahrer sind verschieden. Bei Knieschmerzen "
        "schiebe den Sattel ein paar mm zurück und miss neu. Die Sattelhöhe kommt zuerst.",
    "A knee roughly above the pedal axle is a common starting point, but riders differ. If you have knee pain, try moving the saddle forward a few mm and re-test. Saddle height comes first.":
        "Ein Knie etwa über der Pedalachse ist ein üblicher Ausgangspunkt, aber Fahrer sind verschieden. Bei Knieschmerzen "
        "schiebe den Sattel ein paar mm nach vorne und miss neu. Die Sattelhöhe kommt zuerst.",
    "Check saddle tilt and width": "Sattelneigung und -breite prüfen",
    "Saddle discomfort is often tilt (start level, then 1–2° nose down) or a saddle too narrow for your sit bones, rather than height.":
        "Sattelbeschwerden kommen oft von der Neigung (waagrecht beginnen, dann 1–2° Spitze nach unten) oder einem Sattel, der "
        "für deine Sitzknochen zu schmal ist, seltener von der Höhe.",
    "Check cleat position": "Cleat-Position prüfen",
    "Knee pain that persists with a good saddle height often comes from cleat rotation or fore-aft position. Ball of the foot over the pedal spindle is the start point.":
        "Knieschmerzen trotz guter Sattelhöhe kommen oft von Rotation oder Längsposition der Cleats. Ausgangspunkt: Großzehenballen "
        "über der Pedalachse.",
    "Upper body is moving a lot": "Oberkörper bewegt sich stark",
    "Your torso angle varies by {tr:.0f}° while pedalling. Rocking usually means the saddle is too high, or you're filming during a very hard effort.":
        "Dein Oberkörperwinkel schwankt beim Treten um {tr:.0f}°. Schaukeln heißt meist: Sattel zu hoch, oder die Aufnahme "
        "entstand bei sehr hoher Belastung.",

    # Posture
    "{title} (beta)": "{title} (Beta)",
    " (about {mm:.0f} mm of curve)": " (etwa {mm:.0f} mm Wölbung)",
    "Keep the chest open to avoid rounding": "Brust offen halten, damit der Rücken nicht rund wird",
    "Your upper back curves slightly ({r:.1f}%){bulge}. Cue a long spine and relaxed shoulders; if it worsens late in rides, check reach.":
        "Dein oberer Rücken rundet sich leicht ({r:.1f} %){bulge}. Denk an eine lange Wirbelsäule und lockere Schultern; wird "
        "es gegen Ende langer Fahrten schlimmer, prüfe den Reach.",
    "Flatten your back: shorten the reach or raise the bars": "Rücken flacher: Reach kürzen oder Lenker höher",
    "Your back rounds by {r:.1f}% of its length{bulge}. Try a stem 10 mm shorter or one 5 mm spacer under it, then roll the pelvis forward and hinge from the hips.":
        "Dein Rücken rundet sich um {r:.1f} % seiner Länge{bulge}. Probiere einen 10 mm kürzeren Vorbau oder einen 5-mm-Spacer "
        "darunter, kipp dann das Becken nach vorne und beuge dich aus der Hüfte.",
    "Flatten your back: give yourself more room": "Rücken flacher: Mach dir mehr Platz",
    "Your back rounds by {r:.1f}% of its length{bulge} while the reach is short, so you're folding to fit. Try a stem 10 mm longer, then roll the pelvis forward and hinge from the hips.":
        "Dein Rücken rundet sich um {r:.1f} % seiner Länge{bulge}, obwohl der Reach kurz ist – du faltest dich zusammen. "
        "Probiere einen 10 mm längeren Vorbau, kipp dann das Becken nach vorne und beuge dich aus der Hüfte.",
    "Back shape": "Rückenform",
    "{v:.1f}% curve": "{v:.1f} % Wölbung",
    "Pelvis stability": "Beckenstabilität",
    "Hip bounce per stroke; more than 10 mm suggests the saddle is too high.": "Beckenhub pro Umdrehung; mehr als 10 mm spricht für einen zu hohen Sattel.",
    "{tip}; target {lo:g}–{hi:g}°.": "{tip}; Ziel {lo:g}–{hi:g}°.",
    "Torso angle": "Oberkörperwinkel",
    "Shoulder angle": "Schulterwinkel",
    "Elbow bend": "Ellbogenbeugung",
    "Trunk lean versus horizontal": "Rumpfneigung gegen die Horizontale",
    "Reach from hip to elbow": "Reichweite von der Hüfte zum Ellbogen",
    "Soft elbows absorb road buzz": "Lockere Ellbogen fangen Vibrationen ab",
    "Your spine stays long and flat from hips to shoulders.": "Deine Wirbelsäule bleibt von der Hüfte bis zu den Schultern lang und flach.",
    "Your upper back curves a little. Hinge from the hips and keep the chest open.": "Dein oberer Rücken rundet sich etwas. Beuge dich aus der Hüfte und halte die Brust offen.",
    "Your back hunches over the bars. Usually a sign the reach is too long or the bars too low.": "Du machst über dem Lenker einen Buckel. Meist ein Zeichen für zu langen Reach oder zu tiefen Lenker.",
    "Neutral back": "Neutraler Rücken",
    "Slight rounding": "Leichte Rundung",
    "Rounded back": "Runder Rücken",

    # Frontal
    "Your {side} knee drifts inward": "Dein {side} Knie wandert nach innen",
    "It moves up to {v:.0f}° toward the frame midline (flag at 10°). Check cleat rotation and wedges, foot support, and stance width.":
        "Es bewegt sich bis zu {v:.0f}° zur Rahmenmitte (Schwelle 10°). Prüfe Cleat-Rotation und Keile, Fußstütze und Q-Faktor.",
    "Your {side} knee drifts outward": "Dein {side} Knie wandert nach außen",
    "It moves up to {v:.0f}° away from the midline (flag at 10°). Check cleat rotation, stance width and pedal spacers.":
        "Es bewegt sich bis zu {v:.0f}° von der Mitte weg (Schwelle 10°). Prüfe Cleat-Rotation, Q-Faktor und Pedal-Spacer.",
    "Your legs track differently": "Deine Beine laufen unterschiedlich",
    "The two knees differ by {v:.0f}° (flag at 9°). Compare cleat set-up left and right, and consider a leg-length or flexibility difference.":
        "Die Knie unterscheiden sich um {v:.0f}° (Schwelle 9°). Vergleiche die Cleat-Einstellung links und rechts und denk an "
        "eine Beinlängen- oder Beweglichkeitsdifferenz.",
    "Your pelvis rocks side to side": "Dein Becken kippt seitlich",
    "The hip line tilts {v:.0f}° peak to peak (flag at 12°). A saddle that is a little high or too narrow is the usual cause.":
        "Die Hüftlinie kippt {v:.0f}° von Spitze zu Spitze (Schwelle 12°). Meist ist der Sattel etwas zu hoch oder zu schmal.",
    "left": "linkes",
    "right": "rechtes",

    # Snapshots
    "Leg extension (bottom of stroke)": "Beinstreckung (unterer Totpunkt)",
    "Knee bend (top of stroke)": "Kniebeugung (oberer Totpunkt)",
    "3 o'clock (power phase)": "3 Uhr (Druckphase)",
    "Back & posture analysis": "Rücken- und Haltungsanalyse",
    "Largest knee drift (front/rear view)": "Größte Knieabweichung (Ansicht vorne/hinten)",
    "Your Position": "Deine Position",
    "Knee {mm:.0f} mm ahead of pedal axle": "Knie {mm:.0f} mm vor Pedalachse",
    "Knee {mm:.0f} mm behind pedal axle": "Knie {mm:.0f} mm hinter Pedalachse",

    # Metrics, profiles, rider form
    "Knee extension (bottom of stroke)": "Kniestreckung (unten)",
    "Knee extension": "Kniestreckung",
    "How straight your leg gets at the bottom of the pedal stroke. Mostly controlled by saddle height.":
        "Wie gestreckt dein Bein unten im Tretzyklus ist. Hängt vor allem von der Sattelhöhe ab.",
    "Knee bend (top of stroke)": "Kniebeugung (oberer Totpunkt)",
    "Knee bend at top": "Kniebeugung oben",
    "How bent your knee is at the top of the stroke. Too small = knee is cramped (saddle low/forward or cranks too long).":
        "Wie stark dein Knie oben gebeugt ist. Zu klein = Knie zu eng (Sattel tief/vorne oder Kurbeln zu lang).",
    "Hip angle (most closed)": "Hüftwinkel (am geschlossensten)",
    "Hip angle at top": "Hüftwinkel oben",
    "Angle between torso and thigh at the top of the stroke. Too closed chokes breathing and power; too open is less aero.":
        "Winkel zwischen Oberkörper und Oberschenkel oben im Tretzyklus. Zu geschlossen behindert Atmung und Kraft; zu offen ist "
        "weniger aerodynamisch.",
    "Torso angle (vs. horizontal)": "Oberkörperwinkel (zur Horizontalen)",
    "Torso": "Oberkörper",
    "How low your back is. Lower = more aero, higher = more comfortable. Mostly controlled by handlebar height and reach.":
        "Wie tief dein Rücken ist. Tiefer = aerodynamischer, höher = bequemer. Hängt vor allem von Lenkerhöhe und Reach ab.",
    "Shoulder angle (arm vs. torso)": "Schulterwinkel (Arm zu Oberkörper)",
    "Shoulder": "Schulter",
    "Angle between upper arm and torso. Tells you if the bars are too close (small) or too far (large).":
        "Winkel zwischen Oberarm und Oberkörper. Zeigt, ob der Lenker zu nah (klein) oder zu weit weg (groß) ist.",
    "Elbow": "Ellbogen",
    "A slight bend absorbs road buzz. Locked-out elbows usually mean the reach is too long.":
        "Eine leichte Beugung fängt Vibrationen ab. Durchgestreckte Ellbogen bedeuten meist zu langen Reach.",
    "Endurance road": "Rennrad Endurance",
    "Road: endurance / comfort": "Rennrad: Endurance / Komfort",
    "Sportives, long rides, commuting. Comfort first.": "Radmarathons, lange Ausfahrten, Pendeln. Komfort zuerst.",
    "Race road": "Rennrad Race",
    "Road: race / aggressive": "Rennrad: Race / sportlich",
    "Racing, crits, fast group rides. Lower and longer.": "Rennen, Kriterien, schnelle Gruppenausfahrten. Tiefer und gestreckter.",
    "Triathlon / TT": "Triathlon / Zeitfahren",
    "Triathlon / Time trial": "Triathlon / Zeitfahren",
    "Aero bars, long steady efforts. Aero but sustainable.": "Aufleger, lange gleichmäßige Belastung. Aerodynamisch, aber haltbar.",
    "Gravel / MTB": "Gravel / MTB",
    "MTB / Gravel": "MTB / Gravel",
    "Off-road control, more upright, wider bars.": "Kontrolle im Gelände, aufrechter, breiterer Lenker.",
    "City / hybrid": "City / Trekking",
    "City / hybrid / commuter": "City / Trekking / Pendler",
    "Commuting and casual riding. Upright and relaxed.": "Pendeln und entspanntes Fahren. Aufrecht und locker.",
    "Limited": "Eingeschränkt",
    "Can't touch toes with straight legs": "Mit gestreckten Beinen kommst du nicht an die Zehen",
    "Average": "Durchschnittlich",
    "Fingertips reach toes": "Fingerspitzen erreichen die Zehen",
    "Flexible": "Beweglich",
    "Palms reach the floor": "Handflächen erreichen den Boden",
    "Front of knee": "Vorderes Knie",
    "Back of knee": "Kniekehle",
    "Lower back": "Unterer Rücken",
    "Neck & shoulders": "Nacken & Schultern",
    "Hands or wrists": "Hände oder Handgelenke",
    "Saddle discomfort": "Sattelbeschwerden",

    "the crank circle ({v})": "den Kurbelkreis ({v})",
    "your height ({v})": "deine Körpergröße ({v})",

    # PDF
    "In range": "Im Bereich",
    "Borderline": "Grenzwertig",
    "Adjust": "Anpassen",
    "n/a": "k. A.",
    "Good": "Gute",
    "Fair": "Mittlere",
    "Poor": "Schlechte",
    "video": "Video",
    "photo": "Foto",
    "front/rear video": "Video vorne/hinten",
    "Rider: {name}   |   ": "Fahrer: {name}   |   ",
    "Visual assessment": "Bildauswertung",
    "Measured angles": "Gemessene Winkel",
    "What to adjust (in this order)": "Was du anpassen solltest (in dieser Reihenfolge)",
    "Fit calculations": "Fit-Berechnungen",
    "Cadence {c:.0f} rpm": "Trittfrequenz {c:.0f} U/min",
    "{n} pedal strokes modelled": "{n} Kurbelumdrehungen modelliert",
    "{g} capture quality": "{g} Aufnahmequalität",
    "Metric": "Messwert",
    "Value (95% range)": "Wert (95-%-Bereich)",
    "Target range": "Zielbereich",
    "Status": "Status",
    "Back & posture": "Rücken & Haltung",
    "Capture quality notes": "Hinweise zur Aufnahme",
    "Coach notes": "Coach-Notizen",
    "Crank length: {c:g} mm instead of {now:g} mm, with the saddle {dh:+.0f} mm, is predicted to give a {hip:.0f}° hip angle and {kf:.0f}° knee bend at the top.":
        "Kurbellänge: {c:g} mm statt {now:g} mm, mit Sattel {dh:+.0f} mm, ergibt laut Modell oben {hip:.0f}° Hüftwinkel und "
        "{kf:.0f}° Kniebeugung.",
    "Crank length by tibia length (41 %, Martin & Spirduso 2001, for peak power): {c:.0f} mm.":
        "Kurbellänge nach Tibialänge (41 %, Martin & Spirduso 2001, für Maximalleistung): {c:.0f} mm.",
    "Hip joint {x:.0f} mm behind and {y:.0f} mm above the bottom bracket.": "Hüftgelenk {x:.0f} mm hinter und {y:.0f} mm über dem Tretlager.",
    "Hands {x:.0f} mm ahead of the hip, {d:.0f} mm below it (drop).": "Hände {x:.0f} mm vor der Hüfte, {d:.0f} mm darunter (Überhöhung).",
    "Hands {x:.0f} mm ahead of the hip, {d:.0f} mm above it.": "Hände {x:.0f} mm vor der Hüfte, {d:.0f} mm darüber.",
    "Reach it in 3–5 mm steps.": "In Schritten von 3–5 mm annähern.",
    "Saddle height (BB to saddle top): now {now:.0f} mm, target {tgt:.0f} mm.": "Sattelhöhe (Tretlager bis Satteloberkante): jetzt {now:.0f} mm, Ziel {tgt:.0f} mm.",
    "Inseam formulas: LeMond {l:.0f} mm, Hamley {h:.0f} mm (BB to saddle top). Static starting points only.":
        "Schrittlängen-Formeln: LeMond {l:.0f} mm, Hamley {h:.0f} mm (Tretlager bis Satteloberkante). Nur statische Ausgangswerte.",
    "Ankle at the bottom of the stroke: {b:+.0f}° (+ = toe down), range {r:.0f}° over the stroke.":
        "Sprunggelenk unten im Tretzyklus: {b:+.0f}° (+ = Fußspitze nach unten), Bewegungsumfang {r:.0f}° über die Umdrehung.",
    "Aero estimate: frontal area {a:.2f} m², about {p:.0f} W of air drag at {v:.0f} km/h; 5° lower torso saves about {s:.0f} W. Rough estimate (Heil 2001, assumed Cd 0.7).":
        "Aero-Schätzung: Stirnfläche {a:.2f} m², etwa {p:.0f} W Luftwiderstand bei {v:.0f} km/h; 5° tieferer Oberkörper spart "
        "etwa {s:.0f} W. Grobe Schätzung (Heil 2001, angenommener Cd 0,7).",
    "BikeFit  |  Bike Fit Report": "BikeFit  |  Bikefitting-Bericht",
    "BikeFit - open-source bike fitting": "BikeFit - Open-Source-Bikefitting",
    "Page {n}  -  2D video estimate, not medical advice.": "Seite {n}  -  2D-Videoschätzung, keine medizinische Beratung.",
    "Style: {style}   |   {date}   |   Source: {src}": "Stil: {style}   |   {date}   |   Quelle: {src}",
    "Fit score: {s}/100": "Fit-Score: {s}/100",
    "Everything measured is within range for this style. If you're comfortable, keep it!":
        "Alle Messwerte liegen im Bereich für diesen Stil. Wenn du bequem sitzt, lass es so!",
    "{label}: back curve {r:.1f}% of back length{bulge}, rounded in {p:.0f}% of frames":
        "{label}: Rückenwölbung {r:.1f} % der Rückenlänge{bulge}, rund in {p:.0f} % der Bilder",
    "Posture score: {s}/100": "Haltungs-Score: {s}/100",
    "Avg stroke {a:.2f} s   |   fastest stroke {fn} ({fd:.2f} s)   |   slowest stroke {sn} ({sd:.2f} s)   |   variation {cv:.0f}%":
        "Ø Umdrehung {a:.2f} s   |   schnellste {fn} ({fd:.2f} s)   |   langsamste {sn} ({sd:.2f} s)   |   Schwankung {cv:.0f} %",
}
