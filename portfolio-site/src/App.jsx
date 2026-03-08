import { useState, useMemo, useCallback } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import {
  BarChart3, Database, Brain, Github, Linkedin, Mail, Sun, Moon,
  Code2, Layers, Activity, ChevronDown, ArrowUpRight, FileText,
  Workflow,
} from "lucide-react";

/* ── Floating Data Viz Background ────────────────────────────────────────── */

const FloatingElement = ({ delay, duration, x, y, size, dark, type }) => {
  const colors = ["#2E75B6", "#17A2B8", "#F39C12", "#2ECC71", "#9B59B6"];
  const c = colors[type % colors.length];
  const op = dark ? 0.14 : 0.09;

  const shapes = [
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none" key="0">
      <rect x="4" y="20" width="6" height="16" rx="1" fill={c} opacity={op}/>
      <rect x="13" y="12" width="6" height="24" rx="1" fill={c} opacity={op+0.05}/>
      <rect x="22" y="16" width="6" height="20" rx="1" fill={c} opacity={op}/>
      <rect x="31" y="8" width="6" height="28" rx="1" fill={c} opacity={op+0.08}/>
    </svg>,
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none" key="1">
      <polyline points="4,30 12,18 20,24 28,10 36,16" stroke={c} strokeWidth="2.5" fill="none" opacity={op+0.1} strokeLinecap="round" strokeLinejoin="round"/>
      <circle cx="28" cy="10" r="2" fill={c} opacity={op+0.05}/>
    </svg>,
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none" key="2">
      <circle cx="20" cy="20" r="14" stroke={c} strokeWidth="2" opacity={op}/>
      <path d="M20 6 A14 14 0 0 1 33.8 24 L20 20Z" fill={c} opacity={op+0.05}/>
    </svg>,
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none" key="3">
      <circle cx="8" cy="28" r="2.5" fill={c} opacity={op}/>
      <circle cx="15" cy="18" r="3" fill={c} opacity={op+0.08}/>
      <circle cx="32" cy="12" r="3.5" fill={c} opacity={op+0.06}/>
    </svg>,
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none" key="4">
      <rect x="4" y="4" width="14" height="14" rx="2" stroke={c} strokeWidth="1.5" opacity={op}/>
      <rect x="22" y="22" width="14" height="14" rx="2" fill={c} opacity={op-0.02}/>
    </svg>,
  ];

  return (
    <motion.div
      className="absolute pointer-events-none"
      style={{ left: `${x}%`, top: `${y}%` }}
      animate={{ y: [0,-18,0,14,0], x: [0,8,-4,6,0], rotate: [0,4,-2,3,0] }}
      transition={{ duration, repeat: Infinity, delay, ease: "easeInOut" }}
    >
      {shapes[type % shapes.length]}
    </motion.div>
  );
};

const FloatingViz = ({ dark }) => {
  const els = useMemo(() =>
    Array.from({ length: 14 }, (_, i) => ({
      id: i, x: 5+Math.random()*85, y: 5+Math.random()*85,
      size: 28+Math.random()*30, delay: Math.random()*4,
      duration: 12+Math.random()*8, type: i%5,
    })), []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {els.map(el => <FloatingElement key={el.id} {...el} dark={dark}/>)}
    </div>
  );
};

/* ── Data ─────────────────────────────────────────────────────────────────── */

