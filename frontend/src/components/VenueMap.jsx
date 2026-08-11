function utilizationToColor(value) {
  if (value < 0.6) {
    return "#22c55e"; // green
  }

  if (value < 0.8) {
    return "#eab308"; // yellow
  }

  if (value < 0.9) {
    return "#f97316"; // orange
  }

  return "#ef4444"; // red
}


function getNode(analysis, id) {
  return analysis?.nodes?.find(
    (node) => node.id === id
  );
}


function Node({
  x,
  y,
  label,
  node,
  radius = 24,
}) {
  const utilization = node?.utilization ?? 0;

  const color = utilizationToColor(
    utilization
  );

  return (
    <g>
      {/* Node circle */}
      <circle
        cx={x}
        cy={y}
        r={radius}
        fill={color}
        stroke="#17202a"
        strokeWidth="2"
      />

      {/* Utilization */}
      <text
        x={x}
        y={y + 5}
        textAnchor="middle"
        fontSize="12"
        fontWeight="bold"
        fill="white"
      >
        {Math.round(utilization * 100)}%
      </text>

      {/* Label */}
      <text
        x={x}
        y={y + radius + 18}
        textAnchor="middle"
        fontSize="13"
        fontWeight="600"
        fill="#17202a"
      >
        {label}
      </text>
    </g>
  );
}


function createAgentPositions(count) {
  const positions = [];

  const areas = [
    { x: 300, y: 210 },
    { x: 340, y: 280 },
    { x: 390, y: 220 },
    { x: 430, y: 290 },
    { x: 500, y: 210 },
    { x: 550, y: 280 },
    { x: 590, y: 230 },
    { x: 620, y: 290 },
    { x: 400, y: 420 },
    { x: 470, y: 420 },
    { x: 520, y: 450 },
  ];

  for (let i = 0; i < count; i++) {
    const area = areas[i % areas.length];

    const offsetX = ((i * 17) % 30) - 15;
    const offsetY = ((i * 23) % 30) - 15;

    positions.push({
      x: area.x + offsetX,
      y: area.y + offsetY,
    });
  }

  return positions;
}


export default function VenueMap({ analysis }) {

  // ==========================================
  // GET VENUE NODES
  // ==========================================

  const gateA = getNode(
    analysis,
    "gate_a"
  );

  const mainHall = getNode(
    analysis,
    "main_hall"
  );

  const foodCourt = getNode(
    analysis,
    "food_court"
  );

  const exitA = getNode(
    analysis,
    "exit_a"
  );

  const exitB = getNode(
    analysis,
    "exit_b"
  );

  const exitC = getNode(
    analysis,
    "exit_c"
  );


  // ==========================================
  // LIVE CROWD → AGENT DOTS
  // ==========================================

  const movingCrowd =
    analysis?.crowd?.moving ?? 0;

  // Each dot represents approximately
  // 10 moving people.

  const agentCount = Math.min(
    60,
    Math.ceil(movingCrowd / 10)
  );

  const agentPositions =
    createAgentPositions(agentCount);


  // ==========================================
  // MAP
  // ==========================================

  return (
    <div className="venue-map-container">

      {/* ====================================
          MAP HEADER
      ===================================== */}

      <div className="map-header">

        <div>
          <h2>Venue Map</h2>

          <p>
            Live crowd utilization
          </p>
        </div>


        {/* Legend */}

        <div className="map-legend">

          <span>
            <i className="legend-dot low"></i>
            Low
          </span>

          <span>
            <i className="legend-dot moderate"></i>
            Moderate
          </span>

          <span>
            <i className="legend-dot high"></i>
            High
          </span>

          <span>
            <i className="legend-dot critical"></i>
            Critical
          </span>

        </div>

      </div>


      {/* ====================================
          SVG VENUE MAP
      ===================================== */}

      <svg
        className="venue-svg"
        viewBox="0 0 900 560"
        role="img"
        aria-label="CrowdPilot venue map"
      >

        {/* ==================================
            VENUE STRUCTURE
        =================================== */}

        {/* Main Hall */}

        <rect
          x="220"
          y="120"
          width="460"
          height="250"
          rx="20"
          fill="#f8fafc"
          stroke="#94a3b8"
          strokeWidth="3"
        />

        <text
          x="450"
          y="155"
          textAnchor="middle"
          fontSize="18"
          fontWeight="bold"
          fill="#475569"
        >
          MAIN HALL
        </text>


        {/* Food Court */}

        <rect
          x="330"
          y="390"
          width="240"
          height="90"
          rx="15"
          fill="#f8fafc"
          stroke="#94a3b8"
          strokeWidth="3"
        />

        <text
          x="450"
          y="440"
          textAnchor="middle"
          fontSize="16"
          fontWeight="bold"
          fill="#475569"
        >
          FOOD COURT
        </text>


        {/* ==================================
            CORRIDORS / PATHS
        =================================== */}

        {/* Gate A → Main Hall */}

        <line
          x1="110"
          y1="250"
          x2="220"
          y2="250"
          stroke="#64748b"
          strokeWidth="14"
          strokeLinecap="round"
        />


        {/* Main Hall corridor */}

        <line
          x1="300"
          y1="250"
          x2="600"
          y2="250"
          stroke="#64748b"
          strokeWidth="14"
          strokeLinecap="round"
        />


        {/* Main Hall → Food Court */}

        <line
          x1="450"
          y1="370"
          x2="450"
          y2="390"
          stroke="#64748b"
          strokeWidth="14"
        />


        {/* Main Hall → Exit A */}

        <line
          x1="680"
          y1="180"
          x2="790"
          y2="100"
          stroke="#64748b"
          strokeWidth="14"
          strokeLinecap="round"
        />


        {/* Main Hall → Exit B */}

        <line
          x1="680"
          y1="250"
          x2="810"
          y2="250"
          stroke="#64748b"
          strokeWidth="14"
          strokeLinecap="round"
        />


        {/* Food Court → Exit C */}

        <line
          x1="570"
          y1="435"
          x2="790"
          y2="470"
          stroke="#64748b"
          strokeWidth="14"
          strokeLinecap="round"
        />


        {/* ==================================
            VENUE NODES
        =================================== */}

        <Node
          x={110}
          y={250}
          label="Gate A"
          node={gateA}
        />


        <Node
          x={450}
          y={250}
          label="Main Hall"
          node={mainHall}
        />


        <Node
          x={450}
          y={435}
          label="Food Court"
          node={foodCourt}
        />


        <Node
          x={790}
          y={100}
          label="Exit A"
          node={exitA}
        />


        <Node
          x={810}
          y={250}
          label="Exit B"
          node={exitB}
        />


        <Node
          x={790}
          y={470}
          label="Exit C"
          node={exitC}
        />


        {/* ==================================
            LIVE CROWD DOTS
        =================================== */}

        <g className="agent-dots">

          {agentPositions.map(
            (position, index) => (
              <circle
                key={index}
                cx={position.x}
                cy={position.y}
                r="4"
              />
            )
          )}

        </g>

      </svg>

    </div>
  );
}