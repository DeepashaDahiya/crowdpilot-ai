export default function BeforeAfter({ analysis }) {
  if (!analysis) {
    return null;
  }

  const bottleneck =
    analysis.bottlenecks?.[0];

  const alternatives =
    analysis.alternatives ?? [];

  const currentScore =
    analysis.metrics?.congestion_score ?? 0;

  const currentRisk =
    bottleneck
      ? Math.round(bottleneck.severity * 100)
      : 0;

  const recommendedAlternative =
    alternatives.length > 0
      ? alternatives[0]
      : null;

  // Simple projected improvement for the prototype.
  const projectedScore = Math.max(
    0,
    currentScore - 20
  );

  return (
    <section className="before-after panel">

      <div className="panel-header">
        <div>
          <h2>Before / After</h2>

          <p className="muted">
            Prototype Projection
          </p>
        </div>
      </div>


      <div className="comparison-grid">

        {/* BEFORE */}

        <div className="comparison-card">

          <div className="comparison-title">
            BEFORE
          </div>

          <div className="comparison-risk">
            {bottleneck
              ? bottleneck.node_id
              : "No bottleneck"}
          </div>

          <div className="comparison-value">
            {currentRisk}%
          </div>

          <div className="comparison-label">
            Highest utilization
          </div>

          <div className="comparison-score">
            Congestion score:{" "}
            <strong>
              {currentScore}
            </strong>
          </div>

        </div>


        {/* ARROW */}

        <div className="comparison-arrow">
          →
        </div>


        {/* AFTER */}

        <div className="comparison-card">

          <div className="comparison-title">
            AFTER
          </div>

          <div className="comparison-risk">
            {recommendedAlternative
              ? recommendedAlternative.node_id
              : "Alternative unavailable"}
          </div>

          <div className="comparison-value">
            {projectedScore}
          </div>

          <div className="comparison-label">
            Prototype score
          </div>

          {recommendedAlternative && (
            <div className="comparison-score">
              Available capacity:{" "}
              <strong>
                {recommendedAlternative.available_capacity}
              </strong>
            </div>
          )}

        </div>

      </div>

    </section>
  );
}