const projects = [
  {
    id: 1, title: "IPEDS Pipeline & Dashboard",
    desc: "Production data pipeline harmonizing 72+ CSVs across 7 years of IPEDS survey data. Automated schema detection, type coercion, and deduplication for ~6,400 US institutions.",
    stats: [{k:"Rows",v:"3M+"},{k:"Files",v:"28"},{k:"Changes",v:"47"},{k:"Coercions",v:"8"}],
    tech: ["Polars","Pandera","DuckDB","Plotly","Tableau","Power BI"],
    icon: Database, color: "text-[#2E75B6]", colorBg: "bg-[#2E75B6]/10", colorStat: "text-[#2E75B6]",
    github: "https://github.com/Ruthvik-Bandari/data-portfolio-ruthvik/tree/main/01-ipeds-pipeline-dashboard",
  },
  {
    id: 2, title: "College Scorecard Analytics",
    desc: "Predictive modeling of post-graduation earnings using 3,000+ institutional variables. Random Forest achieves R\u00B2=0.934 with SHAP explainability analysis.",
    stats: [{k:"R\u00B2",v:"0.934"},{k:"Features",v:"35"},{k:"Institutions",v:"5,280"},{k:"Models",v:"3"}],
    tech: ["XGBoost","SHAP","scikit-learn","Polars","Plotly"],
    icon: Brain, color: "text-[#17A2B8]", colorBg: "bg-[#17A2B8]/10", colorStat: "text-[#17A2B8]",
    github: "https://github.com/Ruthvik-Bandari/data-portfolio-ruthvik/tree/main/02-college-scorecard-analytics",
  },
  {
    id: 3, title: "Higher Ed Text Analytics",
    desc: "NLP pipeline for topic modeling and sentiment analysis on ERIC research abstracts. BERTopic discovers latent themes in higher education research discourse.",
    stats: [{k:"Docs",v:"238"},{k:"Topics",v:"2+"},{k:"Sentiment",v:"61%+"},{k:"Keywords",v:"2,380"}],
    tech: ["BERTopic","Transformers","KeyBERT","sentence-transformers","Plotly"],
    icon: FileText, color: "text-[#F39C12]", colorBg: "bg-[#F39C12]/10", colorStat: "text-[#F39C12]",
    github: "https://github.com/Ruthvik-Bandari/data-portfolio-ruthvik/tree/main/03-higher-ed-text-analytics",
  },
  {
    id: 4, title: "Course Sentiment Dashboard",
    desc: "Aspect level sentiment analysis across 5,000 course reviews. Extracts sentiment for 6 categories with DuckDB powered aggregation and interactive dashboards.",
    stats: [{k:"Reviews",v:"5,000"},{k:"Aspects",v:"6"},{k:"Depts",v:"12"},{k:"Positive",v:"84%"}],
    tech: ["Transformers","DuckDB","Polars","Plotly","Tableau"],
    icon: Activity, color: "text-[#2ECC71]", colorBg: "bg-[#2ECC71]/10", colorStat: "text-[#2ECC71]",
    github: "https://github.com/Ruthvik-Bandari/data-portfolio-ruthvik/tree/main/04-course-sentiment-dashboard",
  },
];

const skillGroups = [
  { category: "Data Processing", icon: Database, skills: ["Polars","DuckDB","PyArrow","Pandera","SQL"] },
  { category: "Machine Learning", icon: Brain, skills: ["XGBoost","scikit-learn","SHAP","Feature Engineering"] },
  { category: "NLP & Text Analytics", icon: FileText, skills: ["BERTopic","Transformers","KeyBERT","spaCy","Sentiment Analysis"] },
  { category: "Data Visualization", icon: BarChart3, skills: ["Tableau","Power BI","Plotly","Seaborn","Matplotlib"] },
  { category: "Pipeline Engineering", icon: Workflow, skills: ["uv","Make","GitHub Actions","CI/CD","Parquet"] },
  { category: "Code Quality", icon: Code2, skills: ["Python 3.12+","pytest","ruff","Type Hints","Docstrings"] },
];

const stats = [
  { value: "4", label: "Projects" },
  { value: "3M+", label: "Rows Processed" },
  { value: "47", label: "Tests Passing" },
  { value: "22", label: "Visualizations" },
];

const socials = [
  { icon: Github, label: "GitHub", href: "https://github.com/Ruthvik-Bandari" },
  { icon: Linkedin, label: "LinkedIn", href: "https://www.linkedin.com/in/ruthvik-nath-bandari-908b00247/" },
  { icon: Mail, label: "Email", href: "mailto:bandari.ru@northeastern.edu" },
];

/* ── Main Component ──────────────────────────────────────────────────────── */

