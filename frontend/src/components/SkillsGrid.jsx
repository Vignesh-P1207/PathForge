import { useEffect, useState } from 'react';

export default function SkillsGrid({ currentSkills = [], requiredSkills = [] }) {
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setAnimated(true), 300);
    return () => clearTimeout(timer);
  }, []);

  const renderSkill = (skill, i) => (
    <div className="skill-item" key={i}>
      <div className="skill-header">
        <span className="skill-name">{skill.name}</span>
        <span className="skill-pct">{skill.pct}%</span>
      </div>
      <div className="skill-track">
        <div
          className={`skill-fill ${skill.type}`}
          style={{ width: animated ? `${skill.pct}%` : '0%' }}
        />
      </div>
    </div>
  );

  return (
    <div className="skills-grid">
      <div className="skills-col">
        <div className="skills-heading">YOUR PROFILE</div>
        {currentSkills.map(renderSkill)}
      </div>
      <div className="skills-col">
        <div className="skills-heading">ROLE REQUIRES</div>
        {requiredSkills.map(renderSkill)}
      </div>
    </div>
  );
}
