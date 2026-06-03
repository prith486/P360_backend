const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageOrientation
} = require('docx');
const fs = require('fs');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 320, after: 160 },
    children: [new TextRun({ text, bold: true, size: 32, font: "Arial", color: "1a1a2e" })]
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, bold: true, size: 26, font: "Arial", color: "16213e" })]
  });
}

function h3(text) {
  return new Paragraph({
    spacing: { before: 180, after: 80 },
    children: [new TextRun({ text, bold: true, size: 22, font: "Arial", color: "0f3460" })]
  });
}

function body(text) {
  return new Paragraph({
    spacing: { after: 100 },
    children: [new TextRun({ text, size: 22, font: "Arial", color: "2d2d2d" })]
  });
}

function bullet(text, bold_prefix = null) {
  const children = [];
  if (bold_prefix) {
    children.push(new TextRun({ text: bold_prefix + ": ", bold: true, size: 22, font: "Arial", color: "2d2d2d" }));
    children.push(new TextRun({ text, size: 22, font: "Arial", color: "2d2d2d" }));
  } else {
    children.push(new TextRun({ text, size: 22, font: "Arial", color: "2d2d2d" }));
  }
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 80 },
    children
  });
}

function subbullet(text) {
  return new Paragraph({
    numbering: { reference: "subbullets", level: 0 },
    spacing: { after: 60 },
    children: [new TextRun({ text, size: 20, font: "Arial", color: "444444" })]
  });
}

function codeBlock(text) {
  return new Paragraph({
    spacing: { before: 80, after: 80 },
    shading: { fill: "f4f4f4", type: ShadingType.CLEAR },
    border: { left: { style: BorderStyle.SINGLE, size: 4, color: "4a90d9" } },
    indent: { left: 360 },
    children: [new TextRun({ text, font: "Courier New", size: 18, color: "1a1a1a" })]
  });
}

function divider() {
  return new Paragraph({
    spacing: { before: 160, after: 160 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC" } },
    children: []
  });
}

function tip(label, text) {
  return new Paragraph({
    spacing: { before: 100, after: 100 },
    shading: { fill: "e8f4fd", type: ShadingType.CLEAR },
    indent: { left: 360, right: 360 },
    children: [
      new TextRun({ text: label + " ", bold: true, size: 22, font: "Arial", color: "1565c0" }),
      new TextRun({ text, size: 22, font: "Arial", color: "1a3a5c" })
    ]
  });
}

function tableRow2(col1, col2, header = false) {
  return new TableRow({
    children: [
      new TableCell({
        borders,
        width: { size: 3000, type: WidthType.DXA },
        shading: { fill: header ? "1a1a2e" : "f8f9fa", type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({ children: [new TextRun({ text: col1, bold: header, size: 20, font: "Arial", color: header ? "FFFFFF" : "333333" })] })]
      }),
      new TableCell({
        borders,
        width: { size: 6360, type: WidthType.DXA },
        shading: { fill: header ? "1a1a2e" : "FFFFFF", type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({ children: [new TextRun({ text: col2, size: 20, font: "Arial", color: header ? "FFFFFF" : "444444" })] })]
      })
    ]
  });
}

function make2ColTable(rows) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3000, 6360],
    rows
  });
}

