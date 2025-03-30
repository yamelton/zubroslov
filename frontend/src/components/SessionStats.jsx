import React from 'react';

export default function SessionStats({ stats }) {
  return (
    <div className="session-stats">
      <div className="stat correct-stat">
        ✅ {stats.correct}
      </div>
      <div className="stat incorrect-stat">
        ❌ {stats.incorrect}
      </div>
    </div>
  );
}
