import { useEffect, useRef, useState } from "react";
import VenueMap from "./components/VenueMap";
import BeforeAfter from "./components/BeforeAfter";
import RecommendationPanel from "./components/RecommendationPanel";
import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const POLL_INTERVAL = 1000;
const AFTER_DELAY_MS = 3000;

export default function App() {
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);
  const [backendOnline, setBackendOnline] = useState(false);
  const [simulationRunning, setSimulationRunning] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const [recommendation, setRecommendation] = useState(null);
  const [applyingRecommendation, setApplyingRecommendation] =
    useState(false);

  const [beforeSnapshot, setBeforeSnapshot] = useState(null);
  const [afterSnapshot, setAfterSnapshot] = useState(null);
  const [appliedRoute, setAppliedRoute] = useState(null);

  const applyTimestampRef = useRef(null);
  const afterCapturedRef = useRef(false);

  async function startSimulation() {
    try {
      const response = await fetch(
        `${API_URL}/simulation/start`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error(
          `Simulation start failed: ${response.status}`
        );
      }

      const data = await response.json();

      console.log("Simulation started:", data);

      setSimulationRunning(true);
      setError(null);
    } catch (err) {
      console.error("Simulation start error:", err);

      setSimulationRunning(false);
      setError(
        "Backend is running, but the simulation could not be started."
      );
    }
  }

  async function fetchAnalysis() {
    try {
      const response = await fetch(
        `${API_URL}/analysis`
      );

      if (!response.ok) {
        throw new Error(
          `API error: ${response.status}`
        );
      }

      const data = await response.json();

      console.log("Analysis:", data);

      setAnalysis(data);
      setBackendOnline(true);
      setError(null);
      setLastUpdated(new Date());

      const bottlenecks = data.bottlenecks || [];
      const alternatives = data.alternatives || [];

      if (bottlenecks.length > 0) {
        const bottleneck = bottlenecks[0];

        const exitAlternative = alternatives.find(
          (item) =>
            item.node_id &&
            item.node_id.startsWith("exit_")
        );

        if (exitAlternative) {
          const displayName = exitAlternative.node_id
            .replace("_", " ")
            .replace(/\b\w/g, (c) => c.toUpperCase());

          setRecommendation({
            action: `Open ${displayName}`,
            from_node: bottleneck.node_id,
            to_node: exitAlternative.node_id,
            redirect_percentage: 30,
            reason:
              `${bottleneck.node_id} is experiencing ` +
              `${bottleneck.status} congestion while ` +
              `${exitAlternative.node_id} has available capacity.`,
            expected_effect:
              `Reduce congestion around ${bottleneck.node_id}.`,
          });
        }
      } else {
        setRecommendation(null);
      }

      if (
        applyTimestampRef.current !== null &&
        !afterCapturedRef.current
      ) {
        const elapsed =
          Date.now() - applyTimestampRef.current;

        if (elapsed >= AFTER_DELAY_MS) {
          setAfterSnapshot(data);
          afterCapturedRef.current = true;
        }
      }
    } catch (err) {
      console.error("Analysis error:", err);

      setBackendOnline(false);
      setError(
        "Unable to connect to CrowdPilot backend."
      );
    }
  }

  async function handleApplyRecommendation(
    selectedRecommendation
  ) {
    if (!selectedRecommendation) {
      return;
    }

    try {
      setApplyingRecommendation(true);

      if (analysis) {
        setBeforeSnapshot(analysis);
      }

      const fromNode =
        selectedRecommendation.from_node;

      const toNode =
        selectedRecommendation.to_node;

      const redirectPercentage =
        selectedRecommendation.redirect_percentage ?? 0;

      if (!fromNode || !toNode) {
        throw new Error(
          "Recommendation is missing from_node or to_node."
        );
      }

      setAppliedRoute({
        from_node: fromNode,
        to_node: toNode,
        redirect_percentage: redirectPercentage,
      });

      setAfterSnapshot(null);

      afterCapturedRef.current = false;
      applyTimestampRef.current = Date.now();

      const response = await fetch(
        `${API_URL}/simulation/reroute`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            from_node: fromNode,
            to_node: toNode,
            redirect_percentage:
              redirectPercentage,
          }),
        }
      );

      if (!response.ok) {
        const text = await response.text();

        throw new Error(
          `Reroute failed: ${response.status} ${text}`
        );
      }

      const result = await response.json();

      console.log(
        "Reroute applied:",
        result
      );
    } catch (err) {
      console.error(
        "Apply recommendation error:",
        err
      );

      applyTimestampRef.current = null;
      afterCapturedRef.current = true;

      setAfterSnapshot(null);
      setAppliedRoute(null);
      setBeforeSnapshot(null);

      setError(
        `Unable to apply recommendation: ${err.message}`
      );
    } finally {
      setApplyingRecommendation(false);
    }
  }

  useEffect(() => {
    async function initialize() {
      await startSimulation();
      await fetchAnalysis();
    }

    initialize();

    const interval = setInterval(
      fetchAnalysis,
      POLL_INTERVAL
    );

    return () => {
      clearInterval(interval);
    };
  }, []);

  if (!analysis && !error) {
    return (
      <div className="app">
        <header className="header">
          <div>
            <h1>CrowdPilot AI</h1>
            <p>
              Real-Time Crowd Intelligence
            </p>
          </div>

          <div className="live-indicator">
            <span className="live-dot offline" />
            CONNECTING...
          </div>
        </header>

        <div className="loading-state">
          <h2>
            Starting crowd simulation...
          </h2>

          <p>
            Connecting to CrowdPilot backend.
          </p>
        </div>
      </div>
    );
  }

  if (!analysis && error) {
    return (
      <div className="app">
        <header className="header">
          <div>
            <h1>CrowdPilot AI</h1>
            <p>
              Real-Time Crowd Intelligence
            </p>
          </div>

          <div className="live-indicator">
            <span className="live-dot offline" />
            OFFLINE
          </div>
        </header>

        <div className="error-state">
          <h2>
            CrowdPilot backend unavailable
          </h2>

          <p className="error">
            {error}
          </p>

          <button
            className="retry-button"
            onClick={startSimulation}
          >
            Start Simulation
          </button>
        </div>
      </div>
    );
  }

  const crowd = analysis?.crowd || {
    total: 0,
    moving: 0,
  };

  const metrics = analysis?.metrics || {
    congestion_score: 0,
    average_wait: 0,
    predictions: [],
  };

  const bottlenecks =
    analysis?.bottlenecks || [];

  const highestRisk =
    bottlenecks.length > 0
      ? bottlenecks[0]
      : null;

  const predictions =
    metrics.predictions || [];

  return (
    <div className="app">

      <header className="header">
        <div>
          <h1>CrowdPilot AI</h1>

          <p>
            Real-Time Crowd Intelligence
          </p>
        </div>

        <div className="live-indicator">
          <span
            className={
              backendOnline && simulationRunning
                ? "live-dot online"
                : "live-dot offline"
            }
          />

          {backendOnline && simulationRunning
            ? "LIVE"
            : "OFFLINE"}

          {lastUpdated && (
            <span className="last-updated">
              Updated{" "}
              {lastUpdated.toLocaleTimeString()}
            </span>
          )}
        </div>
      </header>

      <section className="venue-section">
        <h2>
          {analysis?.venue || "stadium_01"}
        </h2>

        <p>
          Monitoring crowd movement and congestion
        </p>
      </section>

      <section className="kpi-grid">

        <div className="kpi-card">
          <div className="kpi-label">
            CROWD SIZE
          </div>

          <div className="kpi-value">
            {crowd.total}
          </div>

          <div className="kpi-subtext">
            {crowd.moving} currently moving
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">
            CONGESTION SCORE
          </div>

          <div className="kpi-value">
            {metrics.congestion_score}
          </div>

          <div className="kpi-subtext">
            Overall venue congestion
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">
            AVERAGE WAIT
          </div>

          <div className="kpi-value">
            {metrics.average_wait}
            <span className="unit">
              {" "}sec
            </span>
          </div>

          <div className="kpi-subtext">
            Current estimated wait
          </div>
        </div>

        <div
          className={
            highestRisk?.status === "critical"
              ? "kpi-card critical-card"
              : "kpi-card"
          }
        >
          <div className="kpi-label">
            HIGHEST RISK
          </div>

          {highestRisk ? (
            <>
              <div className="kpi-value risk">
                {highestRisk.node_id}
              </div>

              <div className="kpi-subtext">
                {Math.round(
                  highestRisk.severity * 100
                )}
                % utilization ·{" "}
                {highestRisk.status}
              </div>
            </>
          ) : (
            <div className="kpi-value">
              None
            </div>
          )}
        </div>

      </section>

      <div className="dashboard-grid">

        <main className="map-column">
          <VenueMap
            analysis={analysis}
          />
        </main>

        <aside className="side-column">

          <section className="panel">
            <div className="panel-header">
              <h2>
                Congestion Alerts
              </h2>
            </div>

            {highestRisk ? (
              <div className="alert">
                <div className="alert-icon">
                  !
                </div>

                <div>
                  <strong>
                    {highestRisk.node_id}
                  </strong>

                  <p>
                    {Math.round(
                      highestRisk.severity * 100
                    )}
                    % utilization —{" "}
                    {highestRisk.status} congestion.
                  </p>
                </div>
              </div>
            ) : (
              <p className="muted">
                No active congestion alerts.
              </p>
            )}
          </section>

          <section className="panel">
            <div className="panel-header">
              <h2>
                Predictions
              </h2>
            </div>

            {predictions.length > 0 ? (
              predictions.map(
                (prediction, index) => (
                  <div
                    className="prediction"
                    key={index}
                  >
                    ⚠️ {prediction}
                  </div>
                )
              )
            ) : (
              <p className="muted">
                No increasing congestion predicted.
              </p>
            )}
          </section>

          <RecommendationPanel
            recommendation={recommendation}
            onApply={() =>
              handleApplyRecommendation(
                recommendation
              )
            }
            applying={
              applyingRecommendation
            }
          />

        </aside>
      </div>

      <BeforeAfter
        before={beforeSnapshot}
        after={afterSnapshot}
        appliedRoute={appliedRoute}
      />

    </div>
  );
}