// CrowdPilot AI — dashboard shell
// Person 2: build VenueMap, KpiCards, BeforeAfter here
// Person 3: build RecommendationPanel here

import contractMock from '../../docs/contract.json'

export default function App() {
  return (
    <div style={{ fontFamily: 'sans-serif', padding: 24 }}>
      <h1>CrowdPilot AI</h1>
      <p>Venue: {contractMock.venue}</p>
      {/* TODO: <Header /> <VenueMap /> <KpiCards /> <RecommendationPanel /> <BeforeAfter /> */}
    </div>
  )
}
