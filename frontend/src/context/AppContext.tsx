import React, { createContext, useContext, useState, useCallback } from 'react';
import { ViewType, Project, BrdDocument, ToastData } from '../types';

const SEED_DOCUMENTS: Record<string, BrdDocument> = {
  proj1: {
    projectName: 'CRM Integration Framework',
    executiveSummary:
      'This document defines the requirements for integrating our main CRM platform with the SAP ERP sync engine to automate lead and contact updates in real-time.',
    objectives: [
      'Automate batch data synchronization every 24 hours.',
      'Implement automatic retry mechanism (up to 3 times) for network failures.',
      'Ensure secure OAuth2 authentication flow for all API connections.',
    ],
    functionalRequirements: [
      {
        id: 'REQ-CRM-1.1',
        title: 'Batch ERP Sync Engine',
        description:
          'Synchronize CRM contacts with SAP daily. The sync should use incremental logs to optimize payload sizes.',
        status: 'Validated',
      },
    ],
    mermaidFlowchart: `graph TD
      A[CRM Sync] -->|Data| B[SAP Gateway]
      B --> C[Success Log]`,
    userStories: [
      {
        actor: 'Sales Rep',
        goal: 'Have updated CRM details synced immediately to SAP',
        outcome: 'I can view customer transactions in real-time.',
      },
    ],
    suggestedImprovements: [
      { id: 'imp1', text: 'Specify encryption standard for SAP synchronization logs', applied: false },
      { id: 'imp2', text: 'Implement fallback email alerts for synchronization errors', applied: false },
    ],
  },
  proj2: {
    projectName: 'Mobile App Onboarding Flow',
    executiveSummary:
      'This BRD outlines functional guidelines for implementing dual-channel MFA within our high-density consumer lending interface, enforcing mandatory identity lockouts and strict audit logs adhering to GDPR and fintech compliance policies.',
    objectives: [
      'Deploy automated dual-channel OTP delivery (SMS primary + WhatsApp API failover) with zero credential lockouts.',
      'Implement robust rate limiting: max 3 failed OTPs results in a strict 5-minute lockout.',
      'Introduce full relational audit logging detailing timestamp, regional scope, and device signatures.',
    ],
    functionalRequirements: [
      {
        id: 'REQ-MFA-3.1',
        title: 'Dual-Channel Gateway Redundancy',
        description:
          'The identity engine MUST attempt WhatsApp delivery if standard SMS exceeds 4500ms transmission delay. Fallback latency checkers run asynchronously in the background.',
        status: 'Validated',
      },
    ],
    mermaidFlowchart: `graph TD
      A[SMS Req] --> B{Gateway Check}
      B -->|Timeout| C[WA Failover]`,
    userStories: [
      {
        actor: 'Retail Borrower',
        goal: 'Receive secondary OTP tokens securely on WhatsApp',
        outcome: 'Can authorize loan applications even in remote regions with cellular lag.',
      },
      {
        actor: 'Compliance Lead',
        goal: 'Mandate PostgreSQL audit trail for failing logs',
        outcome: 'Ensure full regional GDPR regulatory coverage during peak traffic.',
      },
      {
        actor: 'Fintech Operator',
        goal: 'Trigger 300-second lockout after 3 invalid OTP loops',
        outcome: 'Prevent high-volume automated brute-force credential stuffing.',
      },
    ],
    suggestedImprovements: [
      { id: 'imp1', text: 'Add rate-limit policy rule to OTP deliveries', applied: false },
      { id: 'imp2', text: 'Specify audit logging parameters for compliance', applied: false },
      { id: 'imp3', text: 'Formulate GDPR residency criteria for phone lists', applied: false },
    ],
  },
  proj3: {
    projectName: 'Subscription Billing Logic',
    executiveSummary:
      'This document details subscription billing tier logic, handling upgrade and downgrade events, pricing parameters, and automatic payment retry rules for a SaaS platform.',
    objectives: [
      'Define clear billing boundaries for tiered SaaS licenses.',
      'Implement prorated credits when switching mid-cycle.',
      'Support dunning schedules for failed card authorizations.',
    ],
    functionalRequirements: [
      {
        id: 'REQ-BIL-2.1',
        title: 'Proration Calculations',
        description:
          'Calculate and issue credits for remaining days in a billing tier when user initiates an upgrade or downgrade.',
        status: 'Draft',
      },
    ],
    mermaidFlowchart: `graph TD
      A[Bill Check] --> B[Tier Calculation]
      B --> C[Prorate Credit]`,
    userStories: [
      {
        actor: 'Subscriber',
        goal: 'Be charged correctly when upgrading mid-cycle',
        outcome: 'Do not pay full amount for overlapping days.',
      },
    ],
    suggestedImprovements: [
      { id: 'imp1', text: 'Add billing failure notifications via Webhooks', applied: false },
    ],
  },
  proj4: {
    projectName: 'AuthZ Protocol Specs',
    executiveSummary:
      'This document defines authorization specifications, enforcing fine-grained user group permissions and API scopes using OAuth2 JWT credentials across internal microservices.',
    objectives: [
      'Secure internal microservices with structured JWT tokens.',
      'Support role hierarchies: Admin, Manager, Analyst, Viewer.',
      'Incorporate security audit logs for critical authorization failures.',
    ],
    functionalRequirements: [
      {
        id: 'REQ-SEC-4.1',
        title: 'JWT Role Validation',
        description:
          'API gateways MUST unpack JWT user claims and validate scopes prior to proxying downstream microservice requests.',
        status: 'In Review',
      },
    ],
    mermaidFlowchart: `graph TD
      A[Req Scope] --> B[JWT Validate]
      B -->|Valid| C[Access Granted]`,
    userStories: [
      {
        actor: 'API Client',
        goal: 'Request scopes relevant to task only',
        outcome: 'Cannot access restricted user directories.',
      },
    ],
    suggestedImprovements: [
      { id: 'imp1', text: 'Implement token revocation lists', applied: false },
    ],
  },
};

