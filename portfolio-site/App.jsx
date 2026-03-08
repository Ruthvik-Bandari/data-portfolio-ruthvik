import { useState, useEffect, useCallback, useMemo } from "react";
import { motion, useScroll, useTransform, AnimatePresence } from "framer-motion";
import {
  BarChart3,
  Database,
  Brain,
  LineChart,
  PieChart,
  TrendingUp,
  Github,
  Linkedin,
  Mail,
  Sun,
  Moon,
  ExternalLink,
  Code2,
  Layers,
  Activity,
  Target,
  Sparkles,
  ChevronDown,
  ArrowUpRight,
  Shield,
  Cpu,
  FileText,
  GitBranch,
} from "lucide-react";

/* ═══════════════════════════════════════════════════════════════════════════
   THEME & DESIGN TOKENS
   ═══════════════════════════════════════════════════════════════════════════ */

const themes = {
  dark: {
    bg: "#09090b",
    bgAlt: "#0f0f12",
    surface: "#18181b",
    surfaceHover: "#1f1f23",
    border: "#27272a",
    borderGlow: "#2E75B6",
    text: "#fafafa",
    textSecondary: "#a1a1aa",
    textMuted: "#71717a",
    accent: "#2E75B6",
    accentLight: "#4A9FD8",
    teal: "#17A2B8",
    orange: "#F39C12",
    red: "#E74C3C",
    green: "#2ECC71",
    purple: "#9B59B6",
    gloss: "linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%)",
    glossBorder: "rgba(255,255,255,0.1)",
    shadow: "0 8px 32px rgba(0,0,0,0.4)",
    cardShadow: "0 4px 24px rgba(0,0,0,0.3)",
    noise: "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E\")",
  },
  light: {
    bg: "#fafbfc",
    bgAlt: "#f4f5f7",
    surface: "#ffffff",
    surfaceHover: "#f8f9fa",
    border: "#e5e7eb",
    borderGlow: "#2E75B6",
    text: "#111827",
    textSecondary: "#4b5563",
    textMuted: "#9ca3af",
    accent: "#1B4F72",
    accentLight: "#2E75B6",
    teal: "#0e8a9b",
    orange: "#d68910",
    red: "#c0392b",
    green: "#27ae60",
    purple: "#8e44ad",
    gloss: "linear-gradient(135deg, rgba(0,0,0,0.02) 0%, rgba(0,0,0,0.01) 100%)",
    glossBorder: "rgba(0,0,0,0.08)",
    shadow: "0 8px 32px rgba(0,0,0,0.08)",
    cardShadow: "0 4px 24px rgba(0,0,0,0.06)",
    noise: "none",
  },
};

/* ═══════════════════════════════════════════════════════════════════════════
   FLOATING DATA VIZ ELEMENTS (3D-style background)
   ═══════════════════════════════════════════════════════════════════════════ */

