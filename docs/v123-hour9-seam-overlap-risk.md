# V123 octagon seam safety risk

The V122 seam validator checks coincident road endpoints and collinear shared border length, but does not independently reject tiles whose polygon interiors overlap. Two identical tiles with coincident road endpoints can appear to form a valid seam despite being stacked, not adjacent. Add a convex polygon separating-axis overlap guard and a regression test before permitting these seams in gameplay. Preserve the existing production-disabled status.
