export type ViewType =
  | 'splash'
  | 'dashboard'
  | 'signin'
  | 'signup'
  | 'workspace'
  | 'document'
  | 'settings';

export interface Project {
  id: string;
  name: string;
  status: 'Approved' | 'AI Generated' | 'Draft' | 'In Review';
  language: string;
  timeAgo: string;
  category: string;
  icon: string;
}

export interface Activity {
  id: string;
  type: 'refinement' | 'share' | 'completed' | 'comment';
  message: string;
  time: string;
}

export interface FunctionalRequirement {
  id: string;
  title: string;
  description: string;
  status: 'Validated' | 'Draft' | 'In Review';
}

export interface UserStory {
  actor: string;
  goal: string;
  outcome: string;
}

export interface BrdDocument {
  projectName: string;
  executiveSummary: string;
  objectives: string[];
  functionalRequirements: FunctionalRequirement[];
  flowchartSvg: string;
  userStories: UserStory[];
  suggestedImprovements: {
    id: string;
    text: string;
    applied: boolean;
  }[];
}

export interface ToastData {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
}
