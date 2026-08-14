// CrowdPilot AI — Recommendation Panel
// P2 UI component
// Currently supports mock/P3 recommendation data.
// The recommendation object must contain:
// action, from_node, to_node, redirect_percentage,
// reason, expected_effect

export default function RecommendationPanel({
  recommendation,
  onApply,
  applying = false,
}) {
  // ==========================================
  // NO RECOMMENDATION
  // ==========================================

  if (!recommendation) {
    return (
      <section className="panel recommendation-panel">

        <div className="panel-header">
          <h2>AI Recommendation</h2>
        </div>

        <p className="muted">
          Monitoring crowd conditions...
        </p>

      </section>
    );
  }

  // ==========================================
  // RECOMMENDATION
  // ==========================================

  return (
    <section className="panel recommendation-panel">

      {/* ======================================
          HEADER
      ======================================= */}

      <div className="panel-header">

        <div>
          <h2>AI Recommendation</h2>

          <p className="muted">
            Recommended action based on current
            congestion
          </p>
        </div>

        <span className="recommendation-badge">
          AI
        </span>

      </div>


      {/* ======================================
          RECOMMENDED ACTION
      ======================================= */}

      <div className="recommendation-action">

        <span className="action-label">
          Recommended Action
        </span>

        <h3>
          {recommendation.action ||
            "Redirect crowd flow"}
        </h3>

      </div>


      {/* ======================================
          ROUTE
      ======================================= */}

      {(recommendation.from_node ||
        recommendation.to_node) && (

        <div className="recommendation-route">

          <span className="action-label">
            Reroute
          </span>

          <strong>
            {recommendation.from_node ||
              "—"}

            {" → "}

            {recommendation.to_node ||
              "—"}
          </strong>

        </div>

      )}


      {/* ======================================
          DETAILS
      ======================================= */}

      <div className="recommendation-details">

        <div className="recommendation-stat">

          <span>
            Redirect
          </span>

          <strong>
            {recommendation.redirect_percentage ??
              0}
            %
          </strong>

        </div>


        <div className="recommendation-stat">

          <span>
            Expected Effect
          </span>

          <strong>
            Reduce congestion
          </strong>

        </div>

      </div>


      {/* ======================================
          WHY
      ======================================= */}

      <div className="recommendation-reason">

        <span className="reason-label">
          Why?
        </span>

        <p>
          {recommendation.reason ||
            "Crowd conditions indicate that an alternative route may reduce congestion."}
        </p>

      </div>


      {/* ======================================
          EXPECTED EFFECT
      ======================================= */}

      <div className="recommendation-effect">

        <span className="reason-label">
          Expected Effect
        </span>

        <p>
          {recommendation.expected_effect ||
            "Reduce congestion at the affected location."}
        </p>

      </div>


      {/* ======================================
          APPLY
      ======================================= */}

      <button
        className="apply-button"
        onClick={() => onApply(recommendation)}
        disabled={applying}
      >
        {applying
          ? "Applying..."
          : "Apply Recommendation"}
      </button>

    </section>
  );
}