const FloatingElement = ({ delay, duration, x, y, size, theme, type }) => {
  const colors = [theme.accent, theme.teal, theme.orange, theme.green, theme.purple];
  const color = colors[type % colors.length];
  const opacity = theme === themes.dark ? 0.12 : 0.08;

  const shapes = [
    // Bar chart mini
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
      <rect x="4" y="20" width="6" height="16" rx="1" fill={color} opacity={opacity + 0.1} />
      <rect x="13" y="12" width="6" height="24" rx="1" fill={color} opacity={opacity + 0.15} />
      <rect x="22" y="16" width="6" height="20" rx="1" fill={color} opacity={opacity + 0.1} />
      <rect x="31" y="8" width="6" height="28" rx="1" fill={color} opacity={opacity + 0.2} />
    </svg>,
    // Line chart mini
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
      <polyline points="4,30 12,18 20,24 28,10 36,16" stroke={color} strokeWidth="2.5" fill="none" opacity={opacity + 0.2} strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="12" cy="18" r="2" fill={color} opacity={opacity + 0.15} />
      <circle cx="28" cy="10" r="2" fill={color} opacity={opacity + 0.15} />
    </svg>,
    // Pie chart mini
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
      <circle cx="20" cy="20" r="14" stroke={color} strokeWidth="2" opacity={opacity + 0.1} />
      <path d="M20 6 A14 14 0 0 1 33.8 24 L20 20Z" fill={color} opacity={opacity + 0.15} />
    </svg>,
    // Scatter dots
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
      <circle cx="8" cy="28" r="2.5" fill={color} opacity={opacity + 0.15} />
      <circle cx="15" cy="18" r="3" fill={color} opacity={opacity + 0.2} />
      <circle cx="24" cy="24" r="2" fill={color} opacity={opacity + 0.12} />
      <circle cx="32" cy="12" r="3.5" fill={color} opacity={opacity + 0.18} />
      <circle cx="28" cy="32" r="2" fill={color} opacity={opacity + 0.1} />
    </svg>,
    // Data grid
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
      <rect x="4" y="4" width="14" height="14" rx="2" stroke={color} strokeWidth="1.5" opacity={opacity + 0.12} />
      <rect x="22" y="4" width="14" height="14" rx="2" stroke={color} strokeWidth="1.5" opacity={opacity + 0.12} />
      <rect x="4" y="22" width="14" height="14" rx="2" stroke={color} strokeWidth="1.5" opacity={opacity + 0.12} />
      <rect x="22" y="22" width="14" height="14" rx="2" fill={color} opacity={opacity + 0.08} />
    </svg>,
  ];

  return (
    <motion.div
      style={{ position: "absolute", left: `${x}%`, top: `${y}%`, zIndex: 0 }}
      animate={{
        y: [0, -20, 0, 15, 0],
        x: [0, 10, -5, 8, 0],
        rotate: [0, 5, -3, 4, 0],
        scale: [1, 1.05, 0.98, 1.02, 1],
      }}
      transition={{
        duration: duration,
        repeat: Infinity,
        delay: delay,
        ease: "easeInOut",
      }}
    >
      {shapes[type % shapes.length]}
    </motion.div>
  );
};

const FloatingVizBackground = ({ theme }) => {
  const elements = useMemo(
    () =>
      Array.from({ length: 18 }, (_, i) => ({
        id: i,
        x: Math.random() * 90 + 5,
        y: Math.random() * 90 + 5,
        size: Math.random() * 30 + 30,
        delay: Math.random() * 4,
        duration: Math.random() * 8 + 12,
        type: i % 5,
      })),
    []
  );

  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden", pointerEvents: "none" }}>
      {elements.map((el) => (
        <FloatingElement key={el.id} {...el} theme={theme} />
      ))}
    </div>
  );
};

/* ═══════════════════════════════════════════════════════════════════════════
   GLOSS CARD COMPONENT
   ═══════════════════════════════════════════════════════════════════════════ */

const GlossCard = ({ children, theme, style = {}, hover = true, ...props }) => (
  <motion.div
    whileHover={hover ? { y: -4, scale: 1.01 } : {}}
    transition={{ type: "spring", stiffness: 300, damping: 25 }}
    style={{
      background: theme.gloss,
      backgroundColor: theme.surface,
      border: `1px solid ${theme.glossBorder}`,
      borderRadius: "16px",
      boxShadow: theme.cardShadow,
      backdropFilter: "blur(12px)",
      overflow: "hidden",
      ...style,
    }}
    {...props}
  >
    {children}
  </motion.div>
);

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION HEADER
   ═══════════════════════════════════════════════════════════════════════════ */

const SectionHeader = ({ title, subtitle, theme }) => (
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, margin: "-80px" }}
    transition={{ duration: 0.6 }}
    style={{ textAlign: "center", marginBottom: "56px" }}
  >
    <h2
      style={{
        fontFamily: "'DM Serif Display', Georgia, serif",
        fontSize: "clamp(28px, 4vw, 44px)",
        fontWeight: 400,
        color: theme.text,
        marginBottom: "12px",
        letterSpacing: "-0.02em",
      }}
    >
      {title}
    </h2>
    <p style={{ color: theme.textSecondary, fontSize: "16px", maxWidth: "560px", margin: "0 auto" }}>
      {subtitle}
    </p>
  </motion.div>
);

/* ═══════════════════════════════════════════════════════════════════════════
   STAT BADGE
   ═══════════════════════════════════════════════════════════════════════════ */

