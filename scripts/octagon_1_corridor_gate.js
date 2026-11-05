/* Candidate exports are never permission to march into an unverified neighbor. */
(function (root) {
  "use strict";
  const reviewed = value => value && value.review === "verified"
    && typeof value.source === "string" && !!value.source.trim()
    && typeof value.reviewer === "string" && !!value.reviewer.trim();
  const point = value => Array.isArray(value) && value.length === 2
    && value.every(n => typeof n === "number" && Number.isFinite(n))
    && value[0] >= 0 && value[0] <= 1100 && value[1] >= 0 && value[1] <= 842;
  function connectionStatus(edge) {
    if (!edge || typeof edge !== "object" || Array.isArray(edge))
      return { traversable: false, reasons: ["invalid_edge"] };
    const reasons = [];
    if (edge.status !== "verified") reasons.push("unverified_status");
    if (!point(edge.exit) || !point(edge.entry) || edge.exit[0] !== 1100
        || edge.entry[0] !== 0 || Math.abs(edge.exit[1] - edge.entry[1]) > .01)
      reasons.push("unmatched_seam");
    if (!edge.fromCell || !edge.toCell || edge.fromCell === edge.toCell
        || typeof edge.fromCell !== "string" || typeof edge.toCell !== "string")
      reasons.push("missing_neighbor");
    for (const field of ["routeArt", "terrainAccess", "neighborArt"])
      if (!reviewed(edge[field])) reasons.push("unverified_" + field);
    if (typeof edge.crossesRiver !== "boolean") reasons.push("unknown_crossing");
    else if (edge.crossesRiver && !reviewed(edge.bridgeOrFord))
      reasons.push("unverified_crossing");
    return { traversable: reasons.length === 0, reasons };
  }
  function authoringExportStatus(exported, evidence) {
    const edge = evidence && exported
      ? { ...evidence, exit: exported.eastEdge, entry: exported.neighborEntry } : null;
    const review = connectionStatus(edge);
    const reasons = review.reasons.slice();
    if (!exported || exported.kind !== "octagon-1-art-authored-candidate"
        || exported.schemaVersion !== 1) reasons.push("invalid_export");
    if (!exported || exported.approvedForProduction !== false)
      reasons.push("unexpected_approval");
    reasons.push("authoring_export_requires_independent_approval");
    return { traversable: false, reasons: [...new Set(reasons)] };
  }
  const api = Object.freeze({ connectionStatus, authoringExportStatus });
  root.Octagon1CorridorGate = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
