// CrowdPilot AI — dashboard
// Person 2: VenueMap + KPI Cards + analytics
// Person 3: RecommendationPanel can be added later

import { useEffect, useState } from "react";
import VenueMap from "./components/VenueMap";
import BeforeAfter from "./components/BeforeAfter";
import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";


export default function App() {

  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);
  const [backendOnline, setBackendOnline] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);


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

    } catch (err) {

      console.error(err);

      setBackendOnline(false);

      setError(
        "Unable to connect to CrowdPilot backend."
      );
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

        <h1>
          CrowdPilot AI
        </h1>

        <p>
          Loading crowd analytics...
        </p>

      </div>
    );
  }


  // ==========================================
  // ERROR
  // ==========================================

  if (!analysis && error) {

    return (
      <div className="app">

        <h1>
          CrowdPilot AI
        </h1>

        <p className="error">
          {error}
        </p>

      </div>
    );
  }


  // ==========================================
  // HIGHEST RISK NODE
  // ==========================================

  const highestRisk =
    analysis?.bottlenecks?.length > 0
      ? analysis.bottlenecks[0]
      : null;


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
          {analysis.venue}
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
            {analysis.crowd.total}
          </div>

          <div className="kpi-subtext">
            {analysis.crowd.moving}
            {" "}currently moving
          </div>

        </div>


        {/* Congestion Score */}

        <div className="kpi-card">

          <div className="kpi-label">
            CONGESTION SCORE
          </div>

          <div className="kpi-value">
            {analysis.metrics.congestion_score}
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

            {analysis.metrics.average_wait}

            <span className="unit">
              {" "}sec
            </span>

          </div>

          <div className="kpi-subtext">
            Current estimated wait
          </div>

        </div>


        {/* Highest Risk */}

        <div className="kpi-card">

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
            RIGHT — ALERTS + PREDICTIONS
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

              <p>
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


            {analysis.metrics.predictions?.length > 0 ? (

              analysis.metrics.predictions.map(
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