const StatBadge = ({ value, label, theme, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.9 }}
    whileInView={{ opacity: 1, scale: 1 }}
    viewport={{ once: true }}
    transition={{ delay, duration: 0.5 }}
    style={{
      textAlign: "center",
      padding: "24px 16px",
    }}
  >
    <div
      style={{
        fontFamily: "'DM Serif Display', serif",
        fontSize: "clamp(32px, 5vw, 48px)",
        fontWeight: 400,
        color: theme.accent,
        lineHeight: 1,
        marginBottom: "8px",
      }}
    >
      {value}
    </div>
    <div style={{ color: theme.textMuted, fontSize: "13px", fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.08em" }}>
      {label}
    </div>
  </motion.div>
);

/* ═══════════════════════════════════════════════════════════════════════════
   PROJECT DATA
   ═══════════════════════════════════════════════════════════════════════════ */

const projects = [
  {
    id: 1,
    title: "IPEDS Pipeline & Dashboard",
    description:
      "Production data pipeline harmonizing 72+ CSVs across 7 years of IPEDS survey data. Automated schema detection, type coercion, and deduplication for ~6,400 US institutions.",
    stats: { rows: "3M+", files: "28", changes: "47", coercions: "8" },
    tech: ["Polars", "Pandera", "DuckDB", "Plotly", "Tableau", "Power BI"],
    icon: Database,
    color: "#2E75B6",
    github: "https://github.com/Ruthvik-Bandari/data-portfolio-ruthvik/tree/main/01-ipeds-pipeline-dashboard",
  },
  {
    id: 2,
    title: "College Scorecard Analytics",
    description:
      "Predictive modeling of post-graduation earnings using 3,000+ institutional variables. XGBoost achieves R\u00B2=0.934 with SHAP explainability revealing key institutional drivers.",
    stats: { r2: "0.934", features: "35", institutions: "5,280", models: "3" },
    tech: ["XGBoost", "SHAP", "scikit-learn", "Polars", "Plotly"],
    icon: Brain,
    color: "#17A2B8",
    github: "https://github.com/Ruthvik-Bandari/data-portfolio-ruthvik/tree/main/02-college-scorecard-analytics",
  },
  {
    id: 3,
    title: "Higher Ed Text Analytics",
    description:
      "NLP pipeline for topic modeling and sentiment analysis on 238 ERIC research abstracts. BERTopic discovers latent themes in higher education research discourse.",
    stats: { docs: "238", topics: "2+", sentiment: "61%+", keywords: "2,380" },
    tech: ["BERTopic", "Transformers", "KeyBERT", "sentence-transformers", "Plotly"],
    icon: FileText,
    color: "#F39C12",
    github: "https://github.com/Ruthvik-Bandari/data-portfolio-ruthvik/tree/main/03-higher-ed-text-analytics",
  },
  {
    id: 4,
    title: "Course Sentiment Dashboard",
    description:
      "Aspect level sentiment analysis across 5,000 course reviews. Extracts sentiment for 6 categories (teaching, workload, grading) with DuckDB powered aggregation.",
    stats: { reviews: "5,000", aspects: "6", depts: "12", positive: "84%" },
    tech: ["Transformers", "DuckDB", "Polars", "Plotly", "Tableau"],
    icon: Activity,
    color: "#2ECC71",
    github: "https://github.com/Ruthvik-Bandari/data-portfolio-ruthvik/tree/main/04-course-sentiment-dashboard",
  },
];

const skills = [
  { name: "Python / Polars", level: 95, icon: Code2 },
  { name: "Data Visualization", level: 92, icon: BarChart3 },
  { name: "Machine Learning", level: 88, icon: Brain },
  { name: "NLP / Text Analytics", level: 85, icon: FileText },
  { name: "Tableau / Power BI", level: 82, icon: PieChart },
  { name: "SQL / DuckDB", level: 90, icon: Database },
  { name: "Pipeline Engineering", level: 88, icon: GitBranch },
  { name: "Statistical Analysis", level: 86, icon: TrendingUp },
];

const techStack = [
  { category: "Data", items: ["Polars", "DuckDB", "PyArrow", "Pandera"] },
  { category: "ML / NLP", items: ["XGBoost", "SHAP", "BERTopic", "Transformers", "scikit-learn"] },
  { category: "Visualization", items: ["Plotly", "Tableau", "Power BI", "Seaborn"] },
  { category: "Engineering", items: ["uv", "GitHub Actions", "pytest", "ruff", "Make"] },
];

/* ═══════════════════════════════════════════════════════════════════════════
   MAIN APP
   ═══════════════════════════════════════════════════════════════════════════ */

export default function Portfolio() {
  const [isDark, setIsDark] = useState(true);
  const theme = isDark ? themes.dark : themes.light;
  const { scrollYProgress } = useScroll();
  const heroOpacity = useTransform(scrollYProgress, [0, 0.15], [1, 0]);
  const heroScale = useTransform(scrollYProgress, [0, 0.15], [1, 0.96]);

  const toggleTheme = useCallback(() => setIsDark((p) => !p), []);

  return (
    <div style={{ background: theme.bg, color: theme.text, minHeight: "100vh", transition: "background 0.4s, color 0.4s" }}>
      {/* SEO: Meta would go in <Head> in Next.js; here we set document title */}

      {/* ── Progress Bar ─────────────────────────────── */}
      <motion.div
        style={{
          scaleX: scrollYProgress,
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          height: "3px",
          background: `linear-gradient(90deg, ${theme.accent}, ${theme.teal})`,
          transformOrigin: "left",
          zIndex: 100,
        }}
      />

      {/* ── Nav ──────────────────────────────────────── */}
      <nav
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          zIndex: 90,
          padding: "16px 32px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          backdropFilter: "blur(16px)",
          background: isDark ? "rgba(9,9,11,0.8)" : "rgba(250,251,252,0.85)",
          borderBottom: `1px solid ${theme.border}`,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <Layers size={20} color={theme.accent} />
          <span style={{ fontFamily: "'DM Serif Display', serif", fontSize: "18px" }}>RB</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
          <a href="#projects" style={{ color: theme.textSecondary, textDecoration: "none", fontSize: "14px", fontWeight: 500 }}>
            Projects
          </a>
          <a href="#skills" style={{ color: theme.textSecondary, textDecoration: "none", fontSize: "14px", fontWeight: 500 }}>
            Skills
          </a>
          <a href="#contact" style={{ color: theme.textSecondary, textDecoration: "none", fontSize: "14px", fontWeight: 500 }}>
            Contact
          </a>
          <button
            onClick={toggleTheme}
            style={{
              background: "none",
              border: `1px solid ${theme.border}`,
              borderRadius: "8px",
              padding: "6px",
              cursor: "pointer",
              display: "flex",
              color: theme.textSecondary,
            }}
            aria-label="Toggle theme"
          >
            {isDark ? <Sun size={16} /> : <Moon size={16} />}
          </button>
        </div>
      </nav>

      {/* ── Hero ──────────────────────────────────────── */}
      <motion.section style={{ opacity: heroOpacity, scale: heroScale, position: "relative", padding: "160px 32px 120px", overflow: "hidden" }}>
        <FloatingVizBackground theme={theme} />
        <div style={{ maxWidth: "900px", margin: "0 auto", position: "relative", zIndex: 1 }}>
          <motion.div initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, ease: [0.25, 0.1, 0.25, 1] }}>
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "6px 16px",
                borderRadius: "100px",
                border: `1px solid ${theme.glossBorder}`,
                background: theme.gloss,
                marginBottom: "24px",
                fontSize: "13px",
                color: theme.textSecondary,
                fontWeight: 500,
              }}
            >
              <Sparkles size={14} color={theme.accent} />
              Open to Research Assistant Opportunities
            </div>

            <h1
              style={{
                fontFamily: "'DM Serif Display', Georgia, serif",
                fontSize: "clamp(40px, 7vw, 80px)",
                fontWeight: 400,
                lineHeight: 1.05,
                letterSpacing: "-0.03em",
                marginBottom: "20px",
              }}
            >
              Ruthvik Bandari
            </h1>

            <p
              style={{
                fontSize: "clamp(18px, 2.5vw, 24px)",
                color: theme.textSecondary,
                maxWidth: "640px",
                lineHeight: 1.5,
                marginBottom: "40px",
              }}
            >
              Data Analyst & Visualization Engineer
              <br />
              <span style={{ color: theme.textMuted, fontSize: "0.85em" }}>
                MS Applied AI @ Northeastern University | 4.0 GPA
              </span>
            </p>

            <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
              <a
                href="https://github.com/Ruthvik-Bandari/data-portfolio-ruthvik"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "12px 24px",
                  borderRadius: "10px",
                  background: theme.accent,
                  color: "#fff",
                  textDecoration: "none",
                  fontSize: "15px",
                  fontWeight: 600,
                }}
              >
                <Github size={18} />
                View Portfolio
              </a>
              <a
                href="#projects"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "12px 24px",
                  borderRadius: "10px",
                  border: `1px solid ${theme.border}`,
                  color: theme.text,
                  textDecoration: "none",
                  fontSize: "15px",
                  fontWeight: 500,
                }}
              >
                Explore Projects
                <ChevronDown size={16} />
              </a>
            </div>
          </motion.div>
        </div>
      </motion.section>

      {/* ── Stats Bar ─────────────────────────────────── */}
      <section style={{ borderTop: `1px solid ${theme.border}`, borderBottom: `1px solid ${theme.border}`, background: theme.bgAlt }}>
        <div
          style={{
            maxWidth: "1100px",
            margin: "0 auto",
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
            padding: "8px 32px",
          }}
        >
          <StatBadge value="4" label="Projects" theme={theme} delay={0} />
          <StatBadge value="3M+" label="Rows Processed" theme={theme} delay={0.1} />
          <StatBadge value="47" label="Tests Passing" theme={theme} delay={0.2} />
          <StatBadge value="22" label="Visualizations" theme={theme} delay={0.3} />
          <StatBadge value="0.934" label="Best R\u00B2" theme={theme} delay={0.4} />
        </div>
      </section>

      {/* ── Projects ──────────────────────────────────── */}
      <section id="projects" style={{ maxWidth: "1100px", margin: "0 auto", padding: "96px 32px" }}>
        <SectionHeader title="Projects" subtitle="End to end data science pipelines applied to higher education research" theme={theme} />

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 480px), 1fr))", gap: "24px" }}>
          {projects.map((project, i) => {
            const Icon = project.icon;
            return (
              <motion.div
                key={project.id}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ delay: i * 0.1, duration: 0.5 }}
              >
                <GlossCard theme={theme} style={{ height: "100%", padding: "32px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "16px" }}>
                    <div
                      style={{
                        width: "40px",
                        height: "40px",
                        borderRadius: "10px",
                        background: `${project.color}18`,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      <Icon size={20} color={project.color} />
                    </div>
                    <div>
                      <div style={{ fontSize: "11px", color: theme.textMuted, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                        Project {project.id}
                      </div>
                      <h3 style={{ fontSize: "18px", fontWeight: 600, color: theme.text }}>{project.title}</h3>
                    </div>
                  </div>

                  <p style={{ color: theme.textSecondary, fontSize: "14px", lineHeight: 1.65, marginBottom: "20px" }}>
                    {project.description}
                  </p>

                  {/* Stats Grid */}
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(4, 1fr)",
                      gap: "8px",
                      marginBottom: "20px",
                      padding: "12px",
                      borderRadius: "10px",
                      background: isDark ? "rgba(255,255,255,0.03)" : "rgba(0,0,0,0.02)",
                    }}
                  >
                    {Object.entries(project.stats).map(([key, val]) => (
                      <div key={key} style={{ textAlign: "center" }}>
                        <div style={{ fontSize: "16px", fontWeight: 700, color: project.color }}>{val}</div>
                        <div style={{ fontSize: "10px", color: theme.textMuted, textTransform: "uppercase" }}>{key}</div>
                      </div>
                    ))}
                  </div>

                  {/* Tech Tags */}
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginBottom: "16px" }}>
                    {project.tech.map((t) => (
                      <span
                        key={t}
                        style={{
                          fontSize: "11px",
                          padding: "4px 10px",
                          borderRadius: "6px",
                          background: isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.05)",
                          color: theme.textSecondary,
                          fontFamily: "'JetBrains Mono', monospace",
                          fontWeight: 500,
                        }}
                      >
                        {t}
                      </span>
                    ))}
                  </div>

                  <a
                    href={project.github}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "6px",
                      color: theme.accent,
                      fontSize: "14px",
                      fontWeight: 600,
                      textDecoration: "none",
                    }}
                  >
                    View on GitHub <ArrowUpRight size={14} />
                  </a>
                </GlossCard>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* ── Skills ────────────────────────────────────── */}
      <section id="skills" style={{ background: theme.bgAlt, padding: "96px 32px" }}>
        <div style={{ maxWidth: "1100px", margin: "0 auto" }}>
          <SectionHeader title="Skills" subtitle="Core competencies in data science, analytics, and visualization" theme={theme} />

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "16px", marginBottom: "64px" }}>
            {skills.map((skill, i) => {
              const Icon = skill.icon;
              return (
                <motion.div
                  key={skill.name}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.05 }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "14px",
                    padding: "16px 20px",
                    borderRadius: "12px",
                    background: theme.surface,
                    border: `1px solid ${theme.border}`,
                  }}
                >
                  <Icon size={18} color={theme.accent} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: "14px", fontWeight: 600, marginBottom: "6px" }}>{skill.name}</div>
                    <div style={{ height: "4px", borderRadius: "4px", background: isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)" }}>
                      <motion.div
                        initial={{ width: 0 }}
                        whileInView={{ width: `${skill.level}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 1, delay: i * 0.05, ease: "easeOut" }}
                        style={{ height: "100%", borderRadius: "4px", background: `linear-gradient(90deg, ${theme.accent}, ${theme.teal})` }}
                      />
                    </div>
                  </div>
                  <span style={{ fontSize: "13px", fontFamily: "'JetBrains Mono', monospace", color: theme.textMuted, fontWeight: 500 }}>
                    {skill.level}%
                  </span>
                </motion.div>
              );
            })}
          </div>

          {/* Tech Stack Grid */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
            {techStack.map((group, i) => (
              <motion.div
                key={group.category}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <GlossCard theme={theme} style={{ padding: "24px" }} hover={false}>
                  <div style={{ fontSize: "12px", fontWeight: 700, color: theme.accent, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "12px" }}>
                    {group.category}
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                    {group.items.map((item) => (
                      <span
                        key={item}
                        style={{
                          fontSize: "12px",
                          padding: "4px 10px",
                          borderRadius: "6px",
                          border: `1px solid ${theme.border}`,
                          color: theme.textSecondary,
                        }}
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </GlossCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Contact ───────────────────────────────────── */}
      <section id="contact" style={{ maxWidth: "700px", margin: "0 auto", padding: "96px 32px", textAlign: "center" }}>
        <SectionHeader title="Let's Connect" subtitle="Interested in data visualization, analytics, or research collaboration" theme={theme} />

        <div style={{ display: "flex", justifyContent: "center", gap: "16px", flexWrap: "wrap" }}>
          {[
            { icon: Github, label: "GitHub", href: "https://github.com/Ruthvik-Bandari" },
            { icon: Linkedin, label: "LinkedIn", href: "https://linkedin.com/in/ruthvik-bandari" },
            { icon: Mail, label: "Email", href: "mailto:bandari.r@northeastern.edu" },
          ].map(({ icon: Icon, label, href }) => (
            <a
              key={label}
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "12px 24px",
                borderRadius: "10px",
                border: `1px solid ${theme.border}`,
                color: theme.text,
                textDecoration: "none",
                fontSize: "14px",
                fontWeight: 500,
                transition: "border-color 0.2s",
              }}
            >
              <Icon size={18} />
              {label}
            </a>
          ))}
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────── */}
      <footer
        style={{
          borderTop: `1px solid ${theme.border}`,
          padding: "32px",
          textAlign: "center",
          fontSize: "13px",
          color: theme.textMuted,
        }}
      >
        <p>Ruthvik Bandari | Data Science & Visualization Portfolio</p>
        <p style={{ marginTop: "4px" }}>
          Built for the Center for the Future of Higher Education, Northeastern University
        </p>
      </footer>
    </div>
  );
}
