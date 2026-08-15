import React, { useEffect, useMemo, useState } from "react";


// =====================================================
// NODE COLORS
// =====================================================

function utilizationToColor(value) {
  if (value < 0.6) {
    return "#22c55e";
  }

  if (value < 0.8) {
    return "#eab308";
  }

  if (value < 0.9) {
    return "#f97316";
  }

  return "#ef4444";
}


// =====================================================
// NODE LOOKUP
// =====================================================

function getNode(analysis, id) {
  return (
    analysis?.nodes?.find(
      (node) => node.id === id
    ) || null
  );
}


// =====================================================
// VENUE POSITIONS
// =====================================================

const POSITIONS = {
  gate_a: {
    x: 75,
    y: 285,
  },

  corridor_1: {
    x: 210,
    y: 285,
  },

  corridor_2: {
    x: 340,
    y: 285,
  },

  corridor_3: {
    x: 470,
    y: 285,
  },

  main_hall: {
    x: 600,
    y: 285,
  },

  food_court: {
    x: 600,
    y: 505,
  },

  exit_a: {
    x: 1060,
    y: 115,
  },

  exit_b: {
    x: 1080,
    y: 285,
  },

  exit_c: {
    x: 1050,
    y: 500,
  },
};


// =====================================================
// DETERMINISTIC RANDOM
// =====================================================

function random(seed) {
  const value =
    Math.sin(seed * 999.123) *
    43758.5453;

  return (
    value -
    Math.floor(value)
  );
}


// =====================================================
// SCATTER CROWD
// =====================================================

function getCrowdPosition(
  nodeId,
  index
) {
  const rx =
    random(index * 13 + 4);

  const ry =
    random(index * 31 + 8);

  // -----------------------------------------------
  // MAIN HALL
  // -----------------------------------------------

  if (
    nodeId === "main_hall" ||
    nodeId === "corridor_1" ||
    nodeId === "corridor_2" ||
    nodeId === "corridor_3"
  ) {
    return {
      x:
        300 +
        rx * 450,

      y:
        175 +
        ry * 210,
    };
  }


  // -----------------------------------------------
  // GATE
  // -----------------------------------------------

  if (nodeId === "gate_a") {
    return {
      x:
        80 +
        rx * 160,

      y:
        265 +
        ry * 45,
    };
  }


  // -----------------------------------------------
  // FOOD COURT
  // -----------------------------------------------

  if (nodeId === "food_court") {
    return {
      x:
        470 +
        rx * 250,

      y:
        460 +
        ry * 75,
    };
  }


  // -----------------------------------------------
  // EXIT A
  // -----------------------------------------------

  if (nodeId === "exit_a") {
    return {
      x:
        950 +
        rx * 100,

      y:
        80 +
        ry * 90,
    };
  }


  // -----------------------------------------------
  // EXIT B
  // -----------------------------------------------

  if (nodeId === "exit_b") {
    return {
      x:
        950 +
        rx * 100,

      y:
        255 +
        ry * 60,
    };
  }


  // -----------------------------------------------
  // EXIT C
  // -----------------------------------------------

  if (nodeId === "exit_c") {
    return {
      x:
        950 +
        rx * 100,

      y:
        470 +
        ry * 60,
    };
  }


  return {
    x: 600,
    y: 285,
  };
}


// =====================================================
// DESTINATION COLOR
// =====================================================

function getCrowdColor(agent) {
  if (
    agent.destination ===
    "exit_a"
  ) {
    return "#f97316";
  }

  if (
    agent.destination ===
    "exit_b"
  ) {
    return "#22c55e";
  }

  if (
    agent.destination ===
    "exit_c"
  ) {
    return "#06b6d4";
  }

  return "#2563eb";
}


// =====================================================
// VENUE NODE
// =====================================================

function VenueNode({
  x,
  y,
  label,
  node,
}) {
  const utilization =
    node?.utilization ?? 0;

  const color =
    utilizationToColor(
      utilization
    );

  return (
    <g>

      <circle
        cx={x}
        cy={y}
        r="30"
        fill="white"
        stroke={color}
        strokeWidth="2"
        opacity="0.35"
      />

      <circle
        cx={x}
        cy={y}
        r="23"
        fill="white"
        stroke={color}
        strokeWidth="3"
      />

      <text
        x={x}
        y={y + 5}
        textAnchor="middle"
        fontSize="12"
        fontWeight="700"
        fill="#0f172a"
      >
        {Math.round(
          utilization * 100
        )}
        %
      </text>

      <text
        x={x}
        y={y + 46}
        textAnchor="middle"
        fontSize="12"
        fontWeight="600"
        fill="#334155"
      >
        {label}
      </text>

    </g>
  );
}


