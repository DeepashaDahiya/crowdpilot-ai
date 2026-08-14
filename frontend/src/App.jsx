// CrowdPilot AI — dashboard
// Person 2: VenueMap + KPI Cards + analytics
// Person 3: RecommendationPanel can be connected to live API later

import { useEffect, useState } from "react";
import VenueMap from "./components/VenueMap";
import BeforeAfter from "./components/BeforeAfter";
import RecommendationPanel from "./components/RecommendationPanel";
import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

export default function App() {
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);
  const [backendOnline, setBackendOnline] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const [recommendation, setRecommendation] =
    useState(null);

  const [applyingRecommendation, setApplyingRecommendation] =
    useState(false);

  // ==========================================
  

  // ==========================================
  // FETCH ANALYTICS
  // ==========================================

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

      // Update analytics
      setAnalysis(data);

      // Backend is working
      setBackendOnline(true);

      // Clear previous error
      setError(null);

      // Store latest successful update time
      setLastUpdated(new Date());

      // Fetch live AI recommendation
      try {
        const recResponse = await fetch(`${API_URL}/recommendation`, {
          method: "POST",
        });
        const recData = await recResponse.json();
        setRecommendation(recData.recommendation || null);
      } catch (recErr) {
        console.error("Failed to fetch recommendation:", recErr);
        setRecommendation(null);
      }

    } catch (err) {
      console.error(err);

      setBackendOnline(false);

      setError(
        "Unable to connect to CrowdPilot backend."
      );
    }
  }

  // ==========================================
  // APPLY RECOMMENDATION
  // ==========================================

  async function handleApplyRecommendation() {
    if (!recommendation) return;

    try {
      setApplyingRecommendation(true);

      const response = await fetch(`${API_URL}/apply-recommendation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          from_node: recommendation.from_node,
          to_node: recommendation.to_node,
          redirect_percentage: recommendation.redirect_percentage,
        }),
      });

      const result = await response.json();
      console.log("Recommendation applied:", result);

      // Refresh analytics right away to show the effect
      await fetchAnalysis();

    } catch (err) {
      console.error("Failed to apply recommendation:", err);
    } finally {
      setApplyingRecommendation(false);
    }
  }

  // ==========================================
  // REAL-TIME POLLING
  // ==========================================

  useEffect(() => {
    // Fetch immediately
    fetchAnalysis();

    // Fetch every second
    const interval = setInterval(
      fetchAnalysis,
      1000
    );

    // Cleanup
    return () => {
      clearInterval(interval);
    };
  }, []);

  // ==========================================
  // LOADING
  // ==========================================

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
            Loading crowd analytics...
          </h2>

          <p>
            Connecting to the CrowdPilot backend.
          </p>
        </div>

      </div>
    );
  }

  // ==========================================
  // ERROR
  // ==========================================

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
            onClick={fetchAnalysis}
          >
            Retry Connection
          </button>

        </div>

      </div>
    );
  }

  // ==========================================
  // SAFE DATA VALUES
  // ==========================================

  const crowd = analysis?.crowd ?? {
    total: 0,
    moving: 0,
  };

  const metrics = analysis?.metrics ?? {
    congestion_score: 0,
    average_wait: 0,
    predictions: [],
  };

  const bottlenecks =
    analysis?.bottlenecks ?? [];

  const highestRisk =
    bottlenecks.length > 0
      ? bottlenecks[0]
      : null;

  const predictions =
    metrics.predictions ?? [];

  // ==========================================
  // MAIN DASHBOARD
  // ==========================================

  return (
    <div className="app">

      {/* =====================================
          HEADER
      ====================================== */}

      <header className="header">

        <div>

          <h1>
            CrowdPilot AI
          </h1>

          <p>
            Real-Time Crowd Intelligence
          </p>

        </div>

        {/* Backend status */}

        <div className="live-indicator">

          <span
            className={
              backendOnline
                ? "live-dot online"
                : "live-dot offline"
            }
          />

          {backendOnline
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


      {/* =====================================
          VENUE
      ====================================== */}

      <section className="venue-section">

        <h2>
          {analysis?.venue || "stadium_01"}
        </h2>

        <p>
          Monitoring crowd movement
          and congestion
        </p>

      </section>


      {/* =====================================
          KPI CARDS
      ====================================== */}

      <section className="kpi-grid">

        {/* Crowd Size */}

        <div className="kpi-card">

          <div className="kpi-label">
            CROWD SIZE
          </div>

          <div className="kpi-value">
            {crowd.total}
          </div>

          <div className="kpi-subtext">

            {crowd.moving}

            {" "}currently moving

          </div>

        </div>


        {/* Congestion Score */}

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


        {/* Average Wait */}

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


        {/* Highest Risk */}

        <div
          className={
            highestRisk &&
            highestRisk.status === "critical"
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


      {/* =====================================
          MAIN DASHBOARD
      ====================================== */}

      <div className="dashboard-grid">


        {/* ===================================
            LEFT — VENUE MAP
        ==================================== */}

        <main className="map-column">

          <VenueMap
            analysis={analysis}
          />

        </main>


        {/* ===================================
            RIGHT — ALERTS + PREDICTIONS +
            RECOMMENDATION
        ==================================== */}

        <aside className="side-column">


          {/* =================================
              CONGESTION ALERT
          ================================== */}

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

                    {highestRisk.status}
                    {" "}congestion.

                  </p>

                </div>

              </div>

            ) : (

              <p className="muted">
                No active congestion alerts.
              </p>

            )}

          </section>


          {/* =================================
              PREDICTIONS
          ================================== */}

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

                    ⚠️{" "}

                    {prediction}

                  </div>

                )
              )

            ) : (

              <p className="muted">
                No increasing congestion
                predicted.
              </p>

            )}

          </section>


          {/* =================================
              AI RECOMMENDATION
          ================================== */}

          <RecommendationPanel
            recommendation={recommendation}
            onApply={
              handleApplyRecommendation
            }
            applying={
              applyingRecommendation
            }
          />

        </aside>

      </div>


      {/* =====================================
          BEFORE / AFTER
      ====================================== */}

      <BeforeAfter
        analysis={analysis}
      />

    </div>
  );
}