import React from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { AppProvider, useApp } from './context/AppContext';
import ToastStack from './components/Toast';
import { ViewType } from './types';

import SplashView    from './views/SplashView';
import AuthView      from './views/AuthView';
import DashboardView from './views/DashboardView';
import WorkspaceView from './views/WorkspaceView';
import DocumentView  from './views/DocumentView';
import SettingsView  from './views/SettingsView';

function Router() {
  const { currentView, userEmail, navigate } = useApp();

  const PROTECTED: ViewType[] = ['dashboard', 'workspace', 'document', 'settings'];

  React.useEffect(() => {
    if (PROTECTED.includes(currentView) && !userEmail) {
      navigate('signin');
    }
  }, [currentView, userEmail]);

  const view = () => {
    switch (currentView) {
      case 'splash':    return <SplashView />;
      case 'signin':
      case 'signup':    return <AuthView />;
      case 'dashboard': return <DashboardView />;
      case 'workspace': return <WorkspaceView />;
      case 'document':  return <DocumentView />;
      case 'settings':  return <SettingsView />;
      default:          return <SplashView />;
    }
  };

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={currentView}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.18 }}
      >
        {view()}
      </motion.div>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <AppProvider>
      <ToastStack />
      <Router />
    </AppProvider>
  );
}