// =====================================================
// MAIN COMPONENT
// =====================================================

export default function VenueMap({
  analysis,
}) {

  const backendAgents =
    analysis?.agents || [];

  const total =
    analysis?.crowd?.total ?? 0;

  const moving =
    analysis?.crowd?.moving ?? 0;

  const congestion =
    analysis?.metrics
      ?.congestion_score ?? 0;


  // ===================================================
  // CREATE VISIBLE AGENTS
  //
  // IMPORTANT:
  // Even if backend says moving = 0,
  // we still show the existing crowd.
  // ===================================================

  const visibleAgents =
    useMemo(() => {

      if (
        backendAgents.length > 0
      ) {
        return backendAgents
          .slice(0, 250);
      }

      return [];
    }, [backendAgents]);


  // ===================================================
  // LOCAL ANIMATION STATE
  // ===================================================

  const [animationTick, setAnimationTick] =
    useState(0);


  useEffect(() => {

    const interval =
      setInterval(() => {

        setAnimationTick(
          value => value + 1
        );

      }, 80);

    return () => {
      clearInterval(interval);
    };

  }, []);


  // ===================================================
  // COMPUTE CROWD POSITIONS
  // ===================================================

  const crowdDots =
    useMemo(() => {

      return visibleAgents.map(
        (agent, index) => {

          const current =
            getCrowdPosition(
              agent.current_node,
              index
            );

          const destination =
            getCrowdPosition(
              agent.destination,
              index
            );


          /*
           * Each dot gets a slightly
           * different movement phase.
           */

          const phase =
            (index * 0.137) +
            animationTick * 0.035;


          /*
           * Smooth movement.
           */

          const progress =
            (
              Math.sin(phase) +
              1
            ) / 2;


          /*
           * Keep most of the crowd
           * inside the hall.
           *
           * Dots only gradually move
           * toward their destination.
           */

          const x =
            current.x +
            (
              destination.x -
              current.x
            ) *
            progress *
            0.35;


          const y =
            current.y +
            (
              destination.y -
              current.y
            ) *
            progress *
            0.35;


          /*
           * Small organic movement.
           */

          const wobbleX =
            Math.sin(
              phase * 2.1
            ) * 4;

          const wobbleY =
            Math.cos(
              phase * 1.7
            ) * 4;


          return {
            id:
              agent.id ??
              `agent-${index}`,

            x:
              x + wobbleX,

            y:
              y + wobbleY,

            color:
              getCrowdColor(
                agent
              ),
          };
        }
      );

    }, [
      visibleAgents,
      animationTick,
    ]);


  // ===================================================
  // NODES
  // ===================================================

  const gateA =
    getNode(
      analysis,
      "gate_a"
    );

  const mainHall =
    getNode(
      analysis,
      "main_hall"
    );

  const foodCourt =
    getNode(
      analysis,
      "food_court"
    );

  const exitA =
    getNode(
      analysis,
      "exit_a"
    );

  const exitB =
    getNode(
      analysis,
      "exit_b"
    );

  const exitC =
    getNode(
      analysis,
      "exit_c"
    );


  // ===================================================
  // RENDER
  // ===================================================

  return (
    <div className="venue-map-container">

      {/* =================================================
          HEADER
      ================================================= */}

      <div className="venue-map-header">

        <div>

          <div className="venue-title-row">

            <h2>
              Venue Map
            </h2>

            <span className="live-badge">

              <span className="live-dot" />

              LIVE

            </span>

          </div>

          <p>
            Real-time crowd movement
          </p>

        </div>


        {/* LEGEND */}

        <div className="map-legend">

          <span>
            <i className="legend-dot crowd" />
            Crowd
          </span>

          <span>
            <i className="legend-dot low" />
            Low
          </span>

          <span>
            <i className="legend-dot moderate" />
            Moderate
          </span>

          <span>
            <i className="legend-dot high" />
            High
          </span>

          <span>
            <i className="legend-dot critical" />
            Critical
          </span>

        </div>

      </div>


      {/* =================================================
          MAP
      ================================================= */}

      <div className="venue-map-wrapper">

        <svg
          className="venue-svg"
          viewBox="0 0 1150 620"
          preserveAspectRatio="xMidYMid meet"
        >

          {/* ============================================
              GRID
          ============================================ */}

          <defs>

            <pattern
              id="smallGrid"
              width="24"
              height="24"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 24 0 L 0 0 0 24"
                fill="none"
                stroke="#f1f5f9"
                strokeWidth="1"
              />
            </pattern>


            <filter
              id="crowdGlow"
              x="-100%"
              y="-100%"
              width="300%"
              height="300%"
            >

              <feGaussianBlur
                stdDeviation="1.8"
                result="blur"
              />

              <feMerge>

                <feMergeNode
                  in="blur"
                />

                <feMergeNode
                  in="SourceGraphic"
                />

              </feMerge>

            </filter>

          </defs>


          <rect
            width="1150"
            height="620"
            fill="url(#smallGrid)"
          />


          {/* ============================================
              MAIN HALL
          ============================================ */}

          <rect
            x="245"
            y="105"
            width="620"
            height="350"
            rx="24"
            fill="#f8fafc"
            stroke="#cbd5e1"
            strokeWidth="2"
          />

          <rect
            x="260"
            y="120"
            width="590"
            height="320"
            rx="18"
            fill="white"
            stroke="#e2e8f0"
            strokeWidth="1"
          />

          <text
            x="555"
            y="155"
            textAnchor="middle"
            fontSize="17"
            fontWeight="700"
            fill="#334155"
          >
            MAIN HALL
          </text>


          {/* ============================================
              FOOD COURT
          ============================================ */}

          <rect
            x="430"
            y="480"
            width="340"
            height="95"
            rx="18"
            fill="#f8fafc"
            stroke="#cbd5e1"
            strokeWidth="2"
          />

          <text
            x="600"
            y="525"
            textAnchor="middle"
            fontSize="15"
            fontWeight="700"
            fill="#475569"
          >
            FOOD COURT
          </text>


          {/* ============================================
              PATHS
              
              NO ARROWS
          ============================================ */}

          <line
            x1="75"
            y1="285"
            x2="245"
            y2="285"
            stroke="#d1d5db"
            strokeWidth="11"
            strokeLinecap="round"
          />

          <line
            x1="245"
            y1="285"
            x2="865"
            y2="285"
            stroke="#d1d5db"
            strokeWidth="11"
            strokeLinecap="round"
          />

          <line
            x1="865"
            y1="220"
            x2="1060"
            y2="115"
            stroke="#e2e8f0"
            strokeWidth="9"
            strokeLinecap="round"
          />

          <line
            x1="865"
            y1="285"
            x2="1080"
            y2="285"
            stroke="#e2e8f0"
            strokeWidth="9"
            strokeLinecap="round"
          />

          <line
            x1="600"
            y1="455"
            x2="600"
            y2="480"
            stroke="#e2e8f0"
            strokeWidth="9"
          />

          <line
            x1="770"
            y1="525"
            x2="1050"
            y2="500"
            stroke="#e2e8f0"
            strokeWidth="9"
            strokeLinecap="round"
          />


          {/* ============================================
              CROWD DOTS
          ============================================ */}

          <g
            className="crowd-layer"
          >

            {crowdDots.map(
              (dot) => (

                <circle
                  key={dot.id}
                  cx={dot.x}
                  cy={dot.y}
                  r="4.2"
                  fill={dot.color}
                  opacity="0.85"
                  filter="url(#crowdGlow)"
                  className="crowd-dot"
                />

              )
            )}

          </g>


          {/* ============================================
              VENUE NODES
          ============================================ */}

          <VenueNode
            x={75}
            y={285}
            label="Gate A"
            node={gateA}
          />

          <VenueNode
            x={600}
            y={285}
            label="Main Hall"
            node={mainHall}
          />

          <VenueNode
            x={600}
            y={525}
            label="Food Court"
            node={foodCourt}
          />

          <VenueNode
            x={1060}
            y={115}
            label="Exit A"
            node={exitA}
          />

          <VenueNode
            x={1080}
            y={285}
            label="Exit B"
            node={exitB}
          />

          <VenueNode
            x={1050}
            y={500}
            label="Exit C"
            node={exitC}
          />

        </svg>


        {/* =================================================
            BOTTOM INFORMATION
        ================================================= */}

        <div className="map-stats">

          <div>
            <span>
              Total Crowd
            </span>

            <strong>
              {total}
            </strong>
          </div>

          <div>
            <span>
              Moving
            </span>

            <strong>
              {moving}
            </strong>
          </div>

          <div>
            <span>
              Visible
            </span>

            <strong>
              {crowdDots.length}
            </strong>
          </div>

          <div>
            <span>
              Congestion
            </span>

            <strong>
              {congestion}
            </strong>
          </div>

        </div>

      </div>

    </div>
  );
}