export default function Portfolio() {
  const [dark, setDark] = useState(true);
  const { scrollYProgress } = useScroll();
  const heroOpacity = useTransform(scrollYProgress, [0, 0.15], [1, 0]);
  const heroScale = useTransform(scrollYProgress, [0, 0.15], [1, 0.96]);

  const bg = dark ? "bg-[#09090b]" : "bg-[#fafbfc]";
  const bgAlt = dark ? "bg-[#0f0f12]" : "bg-[#f4f5f7]";
  const surface = dark ? "bg-[#18181b]" : "bg-white";
  const borderColor = dark ? "border-[#27272a]" : "border-[#e5e7eb]";
  const textPrimary = dark ? "text-[#fafafa]" : "text-[#111827]";
  const textSecondary = dark ? "text-[#a1a1aa]" : "text-[#4b5563]";
  const textMuted = dark ? "text-[#71717a]" : "text-[#9ca3af]";
  const accentText = dark ? "text-[#2E75B6]" : "text-[#1B4F72]";
  const glassBorder = dark ? "border-white/10" : "border-black/[0.08]";
  const cardGlow = dark ? "shadow-[0_4px_24px_rgba(0,0,0,0.3)]" : "shadow-[0_4px_24px_rgba(0,0,0,0.06)]";
  const subtleBg = dark ? "bg-white/[0.04]" : "bg-black/[0.03]";

  return (
    <div className={`${bg} ${textPrimary} min-h-screen w-full overflow-x-hidden transition-colors duration-300`}>

      {/* ── Progress Bar ─────────────────────────────── */}
      <motion.div
        className="fixed top-0 left-0 right-0 h-[3px] z-[100] origin-left bg-gradient-to-r from-[#2E75B6] to-[#17A2B8]"
        style={{ scaleX: scrollYProgress }}
      />

      {/* ── Nav ──────────────────────────────────────── */}
      <nav className={`fixed top-0 inset-x-0 z-90 px-6 sm:px-10 py-4 flex justify-between items-center backdrop-blur-xl border-b ${borderColor} ${dark ? "bg-[#09090b]/80" : "bg-[#fafbfc]/85"}`}>
        <div className="flex items-center gap-2.5">
          <Layers size={20} className={accentText}/>
          <span className="font-serif text-lg tracking-tight">RNB</span>
        </div>
        <div className="flex items-center gap-6">
          {["Projects","Skills","Contact"].map(item => (
            <a key={item} href={`#${item.toLowerCase()}`} className={`${textSecondary} text-sm font-medium hover:${textPrimary} transition-colors hidden sm:block`}>{item}</a>
          ))}
          <button onClick={() => setDark(d => !d)} aria-label="Toggle theme" className={`p-1.5 rounded-lg border ${borderColor} ${textSecondary} cursor-pointer hover:${textPrimary} transition-colors`}>
            {dark ? <Sun size={16}/> : <Moon size={16}/>}
          </button>
        </div>
      </nav>

      {/* ── Hero ──────────────────────────────────────── */}
      <motion.section className="relative pt-40 pb-28 px-6 sm:px-10 overflow-hidden" style={{ opacity: heroOpacity, scale: heroScale }}>
        <FloatingViz dark={dark}/>
        <div className="max-w-[1400px] mx-auto relative z-10">
          <motion.div initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, ease: [0.25,0.1,0.25,1] }}>
            <h1 className="font-serif text-5xl sm:text-6xl lg:text-8xl font-normal leading-[1.05] tracking-[-0.03em] mb-5">
              Ruthvik Nath Bandari
            </h1>
            <p className={`text-xl sm:text-2xl ${textSecondary} max-w-xl leading-relaxed mb-10`}>
              Applied AI Engineer
              <br/>
              <span className={`${textMuted} text-[0.85em]`}>
                Turning complex datasets into clear, actionable insights
              </span>
            </p>
            <div className="flex gap-3 flex-wrap">
              <a href="https://github.com/Ruthvik-Bandari/data-portfolio-ruthvik" target="_blank" rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-[#2E75B6] text-white text-[15px] font-semibold hover:bg-[#2563a0] transition-colors">
                <Github size={18}/> View Portfolio
              </a>
              <a href="#projects" className={`inline-flex items-center gap-2 px-6 py-3 rounded-xl border ${borderColor} text-[15px] font-medium hover:${bgAlt} transition-colors`}>
                Explore Projects <ChevronDown size={16}/>
              </a>
            </div>
          </motion.div>
        </div>
      </motion.section>

      {/* ── Stats ─────────────────────────────────────── */}
      <section className={`border-y ${borderColor} ${bgAlt}`}>
        <div className="max-w-[1400px] mx-auto grid grid-cols-2 sm:grid-cols-4 px-6 sm:px-10 py-2">
          {stats.map((s, i) => (
            <motion.div key={s.label} className="text-center py-6 px-4" initial={{ opacity: 0, scale: 0.9 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }} transition={{ delay: i*0.1 }}>
              <div className={`font-serif text-3xl sm:text-4xl lg:text-5xl font-normal ${accentText} leading-none mb-2`}>{s.value}</div>
              <div className={`${textMuted} text-xs font-semibold uppercase tracking-wider`}>{s.label}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── Projects ──────────────────────────────────── */}
      <section id="projects" className="max-w-[1400px] mx-auto py-24 px-6 sm:px-10">
        <motion.div className="text-center mb-14" initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
          <h2 className="font-serif text-3xl sm:text-4xl lg:text-[44px] font-normal tracking-[-0.02em] mb-3">Projects</h2>
          <p className={`${textSecondary} text-base max-w-[560px] mx-auto`}>End to end data science pipelines from raw data to interactive dashboards</p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-7">
          {projects.map((p, i) => {
            const Icon = p.icon;
            return (
              <motion.div key={p.id} initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-60px" }} transition={{ delay: i*0.1, duration: 0.5 }}
                className="h-full"
              >
                <motion.div
                  whileHover={{ y: -2 }}
                  transition={{ type: "spring", stiffness: 400, damping: 30 }}
                  className={`${surface} border ${glassBorder} rounded-2xl ${cardGlow} p-8 h-full flex flex-col`}
                >
                  {/* Header */}
                  <div className="flex items-center gap-3 mb-4">
                    <div className={`w-10 h-10 rounded-[10px] ${p.colorBg} flex items-center justify-center shrink-0`}>
                      <Icon size={20} className={p.color}/>
                    </div>
                    <div>
                      <div className={`text-[11px] ${textMuted} font-semibold uppercase tracking-wide`}>Project {p.id}</div>
                      <h3 className="text-lg font-semibold">{p.title}</h3>
                    </div>
                  </div>

                  {/* Description */}
                  <p className={`${textSecondary} text-sm leading-relaxed mb-auto min-h-[72px]`}>{p.desc}</p>

                  {/* Stats */}
                  <div className={`grid grid-cols-4 gap-2 my-5 p-3.5 rounded-[10px] ${subtleBg}`}>
                    {p.stats.map(s => (
                      <div key={s.k} className="text-center">
                        <div className={`text-base font-bold ${p.colorStat}`}>{s.v}</div>
                        <div className={`text-[10px] ${textMuted} uppercase tracking-wide`}>{s.k}</div>
                      </div>
                    ))}
                  </div>

                  {/* Tech */}
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {p.tech.map(t => (
                      <span key={t} className={`text-[11px] px-2.5 py-1 rounded-md ${subtleBg} ${textSecondary} font-mono font-medium`}>{t}</span>
                    ))}
                  </div>

                  {/* Link */}
                  <a href={p.github} target="_blank" rel="noopener noreferrer" className={`inline-flex items-center gap-1.5 ${accentText} text-sm font-semibold hover:underline`}>
                    View on GitHub <ArrowUpRight size={14}/>
                  </a>
                </motion.div>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* ── Skills ────────────────────────────────────── */}
      <section id="skills" className={`${bgAlt} py-24 px-6 sm:px-10`}>
        <div className="max-w-[1400px] mx-auto">
          <motion.div className="text-center mb-14" initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
            <h2 className="font-serif text-3xl sm:text-4xl lg:text-[44px] font-normal tracking-[-0.02em] mb-3">Skills & Tools</h2>
            <p className={`${textSecondary} text-base max-w-[560px] mx-auto`}>Technologies and methodologies across the data science lifecycle</p>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {skillGroups.map((g, i) => {
              const Icon = g.icon;
              return (
                <motion.div key={g.category} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i*0.08 }}
                  className={`${surface} border ${glassBorder} rounded-2xl ${cardGlow} p-7 h-full`}
                >
                  <div className="flex items-center gap-2.5 mb-4">
                    <Icon size={18} className={accentText}/>
                    <span className="text-sm font-bold">{g.category}</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {g.skills.map(s => (
                      <span key={s} className={`text-[13px] px-3.5 py-1.5 rounded-lg border ${borderColor} ${textSecondary} font-medium`}>{s}</span>
                    ))}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── Contact ───────────────────────────────────── */}
      <section id="contact" className="max-w-2xl mx-auto py-24 px-6 sm:px-10 text-center">
        <motion.div className="mb-14" initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
          <h2 className="font-serif text-3xl sm:text-4xl lg:text-[44px] font-normal tracking-[-0.02em] mb-3">Let's Connect</h2>
          <p className={`${textSecondary} text-base`}></p>
        </motion.div>

        <div className="flex justify-center gap-4 flex-wrap">
          {socials.map(({ icon: Icon, label, href }) => (
            <a key={label} href={href} target="_blank" rel="noopener noreferrer"
              className={`inline-flex items-center gap-2 px-6 py-3 rounded-xl border ${borderColor} text-sm font-medium hover:${bgAlt} transition-colors`}>
              <Icon size={18}/> {label}
            </a>
          ))}
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────── */}
      <footer className={`border-t ${borderColor} py-8 text-center text-[13px] ${textMuted}`}>
        Ruthvik Nath Bandari | Data Science & Visualization Portfolio
      </footer>
    </div>
  );
}
