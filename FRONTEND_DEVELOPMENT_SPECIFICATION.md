# Enviro-Governance Platform: Frontend Development Specification

## 1. Project Overview

Frontend application for the Enviro-Governance Platform - a React-based dashboard enabling municipalities and water authorities to access AI-driven remediation recommendations and participate in transparent multi-stakeholder governance voting.

**Tech Stack:**
- React 18+ (TypeScript)
- Vite (build tool)
- TailwindCSS (styling)
- React Query (state management)
- Recharts (data visualization)
- React Router v6 (navigation)
- Zustand (global state)
- API: FastAPI backend (REST)

## 2. Core Components & Features

### 2.1 Authentication & Authorization
```
/auth
├── LoginPage
│   ├── Email/password form
│   ├── Multi-factor authentication
│   └── Remember device
├── RegisterPage
├── ForgotPasswordPage
└── ProtectedRoute (HOC)
```

### 2.2 Remediation Module
```
/remediation
├── RemediationDashboard
│   ├── InputForm (pollution details)
│   ├── StrategyComparison (4 strategies side-by-side)
│   │   ├── Cost analysis
│   │   ├── Effectiveness timeline
│   │   └── Risk assessment
│   ├── RecommendedStrategy
│   └── SavePlanButton
├── HistoryList (past plans)
└── DetailView (single plan expansion)
```

### 2.3 Governance Voting Module
```
/governance
├── GovernanceDashboard
│   ├── ActivePolicies
│   ├── VotingInterface
│   │   ├── PolicyDescription
│   │   ├── VotingVectors
│   │   │   ├── Environmental Impact (slider -1 to +1)
│   │   │   ├── Cost Effectiveness
│   │   │   ├── Social Acceptance
│   │   │   ├── Implementation Feasibility
│   │   │   └── Long-term Sustainability
│   │   ├── WeightedVoting
│   │   ├── SubmitVote
│   │   └── AggregateResults (real-time)
│   └── RecommendationEngine
│       ├── AggregateScore (-1 to +1)
│       ├── ConsensusMetric (0-100%)
│       ├── Recommendation (APPROVE/REJECT/NEEDS_REVIEW)
│       └── AIExplanation
└── VotingHistory
```

### 2.4 Dashboard & Analytics
```
/dashboard
├── Overview
│   ├── Key Metrics
│   │   ├── Total decisions made
│   │   ├── Average consensus
│   │   ├── Implementation rate
│   │   └── Cost savings
│   ├── Charts
│   │   ├── Consensus trend (line chart)
│   │   ├── Remediation effectiveness (bar chart)
│   │   ├── Policy outcomes (pie chart)
│   │   └── Timeline analysis
│   └── RecentActivity
├── AuditLog
│   ├── All voting records
│   ├── Filter by date/type
│   └── Export functionality
└── Reports
```

### 2.5 Organization Management
```
/settings/organization
├── Profile
│   ├── Organization details
│   ├── Logo upload
│   └── Description
├── Members
│   ├── User list
│   ├── Add/remove members
│   ├── Role assignment
│   └── Invitation management
├── Subscriptions
│   ├── Current plan
│   ├── Usage metrics
│   └── Upgrade/downgrade
└── APIKeys
    └── Generate/revoke tokens
```

## 3. Page Hierarchy & Routes

```
App
├── / (Landing/Dashboard)
├── /auth
│   ├── /login
│   ├── /register
│   └── /forgot-password
├── /remediation
│   ├── / (Dashboard)
│   ├── /new (Create plan)
│   ├── /history
│   └── /:id (Detail view)
├── /governance
│   ├── / (Dashboard)
│   ├── /vote/:policyId
│   ├── /history
│   └── /results/:policyId
├── /dashboard
│   ├── / (Overview)
│   ├── /analytics
│   ├── /audit-log
│   └── /reports
└── /settings
    ├── /profile
    ├── /organization
    ├── /members
    ├── /subscription
    └── /api-keys
```

## 4. UI/UX Specifications

### 4.1 Design System
- **Color Palette:**
  - Primary: #10B981 (emerald, environmental)
  - Secondary: #3B82F6 (blue, governance)
  - Danger: #EF4444 (red, warnings)
  - Neutral: #64748B (slate, text)

- **Typography:**
  - Heading 1: 32px, 700 weight (inter)
  - Heading 2: 24px, 600 weight
  - Body: 14px, 400 weight
  - Small: 12px, 400 weight

- **Spacing:** 4px, 8px, 12px, 16px, 24px, 32px (4px base unit)

### 4.2 Component Library (TailwindCSS + Custom)
- Button (primary, secondary, danger, ghost)
- Input (text, email, password, number)
- Slider (voting vector)
- Modal/Dialog
- Card
- Table
- Badge
- Toast notifications
- Loading spinner
- Empty state

## 5. Data Flow & State Management