const SEED_PROJECTS: Project[] = [
  { id: 'proj1', name: 'CRM Integration Framework', status: 'Approved', language: 'English', timeAgo: '2h ago', category: 'CRM Architecture', icon: 'groups' },
  { id: 'proj2', name: 'Mobile App Onboarding Flow', status: 'AI Generated', language: 'Spanish', timeAgo: '5h ago', category: 'Mobile UX Guidelines', icon: 'phone_iphone' },
  { id: 'proj3', name: 'Subscription Billing Logic', status: 'Draft', language: 'English', timeAgo: 'Yesterday', category: 'Payments Strategy', icon: 'payments' },
  { id: 'proj4', name: 'AuthZ Protocol Specs', status: 'In Review', language: 'German', timeAgo: '2 days ago', category: 'Security Compliance', icon: 'security' },
];

interface AppContextValue {
  currentView: ViewType;
  navigate: (view: ViewType) => void;
  userEmail: string;
  setUserEmail: (email: string) => void;
  isDark: boolean;
  toggleDarkMode: () => void;
  projects: Project[];
  selectedProjectId: string;
  selectProject: (id: string) => void;
  addProject: (
    meta: { name: string; status: Project['status']; language: string; category: string; icon: string },
    doc?: BrdDocument
  ) => string;
  documents: Record<string, BrdDocument>;
  updateDocument: (id: string, doc: BrdDocument) => void;
  toasts: ToastData[];
  addToast: (message: string, type: ToastData['type']) => void;
  removeToast: (id: string) => void;
}

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [currentView, setCurrentView] = useState<ViewType>('splash');
  const [userEmail, setUserEmail] = useState('');
  const [isDark, setIsDark] = useState<boolean>(() => {
    try { return localStorage.getItem('isDark') === 'true'; } catch { return false; }
  });
  const [projects, setProjects] = useState<Project[]>(SEED_PROJECTS);
  const [selectedProjectId, setSelectedProjectId] = useState('proj2');
  const [documents, setDocuments] = useState<Record<string, BrdDocument>>(SEED_DOCUMENTS);
  const [toasts, setToasts] = useState<ToastData[]>([]);
  React.useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark);
  }, [isDark]);

  const toggleDarkMode = useCallback(() => {
    setIsDark(prev => {
      const next = !prev;
      localStorage.setItem('isDark', String(next));
      return next;
    });
  }, []);

  const navigate = useCallback((view: ViewType) => setCurrentView(view), []);

  const selectProject = useCallback((id: string) => setSelectedProjectId(id), []);

  const addProject = useCallback(
    (
      meta: { name: string; status: Project['status']; language: string; category: string; icon: string },
      doc?: BrdDocument
    ) => {
      const id = `proj_${Date.now()}`;
      setProjects(prev => [
        { id, name: meta.name, status: meta.status, language: meta.language, timeAgo: 'Just now', category: meta.category, icon: meta.icon },
        ...prev,
      ]);
      setDocuments(prev => ({
        ...prev,
        [id]: doc ?? {
          projectName: meta.name,
          executiveSummary: `BRD Document draft for ${meta.name}.`,
          objectives: ['Define initial scope.', 'Formulate system integrations.'],
          functionalRequirements: [],
          mermaidFlowchart: 'graph TD\\n    A[Start] --> B[End]',
          userStories: [],
          suggestedImprovements: [],
        },
      }));
      setSelectedProjectId(id);
      return id;
    },
    []
  );

  const updateDocument = useCallback((id: string, doc: BrdDocument) => {
    setDocuments(prev => ({ ...prev, [id]: doc }));
  }, []);

  const addToast = useCallback((message: string, type: ToastData['type']) => {
    const id = Math.random().toString(36).slice(2);
    setToasts(prev => [...prev, { id, message, type }]);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <AppContext.Provider
      value={{
        currentView, navigate,
        userEmail, setUserEmail,
        isDark, toggleDarkMode,
        projects, selectedProjectId, selectProject, addProject,
        documents, updateDocument,
        toasts, addToast, removeToast,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}
