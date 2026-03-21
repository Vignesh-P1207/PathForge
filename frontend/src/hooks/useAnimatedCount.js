import { useState, useEffect, useRef } from 'react';

export default function useAnimatedCount(target, duration = 900, suffix = '') {
  const [current, setCurrent] = useState(0);
  const startTimeRef = useRef(null);
  const rafRef = useRef(null);

  useEffect(() => {
    if (target === 0 || target === undefined || target === null) {
      setCurrent(0);
      return;
    }

    startTimeRef.current = null;

    const animate = (timestamp) => {
      if (!startTimeRef.current) startTimeRef.current = timestamp;
      const elapsed = timestamp - startTimeRef.current;
      const t = Math.min(elapsed / duration, 1);

      // ease-out-quart
      const eased = 1 - Math.pow(1 - t, 4);
      const value = Math.round(eased * target);

      setCurrent(value);

      if (t < 1) {
        rafRef.current = requestAnimationFrame(animate);
      }
    };

    rafRef.current = requestAnimationFrame(animate);

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [target, duration]);

  return `${current}${suffix}`;
}