### 5.1 State Structure (Zustand)
```typescript
store.ts
├── auth (user, token, permissions)
├── remediation (plans, currentPlan, loading)
├── governance (policies, votes, consensus)
├── ui (theme, sidebar collapsed, modal state)
└── notifications (toasts, alerts)
```

### 5.2 API Integration (React Query)
```typescript
hooks/
├── useRemediationPlans()
├── useCreateRemediationPlan()
├── useGovernanceVotes()
├── useSubmitVote()
├── useAggregateResults()
├── usePolicies()
└── useOrganization()
```

## 6. Feature Specifications

### 6.1 Remediation Plan Input Form
**Inputs:**
- Pollution description (textarea, min 50 chars)
- Site type (select: wastewater_treatment_plant, contaminated_land, etc.)
- Location (text input, geolocation optional)
- Budget tier (radio: low, medium, high)
- Timeline preference (optional)

**Outputs:**
- 4 strategy recommendations
- Effectiveness score (0-100%)
- Estimated cost
- Timeline (days)
- Risk assessment
- Implementation steps (expandable)

### 6.2 Governance Voting Interface
**Vote Submission:**
1. Display policy description
2. Show 5-6 voting vectors
3. Each vector: slider (-1 to +1) with label
4. Real-time consensus meter
5. AI-generated explanation
6. Submit button

**Real-time Results:**
- Aggregate score display
- Consensus percentage
- Vector breakdown (radar chart)
- Recommendation box
- Voter statistics

### 6.3 Analytics Dashboard
**Metrics:**
- Total governance decisions (counter)
- Average consensus score (gauge chart)
- Policy approval rate (%)
- Decision time reduction (trend)
- Cost savings (currency)

**Charts:**
- Consensus trend (7-day/30-day/90-day)
- Remediation effectiveness by type
- Policy outcomes (approved/rejected/review)
- User participation rate

## 7. Mobile Responsiveness

**Breakpoints:**
- Mobile: 320px - 640px
- Tablet: 641px - 1024px
- Desktop: 1025px+

**Mobile Adaptations:**
- Single-column layout
- Full-width forms
- Bottom sheet for actions
- Simplified charts (single metric)
- Touch-friendly buttons (48px minimum)

## 8. Performance Requirements

- First Contentful Paint: < 1.5s
- Largest Contentful Paint: < 2.5s
- Time to Interactive: < 3.5s
- Bundle size: < 250KB (gzipped)
- API response time: < 200ms
- Lighthouse score: > 90

## 9. Accessibility (WCAG 2.1 AA)

- Semantic HTML
- ARIA labels on interactive elements
- Keyboard navigation support
- Color contrast ratio > 4.5:1
- Focus visible indicators
- Alt text on images
- Form field labels
- Error messages linked to inputs

## 10. Development Workflow

```
frontend/
├── src/
│   ├── components/
│   │   ├── remediation/
│   │   ├── governance/
│   │   ├── dashboard/
│   │   ├── auth/
│   │   ├── common/
│   │   └── layout/
│   ├── hooks/
│   │   ├── useRemediationPlans.ts
│   │   ├── useGovernanceVotes.ts
│   │   └── useAPI.ts
│   ├── services/
│   │   └── api.ts
│   ├── store/
│   │   └── store.ts (Zustand)
│   ├── types/
│   │   └── index.ts
│   ├── pages/
│   ├── App.tsx
│   └── main.tsx
├── public/
├── tests/
├── .env.example
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

## 11. Testing Strategy

- **Unit Tests:** Jest + React Testing Library (components)
- **Integration Tests:** React Testing Library (user flows)
- **E2E Tests:** Cypress/Playwright (critical paths)
- **Coverage Target:** > 80%

## 12. Deployment & CI/CD

**Build Process:**
```bash
npm run build     # Vite build
npm run preview   # Preview build
npm run test      # Run tests
npm run lint      # ESLint + Prettier
```

**Deployment:**
- Vercel (recommended for React SPA)
- Environment variables: API_URL, AUTH_DOMAIN
- Automatic deployments on push to main

## 13. Security Considerations

- HTTPS only
- Environment variables for sensitive data
- CSRF protection (same-site cookies)
- XSS prevention (React auto-escaping)
- JWT token storage (secure httpOnly cookies)
- Input sanitization
- API rate limiting

## 14. Timeline & Milestones

**Phase 1 (Weeks 1-2):** Project setup, component library, auth flow
**Phase 2 (Weeks 3-4):** Remediation module, form validation
**Phase 3 (Weeks 5-6):** Governance voting interface, real-time results
**Phase 4 (Weeks 7-8):** Dashboard, analytics, charts
**Phase 5 (Weeks 9-10):** Settings, organization management
**Phase 6 (Weeks 11-12):** Testing, optimization, polish
**Phase 7 (Weeks 13-14):** Deployment, monitoring, documentation

---

**Total Development Time:** 14 weeks (1 FTE)
**Estimated Team Size:** 1-2 developers + 1 designer
**Version:** 1.0.0
**Last Updated:** December 28, 2025
