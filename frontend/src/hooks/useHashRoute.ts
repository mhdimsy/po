import { useEffect, useState } from 'react';

export function useHashRoute(defaultRoute = 'dashboard') {
  const [route, setRoute] = useState(readRoute(defaultRoute));

  useEffect(() => {
    const onHashChange = () => setRoute(readRoute(defaultRoute));
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, [defaultRoute]);

  const navigate = (nextRoute: string) => {
    window.location.hash = nextRoute;
  };

  return { route, navigate };
}

function readRoute(defaultRoute: string) {
  return window.location.hash.replace(/^#\/?/, '') || defaultRoute;
}