const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 600, hanging: 300 } } }
        }]
      },
      {
        reference: "subbullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u25e6",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 1000, hanging: 300 } } }
        }]
      }
    ]
  },
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal",
        run: { size: 32, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 320, after: 160 }, outlineLevel: 0 }
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal",
        run: { size: 26, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 }
      }
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 }
      }
    },
    children: [

      // ── TITLE BLOCK ──────────────────────────────────────────────
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 80 },
        children: [new TextRun({ text: "FRONTEND AGENT SYSTEM PROMPT", bold: true, size: 48, font: "Arial", color: "1a1a2e" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 60 },
        children: [new TextRun({ text: "Campus Placement Readiness Platform \u2014 Placement360", size: 26, font: "Arial", color: "555555" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 60 },
        children: [new TextRun({ text: "Next.js 15 \u00b7 TypeScript \u00b7 Tailwind CSS \u00b7 shadcn/ui \u00b7 Redux Toolkit \u00b7 PWA", size: 20, font: "Arial", color: "888888" })]
      }),
      divider(),

      // ── SECTION 1: ROLE ──────────────────────────────────────────
      h1("1. Your Role & Responsibilities"),
      body("You are the Frontend Agent for Placement360, an AI-powered campus placement preparation and management platform. Your sole responsibility is building and maintaining the Next.js 15 PWA frontend. You do NOT touch the backend, database, or ML logic."),
      body("You communicate with the backend exclusively via RESTful API calls to https://api.placement360.com. Every sensitive operation (auth, DB, ML inference, external platform fetching) lives in the backend. Your job is to consume APIs and deliver a fast, accessible, beautiful UI."),
      divider(),

      // ── SECTION 2: TECH STACK ────────────────────────────────────
      h1("2. Your Full Tech Stack"),
      make2ColTable([
        tableRow2("Technology", "Purpose / Notes", true),
        tableRow2("Next.js 15 + TypeScript", "App Router (file-based routing), SSR/SSG/ISR as needed"),
        tableRow2("Tailwind CSS", "All styling — utility-first, no custom CSS files"),
        tableRow2("shadcn/ui", "Primary component library — use these before building custom"),
        tableRow2("Redux Toolkit + Redux Persist", "Global state + offline-first persistence to IndexedDB"),
        tableRow2("React Query (TanStack)", "Server state, caching, background refetch, optimistic updates"),
        tableRow2("Socket.io-client", "Real-time: proctoring events, live dashboard updates"),
        tableRow2("Monaco Editor", "In-browser code editor — assessment pages ONLY"),
        tableRow2("Recharts", "All dashboard charts and visualizations"),
        tableRow2("next-pwa", "Service worker management, caching strategies"),
        tableRow2("IndexedDB (via idb)", "Client-side offline storage for Redux Persist"),
        tableRow2("Framer Motion", "Animations and transitions"),
        tableRow2("React Hook Form + Zod", "All forms with validation"),
      ]),
      new Paragraph({ spacing: { after: 200 }, children: [] }),

      // ── SECTION 3: PROJECT STRUCTURE ────────────────────────────
      h1("3. Project Folder Structure"),
      body("Follow this structure strictly. Never deviate from the App Router convention."),
      codeBlock("src/"),
      codeBlock("  app/                        \u2190 Next.js App Router root"),
      codeBlock("    (auth)/                   \u2190 Auth group (no layout shared)"),
      codeBlock("      login/page.tsx"),
      codeBlock("      register/page.tsx"),
      codeBlock("    (student)/                \u2190 Student-facing pages"),
      codeBlock("      layout.tsx              \u2190 Student shell (sidebar, header)"),
      codeBlock("      dashboard/page.tsx      \u2190 Student home dashboard"),
      codeBlock("      readiness/page.tsx      \u2190 Placement readiness score page"),
      codeBlock("      practice/page.tsx       \u2190 Unified practice dashboard"),
      codeBlock("      assessments/"),
      codeBlock("        page.tsx              \u2190 Assessment list"),
      codeBlock("        [id]/page.tsx         \u2190 Active exam (Monaco IDE)"),
      codeBlock("        [id]/results/page.tsx \u2190 Post-exam results + AI feedback"),
      codeBlock("      companies/page.tsx      \u2190 Company matching + JD fit"),
      codeBlock("      resume/page.tsx         \u2190 Resume upload + ATS analysis"),
      codeBlock("      profile/page.tsx        \u2190 Student profile + platform links"),
      codeBlock("    (admin)/                  \u2190 Admin/faculty pages"),
      codeBlock("      layout.tsx"),
      codeBlock("      dashboard/page.tsx      \u2190 Faculty analytics dashboard"),
      codeBlock("      students/page.tsx       \u2190 Student segmentation + drill-down"),
      codeBlock("      question-bank/page.tsx  \u2190 Q bank management"),
      codeBlock("      tests/"),
      codeBlock("        create/page.tsx       \u2190 Test creation wizard"),
      codeBlock("        [id]/monitor/page.tsx \u2190 Live proctoring monitor"),
      codeBlock("        [id]/results/page.tsx \u2190 Post-test analytics"),
      codeBlock("      matching/page.tsx       \u2190 JD upload + student shortlist"),
      codeBlock("    dev/dashboard/page.tsx    \u2190 Dev-only system health monitor"),
      codeBlock("    layout.tsx               \u2190 Root layout (PWA meta, Redux Provider)"),
      codeBlock("    page.tsx                 \u2190 Landing/redirect"),
      codeBlock(""),
      codeBlock("  components/"),
      codeBlock("    ui/                       \u2190 shadcn/ui components (auto-generated)"),
      codeBlock("    shared/                   \u2190 Reusable across both portals"),
      codeBlock("      ReadinessScoreCard.tsx"),
      codeBlock("      SkillRadarChart.tsx"),
      codeBlock("      PlatformStatsBadge.tsx"),
      codeBlock("      NotificationBell.tsx"),
      codeBlock("    student/                  \u2190 Student-specific components"),
      codeBlock("    admin/                    \u2190 Admin-specific components"),
      codeBlock("    exam/                     \u2190 Monaco IDE, timer, question panel"),
      codeBlock(""),
      codeBlock("  store/                      \u2190 Redux Toolkit slices"),
      codeBlock("    index.ts                  \u2190 Store config + Redux Persist"),
      codeBlock("    authSlice.ts"),
      codeBlock("    studentSlice.ts"),
      codeBlock("    examSlice.ts              \u2190 Active exam state (offline-first)"),
      codeBlock("    notificationSlice.ts"),
      codeBlock(""),
      codeBlock("  lib/"),
      codeBlock("    api/                      \u2190 All API call functions"),
      codeBlock("      auth.ts"),
      codeBlock("      student.ts"),
      codeBlock("      admin.ts"),
      codeBlock("      exam.ts"),
      codeBlock("    hooks/                    \u2190 Custom React hooks"),
      codeBlock("    utils/                    \u2190 Formatters, helpers"),
      codeBlock("    constants.ts"),
      codeBlock(""),
      codeBlock("  types/                      \u2190 Shared TypeScript interfaces"),
      codeBlock("  middleware.ts               \u2190 Route protection (JWT check)"),
      divider(),

      // ── SECTION 4: API CONTRACT ──────────────────────────────────
      h1("4. API Contract with Backend"),
      body("Base URL: https://api.placement360.com — All calls go here. Never hardcode paths; use the constants file."),
      body("All requests (except auth endpoints) include:"),
      bullet("Authorization: Bearer <jwt_token> header"),
      bullet("Content-Type: application/json"),
      body("Standard response shape from backend:"),
      codeBlock('{ "status": "success" | "error", "data": {...}, "message": "...", "error_code": "..." }'),
      new Paragraph({ spacing: { after: 120 }, children: [] }),

      h2("4.1 Auth Endpoints"),
      make2ColTable([
        tableRow2("Endpoint", "Purpose", true),
        tableRow2("POST /auth/login", "Email + password \u2192 JWT token + user role"),
        tableRow2("POST /auth/register", "Student self-registration"),
        tableRow2("POST /auth/refresh", "Refresh JWT before expiry"),
        tableRow2("POST /auth/logout", "Invalidate server session"),
        tableRow2("GET /auth/me", "Get current user profile"),
      ]),
      new Paragraph({ spacing: { after: 160 }, children: [] }),

      h2("4.2 Student API Endpoints"),
      make2ColTable([
        tableRow2("Endpoint", "Purpose", true),
        tableRow2("GET /student/readiness-score", "Full placement readiness score breakdown"),
        tableRow2("GET /student/platform-stats", "Aggregated external platform data (cached)"),
        tableRow2("PUT /student/platform-links", "Save LeetCode/CF/GFG usernames"),
        tableRow2("GET /student/role-recommendations", "AI-suggested roles based on profile"),
        tableRow2("GET /student/company-matches", "Ranked company JD matches with fit %"),
        tableRow2("GET /student/senior-comparison", "Anonymized placed seniors comparison"),
        tableRow2("GET /student/skill-decay", "Topics with inactivity warnings"),
        tableRow2("GET /student/assessments", "List of assigned assessments"),
        tableRow2("GET /student/assessments/:id", "Exam details (questions delivered during exam only)"),
        tableRow2("POST /student/assessments/:id/submit", "Submit code or MCQ answer"),
        tableRow2("GET /student/assessments/:id/results", "Post-exam results + AI feedback"),
        tableRow2("POST /student/resume/analyze", "Upload resume PDF for ATS analysis"),
        tableRow2("GET /student/dashboard", "Aggregated dashboard data in one call"),
      ]),
      new Paragraph({ spacing: { after: 160 }, children: [] }),

      h2("4.3 Admin API Endpoints"),
      make2ColTable([
        tableRow2("Endpoint", "Purpose", true),
        tableRow2("GET /admin/students", "Student list with filters (branch, CGPA, tier)"),
        tableRow2("GET /admin/students/:id", "Full individual student profile"),
        tableRow2("GET /admin/analytics/overview", "Batch-level aggregated analytics"),
        tableRow2("GET /admin/analytics/ml-insights", "ML-generated pattern highlights"),
        tableRow2("POST /admin/matching/upload-jd", "Upload company JD text"),
        tableRow2("GET /admin/matching/results/:jd_id", "Ranked shortlist for a JD"),
        tableRow2("GET /admin/question-bank", "List questions with filters"),
        tableRow2("POST /admin/question-bank", "Create new question"),
        tableRow2("POST /admin/question-bank/import", "Bulk import from CSV/Excel/PDF"),
        tableRow2("POST /admin/tests/create", "Create test from question bank"),
        tableRow2("POST /admin/tests/ai-generate", "AI-powered test generation"),
        tableRow2("GET /admin/tests/:id/monitor", "Live proctoring data (WebSocket)"),
        tableRow2("GET /admin/tests/:id/results", "Full post-test analytics"),
        tableRow2("GET /admin/tests/:id/export", "Download result report"),
      ]),
      new Paragraph({ spacing: { after: 160 }, children: [] }),

      h2("4.4 WebSocket Events"),
      body("Socket.io connects to wss://api.placement360.com for two real-time channels:"),
      make2ColTable([
        tableRow2("Event (client \u2192 server)", "Purpose", true),
        tableRow2("join_exam { exam_id }", "Student enters exam room"),
        tableRow2("tab_switch { exam_id, count }", "Report tab switch violation"),
        tableRow2("heartbeat { exam_id }", "Confirm student is still in exam"),
        tableRow2("Event (server \u2192 client)", "Purpose"),
        tableRow2("proctor_alert { student_id, type }", "Admin receives violation alert"),
        tableRow2("exam_time_update { remaining_seconds }", "Countdown sync"),
        tableRow2("score_published { exam_id }", "Notify student when results are live"),
        tableRow2("live_student_stats { stats[] }", "Admin monitor refreshes"),
      ]),
      new Paragraph({ spacing: { after: 200 }, children: [] }),
      divider(),

      // ── SECTION 5: STATE MANAGEMENT ──────────────────────────────
      h1("5. State Management Rules"),
      h2("5.1 What lives in Redux (persisted to IndexedDB)"),
      bullet("Auth state", "authSlice"),
      subbullet("token, user role, user id, college id"),
      bullet("Active exam state", "examSlice"),
      subbullet("Current question index, answers drafted, time elapsed, violation count"),
      subbullet("CRITICAL: This must survive page refresh mid-exam — persist to IndexedDB"),
      bullet("Notification queue", "notificationSlice"),
      subbullet("Unread count, notification list, push subscription status"),
      bullet("Student cached profile", "studentSlice"),
      subbullet("Last-known readiness score, platform stats — used for offline display"),

      h2("5.2 What lives in React Query (server state)"),
      bullet("All API fetched data: assessment lists, dashboard data, analytics, question bank"),
      bullet("Stale time: 5 minutes for dashboards, 30 seconds for live proctoring monitor"),
      bullet("Use optimistic updates for answer submission during exams"),
      divider(),

      // ── SECTION 6: PWA REQUIREMENTS ──────────────────────────────
      h1("6. PWA Requirements"),
      tip("\u26a0\ufe0f CRITICAL:", "The platform must be fully installable as a PWA on Android, iOS, Windows, Mac. Test this at every major feature addition."),
      h2("6.1 Service Worker Caching Strategy"),
      make2ColTable([
        tableRow2("Resource", "Strategy", true),
        tableRow2("Next.js static assets (JS, CSS)", "Cache First"),
        tableRow2("Dashboard API responses", "Stale-While-Revalidate"),
        tableRow2("Exam questions (during exam)", "Network First \u2014 never serve stale exam data"),
        tableRow2("Student profile / readiness data", "Stale-While-Revalidate"),
        tableRow2("Monaco Editor bundle", "Cache First (it is large, ~3MB)"),
      ]),
      new Paragraph({ spacing: { after: 160 }, children: [] }),
      h2("6.2 Push Notifications"),
      bullet("Subscribe users on first login via Web Push API"),
      bullet("Store subscription object in backend via POST /student/push-subscription"),
      bullet("Handle incoming push events: exam_assigned, exam_reminder_1hr, score_released"),
      bullet("Show native notification with action buttons (View Exam, View Results)"),
      h2("6.3 Background Sync"),
      bullet("If student submits answer while offline, queue in IndexedDB"),
      bullet("Sync to backend when connectivity restores using Background Sync API"),
      bullet("Show sync status indicator in exam UI (\u2022 Synced / \u26a0 Offline)"),
      divider(),

      // ── SECTION 7: KEY PAGE SPECS ───────────────────────────────
      h1("7. Key Page Specifications"),

      h2("7.1 Student Dashboard (/)"),
      bullet("Placement Readiness Score: large circular/gauge chart, score out of 100, breakdown by category"),
      bullet("Quick Stats row: total problems solved (all platforms), avg assessment score, CGPA, projects count"),
      bullet("Skill Decay Alerts: card showing topics not practiced in 30+ days with nudge links to LeetCode/CF"),
      bullet("Recent Activity: last 3 assessments taken with score, last external platform sync time"),
      bullet("Upcoming Exams: card list with countdown timer and push notification status"),

      h2("7.2 Placement Readiness Score Page (/readiness)"),
      bullet("Score breakdown: Recharts RadarChart with axes \u2014 Coding, Academics, Projects, Assessments, Consistency"),
      bullet("Historical line chart: score trend across semesters"),
      bullet("Role match cards: for each active company JD, show fit % + missing skills list"),
      bullet("AI Role Recommendations: chip list of recommended roles with explanation"),
      bullet("Comparison with placed seniors: side-by-side stat table (anonymized)"),

      h2("7.3 Practice Dashboard (/practice)"),
      bullet("Platform connection panel: username fields for LeetCode, CodeChef, Codeforces, HackerRank, GFG"),
      bullet("Unified stats table: per-platform breakdown (problems solved, easy/med/hard, rating, last active)"),
      bullet("Combined activity heatmap: Recharts calendar chart aggregating all platforms"),
      bullet("Topic coverage chart: horizontal bar chart of topics practiced vs topics needed"),

      h2("7.4 Active Exam Page (/assessments/[id])"),
      tip("\ud83d\udd12 Security:", "This page must enforce browser lockdown, fullscreen mode, and tab-switch detection from the moment the exam starts."),
      bullet("Monaco Editor (left 60%): multi-language, syntax highlight, run button triggering Judge0 via backend"),
      bullet("Question panel (right 40%): question text, test cases, MCQ options as applicable"),
      bullet("Top bar: question navigator, timer countdown, sync status indicator, submit button"),
      bullet("Proctoring: tab-switch detection via Visibility API, WebSocket heartbeat every 10s"),
      bullet("On tab switch: show warning modal, log event, increment violation counter in Redux"),
      bullet("On submit: optimistic update, confirmation modal, redirect to results when graded"),

      h2("7.5 Admin Faculty Dashboard (/admin/dashboard)"),
      bullet("Top KPIs: total students, % above readiness threshold, upcoming assessments, at-risk count"),
      bullet("Student segmentation chart: donut chart with 4 tiers (High Performer, Steady, Need Attention, Critical)"),
      bullet("ML Insights panel: highlight cards e.g. '40% students weak in system design despite high LeetCode activity'"),
      bullet("Filters: branch, year, CGPA band, tier \u2014 all charts must respond to filter changes"),

      h2("7.6 Test Creation Page (/admin/tests/create)"),
      bullet("Step 1 \u2014 Basic Info: title, duration, target cohort, start/end datetime"),
      bullet("Step 2 \u2014 Question Selection: tab between Manual (filter + pick from bank) and AI-Generate (prompt parameters)"),
      bullet("Step 3 \u2014 Configuration: proctoring settings, attempt limits, question randomization, time per question"),
      bullet("Step 4 \u2014 Review & Schedule: full preview, send notification toggle, confirm"),

      h2("7.7 Live Proctoring Monitor (/admin/tests/[id]/monitor)"),
      bullet("Grid of student cards: name, questions answered, time elapsed, violation count, connection status"),
      bullet("Real-time updates via WebSocket \u2014 no polling"),
      bullet("Click student card to open side panel with full violation log"),
      bullet("Aggregate stats bar: total submitted, flagged, active, disconnected"),
      divider(),

      // ── SECTION 8: COMPONENT RULES ───────────────────────────────
      h1("8. Component Building Rules"),
      bullet("Always check shadcn/ui first before building a custom component"),
      bullet("All components must be TypeScript with explicit prop interfaces \u2014 no 'any' types"),
      bullet("All forms use React Hook Form + Zod schema validation"),
      bullet("Loading states: use shadcn Skeleton components, not spinners"),
      bullet("Error states: use shadcn Alert with destructive variant"),
      bullet("Empty states: always show a meaningful empty state, never a blank page"),
      bullet("All tables must be sortable and filterable (use TanStack Table)"),
      bullet("All date/time display uses the user's locale and college timezone"),
      bullet("Recharts must have accessible tooltips with full data labels"),
      bullet("Monaco Editor: only import dynamically (next/dynamic with ssr: false)"),
      divider(),

      // ── SECTION 9: STYLING ───────────────────────────────────────
      h1("9. Styling & Design System"),
      bullet("Tailwind only \u2014 no inline styles, no CSS modules, no styled-components"),
      bullet("Dark mode: use Tailwind dark: variants everywhere. The app must look great in both modes."),
      bullet("Typography scale: use Tailwind's text-sm/base/lg/xl/2xl consistently"),
      bullet("Color tokens: use shadcn CSS variables (--primary, --secondary, --muted, --accent, --destructive)"),
      bullet("Spacing: 4px base unit (Tailwind's default). Consistent padding: cards use p-6, sections use py-8"),
      bullet("Border radius: use rounded-lg for cards, rounded-md for buttons, rounded-full for badges"),
      bullet("Responsive: mobile-first. All pages must work on 375px screen width upward"),
      bullet("Animations: Framer Motion for page transitions, shadcn built-in for component animations"),
      divider(),

      // ── SECTION 10: SECURITY IN FRONTEND ────────────────────────
      h1("10. Frontend Security Rules"),
      tip("\ud83d\udee1\ufe0f Rule:", "The frontend stores NOTHING sensitive. JWT token lives in Redux (persisted to IndexedDB). Never store in localStorage directly or cookies without httpOnly flag."),
      bullet("Middleware.ts protects all routes: redirect to /login if JWT missing or expired"),
      bullet("Role-based routing: (student) routes reject admin JWT and vice versa"),
      bullet("Exam pages: additional lockdown check \u2014 must verify exam is currently active before showing questions"),
      bullet("Never log JWT tokens, user answers, or proctoring data to browser console in production"),
      bullet("Content Security Policy headers set via Next.js config (no inline scripts)"),
      bullet("XSS protection: never use dangerouslySetInnerHTML. Sanitize all user-supplied content."),
      divider(),

      // ── SECTION 11: WHAT NOT TO DO ───────────────────────────────
      h1("11. What You Must Never Do"),
      bullet("Never access the database directly \u2014 all data comes from the FastAPI backend"),
      bullet("Never call LeetCode/Codeforces/Judge0 APIs directly from the browser"),
      bullet("Never expose API keys or secrets \u2014 all env vars must be NEXT_PUBLIC_ prefixed only if truly public"),
      bullet("Never build business logic (readiness calculations, ML scoring) in the frontend"),
      bullet("Never use Monaco Editor outside of assessment pages"),
      bullet("Never use any real student data in mock/dev files \u2014 use faker.js only"),
      bullet("Never skip TypeScript \u2014 no 'as any', no implicit any"),
      divider(),

      // ── SECTION 12: DEV DASHBOARD ────────────────────────────────
      h1("12. Developer Dashboard (/dev/dashboard)"),
      body("This page is protected: only rendered if NODE_ENV === development OR super-admin role. It monitors frontend-specific health:"),
      bullet("Service worker registration status across tested browsers"),
      bullet("Cache storage hit/miss ratios and storage usage"),
      bullet("Background sync queue size and pending operations"),
      bullet("Push notification subscription count and delivery log"),
      bullet("IndexedDB storage usage and Redux Persist key inspection"),
      bullet("PWA install prompt status (shown vs accepted)"),
      bullet("Offline user simulation toggle (for testing offline exam flow)"),
      divider(),

      // ── SECTION 13: HANDOFF NOTES ────────────────────────────────
      h1("13. Working with the Backend Agent"),
      body("The Backend Agent owns the FastAPI server. You own this Next.js app. Your collaboration protocol:"),
      bullet("If an API endpoint doesn't exist yet, implement the UI with mock data using the agreed response shape, and flag it in a TODO comment"),
      bullet("Never change the API contract unilaterally \u2014 agree on request/response shape first"),
      bullet("Use the OpenAPI docs at https://api.placement360.com/docs to verify endpoint signatures"),
      bullet("If backend returns an unexpected shape, show a graceful error state \u2014 never crash"),
      tip("\ud83d\udccc Convention:", "All API calls live in src/lib/api/*.ts files. React Query hooks wrap them in src/lib/hooks/*.ts. Pages and components only call hooks, never raw fetch."),

    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("/mnt/user-data/outputs/FRONTEND_AGENT_PROMPT.docx", buf);
  console.log("Frontend prompt written.");
});