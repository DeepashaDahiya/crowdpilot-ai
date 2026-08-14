// CrowdPilot AI — Recommendation Panel
// Uses contract.json/mock data for now.
// Later this will receive P3's live /recommendation response.

export default function RecommendationPanel({
  recommendation,
  onApply,
  applying = false,
}) {
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

  return (
    <section className="panel recommendation-panel">
      <div className="panel-header">
        <div>
          <h2>AI Recommendation</h2>
          <p className="panel-subtitle">
            Recommended action based on current congestion
          </p>
        </div>

        <span className="recommendation-badge">
          AI
        </span>
      </div>

      <div className="recommendation-action">
        <span className="action-label">
          Recommended Action
        </span>

        <h3>
          {recommendation.action}
        </h3>
      </div>

      <div className="recommendation-details">
        <div className="recommendation-stat">
          <span>Redirect</span>
          <strong>
            {recommendation.redirect_percentage}%
          </strong>
        </div>

        <div className="recommendation-stat">
          <span>Expected Effect</span>
          <strong>
            Reduce congestion
          </strong>
        </div>
      </div>

      <div className="recommendation-reason">
        <span className="reason-label">
          Why?
        </span>

        <p>
          {recommendation.reason}
        </p>
      </div>

      <div className="recommendation-effect">
        <span className="reason-label">
          Expected Effect
        </span>

        <p>
          {recommendation.expected_effect}
        </p>
      </div>

      <button
        className="apply-button"
        onClick={onApply}
        disabled={applying}
      >
        {applying
          ? "Applying..."
          : "Apply Recommendation"}
      </button>
    </section>
  );
}