export default function BeforeAfter({
  before,
  after,
  appliedRoute,
}) {
  if (!before) {
    return null;
  }

  const getNode = (snapshot, nodeId) => {
    return snapshot?.nodes?.find(
      (node) => node.id === nodeId
    );
  };

  const fromBefore = getNode(
    before,
    appliedRoute?.from_node
  );

  const toBefore = getNode(
    before,
    appliedRoute?.to_node
  );

  const fromAfter = getNode(
    after,
    appliedRoute?.from_node
  );

  const toAfter = getNode(
    after,
    appliedRoute?.to_node
  );

  return (
    <section className="before-after">

      <div className="before-after-header">
        <div>
          <h2>Before / After</h2>
          <p>
            Live impact of the applied reroute
          </p>
        </div>

        {appliedRoute && (
          <div className="route-badge">
            {appliedRoute.from_node}
            {" → "}
            {appliedRoute.to_node}
          </div>
        )}
      </div>

      <div className="before-after-grid">

        {/* BEFORE */}

        <div className="snapshot-card">

          <h3>BEFORE</h3>

          <div className="snapshot-metric">
            <span>Congestion Score</span>
            <strong>
              {before.metrics?.congestion_score ?? "—"}
            </strong>
          </div>

          <div className="snapshot-metric">
            <span>Average Wait</span>
            <strong>
              {before.metrics?.average_wait ?? "—"} sec
            </strong>
          </div>

          <div className="snapshot-metric">
            <span>
              {appliedRoute?.from_node ?? "Source"}
              {" "}Utilization
            </span>

            <strong>
              {fromBefore
                ? `${Math.round(
                    fromBefore.utilization * 100
                  )}%`
                : "—"}
            </strong>
          </div>

          <div className="snapshot-route">
            {appliedRoute
              ? `${appliedRoute.from_node} → ${appliedRoute.to_node}`
              : "No reroute applied"}
          </div>

        </div>


        {/* AFTER */}

        <div className="snapshot-card">

          <h3>AFTER</h3>

          {!after ? (

            <p className="muted">
              Waiting for the reroute to settle...
            </p>

          ) : (

            <>
              <div className="snapshot-metric">
                <span>Congestion Score</span>
                <strong>
                  {after.metrics?.congestion_score ?? "—"}
                </strong>
              </div>

              <div className="snapshot-metric">
                <span>Average Wait</span>
                <strong>
                  {after.metrics?.average_wait ?? "—"} sec
                </strong>
              </div>

              <div className="snapshot-metric">
                <span>
                  {appliedRoute?.from_node ?? "Source"}
                  {" "}Utilization
                </span>

                <strong>
                  {fromAfter
                    ? `${Math.round(
                        fromAfter.utilization * 100
                      )}%`
                    : "—"}
                </strong>
              </div>

              <div className="snapshot-route">
                {appliedRoute
                  ? `${appliedRoute.from_node} → ${appliedRoute.to_node}`
                  : "—"}
              </div>

            </>

          )}

        </div>

      </div>

    </section>
  );
}