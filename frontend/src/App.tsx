import { useState, useEffect } from "react";
import type { CSSProperties } from "react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from "recharts";
import {
  Play, TrendingUp, Users, DollarSign, Target, Sun, Moon,
} from "lucide-react";

// ════════════════════════════════════════════════════════════
// PRESTES — Simulador de Leads
// Design System: brandbook Prestes
//   Light → Vittace: 70% Branco | 20% Verde Escuro | 10% Verde Prestes
//   Dark  → Vista:  70% Chumbo  | 20% Branco       | 10% Verde Prestes
// ════════════════════════════════════════════════════════════

interface TimelineNode {
  mes_ciclo: number;
  mes_calendario: number;
  leads: number;
  leads_qualificados: number;
  cpl: number;
}

// URL da API: usa variável de ambiente em produção, localhost em dev
const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

const MONTHS_ABBR = ["","Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"];
const MONTHS_FULL = ["","Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"];

// Estágios fixos — sem filtro, sempre exibidos como linha do tempo obrigatória
const CAMPAIGN_STAGES = [
  { mes_ciclo:  1, label: "lançamento",      sublabel: "início da captação"  },
  { mes_ciclo:  4, label: "pico de tração",  sublabel: "máxima de leads"     },
  { mes_ciclo:  8, label: "sustentação",     sublabel: "estabilização"       },
  { mes_ciclo: 16, label: "estoque resíduo", sublabel: "fase final"          },
];

// ── Fonte global ───────────────────────────────────────────
const F = "'Lufga', 'Outfit', system-ui, sans-serif";

// ── Helpers de estilo ──────────────────────────────────────
const inputStyle: CSSProperties = {
  width: "100%",
  padding: "0.65rem 0.85rem",
  border: "1px solid var(--input-border)",
  borderRadius: "6px",
  background: "var(--input-bg)",
  color: "var(--text-body)",
  fontFamily: F,
  fontWeight: 300,
  fontSize: "0.88rem",
  outline: "none",
  transition: "border-color .2s",
  cursor: "pointer",
};

const cardStyle: CSSProperties = {
  background: "var(--bg-card)",
  border: "1px solid var(--border)",
  borderRadius: "8px",
  padding: "1.5rem",
};

// Labels: Lufga Bold uppercase (10% proporção — cor primária ou neon no dark)
const mkLabel = (dark: boolean): CSSProperties => ({
  display: "block",
  fontFamily: F,
  fontWeight: 700,
  fontSize: "0.58rem",
  textTransform: "uppercase",
  letterSpacing: "2px",
  color: dark ? "rgba(255,255,255,.55)" : "#044d41",
  marginBottom: "0.4rem",
});

// Títulos de seção: Lufga Bold
const mkSectionTitle = (dark: boolean): CSSProperties => ({
  fontFamily: F,
  fontWeight: 700,
  fontSize: "0.62rem",
  textTransform: "uppercase",
  letterSpacing: "2.5px",
  color: dark ? "#ffffff" : "#044d41",
  margin: 0,
});

// ═══════════════════════════════════════════════════════════
// COMPONENTE PRINCIPAL
// ═══════════════════════════════════════════════════════════
export default function App() {
  const [theme, setTheme]         = useState<"light" | "dark">("light");
  const [pracas, setPracas]       = useState<string[]>([]);
  const [produtos, setProdutos]   = useState<string[]>([]);
  const [apiStatus, setApiStatus] = useState<"loading" | "ok" | "error">("loading");
  const [verbaFocused, setVerbaFocused] = useState(false);
  const [form, setForm]         = useState({
    praca: "", produto: "",
    investimentoMensal: 15000,
    mesInicio: 3,
    mesesProjecao: 12,
  });
  const [timeline, setTimeline] = useState<TimelineNode[]>([]);
  const [loading, setLoading]   = useState(false);

  const dark = theme === "dark";

  // Propaga tema no root
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  // Carrega metadados da API (timeout de 90s para cold start do Render)
  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 90_000);

    fetch(`${API_URL}/api/metadata`, { signal: controller.signal })
      .then((r) => { if (!r.ok) throw new Error("API error"); return r.json(); })
      .then((d) => {
        const pracasList   = d.pracas?.length   ? d.pracas   : [];
        const produtosList = d.produtos?.length  ? d.produtos : ["Produto 1"];
        setPracas(pracasList);
        setProdutos(produtosList);
        setApiStatus("ok");
        setForm((p) => ({
          ...p,
          praca:   pracasList[0]   ?? p.praca,
          produto: produtosList[0] ?? p.produto,
        }));
      })
      .catch(() => setApiStatus("error"))
      .finally(() => clearTimeout(timer));
  }, []);

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const resp = await fetch(`${API_URL}/api/simulate-lifecycle`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          praca:                 form.praca,
          produto:               form.produto,
          investimento_mensal:   form.investimentoMensal,
          mes_calendario_inicio: form.mesInicio,
          meses_projecao:        form.mesesProjecao,
        }),
      });
      const d = await resp.json();
      setTimeline(d.timeline || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // Mês calendário correspondente ao mês do ciclo
  const calMonth = (mc: number) => {
    const n = ((form.mesInicio - 1 + (mc - 1)) % 12) + 1;
    return { n, abbr: MONTHS_ABBR[n], full: MONTHS_FULL[n] };
  };

  const stageActive = (mc: number) => mc <= form.mesesProjecao;
  const stageData   = (mc: number) => timeline.find((t) => t.mes_ciclo === mc);

  // KPIs acumulados
  const totalLeads  = timeline.reduce((a, t) => a + t.leads, 0);
  const totalQualif = timeline.reduce((a, t) => a + t.leads_qualificados, 0);
  const avgCpl      = timeline.length ? timeline.reduce((a, t) => a + t.cpl, 0) / timeline.length : 0;
  const peakLeads   = timeline.length ? Math.max(...timeline.map((t) => t.leads)) : 0;

  const fmt    = (v: number) => v.toLocaleString("pt-BR");
  const fmtBRL = (v: number) =>
    `R$ ${v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  // Progresso da linha do tempo (quantos estágios ativos / total de gaps)
  const activeCount = CAMPAIGN_STAGES.filter((s) => stageActive(s.mes_ciclo)).length;
  const progressPct = Math.max(0, (activeCount - 1) / (CAMPAIGN_STAGES.length - 1)) * 100;

  // Alertas de sinergia
  const alert =
    form.praca === "Praça 2" && form.produto === "Produto 1"
      ? { ok: false, msg: "Baixa sinergia histórica — CPL projetado em alto risco." }
    : form.praca === "Praça 1" && form.produto === "Produto 3"
      ? { ok: true,  msg: "Alta conversão para esta combinação na régua." }
    : null;

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", fontFamily: F, color: "var(--text-body)" }}>

      {/* ── HEADER ──────────────────────────────────────────── */}
      <header style={{
        background: "var(--header-bg)",
        borderBottom: `1px solid var(--header-border)`,
        padding: "0.85rem 2rem",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        position: "sticky",
        top: 0,
        zIndex: 50,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          {/* Logo Prestes — branco/transparente, funciona em ambos os temas */}
          <img
            src="/logo-prestes.png"
            alt="Prestes"
            style={{ height: 28, width: "auto", objectFit: "contain" }}
          />

          <div style={{ width: 1, height: 26, background: "var(--header-border)", margin: "0 0.25rem" }} />

          <span style={{
            fontFamily: F, fontWeight: 300, fontSize: "0.68rem",
            letterSpacing: "2.5px", textTransform: "uppercase",
            color: "var(--header-text)",
          }}>
            simulador de leads · projeção de ciclo
          </span>
        </div>

        {/* Botão de tema */}
        <button
          onClick={() => setTheme(dark ? "light" : "dark")}
          style={{
            display: "flex", alignItems: "center", gap: "0.4rem",
            padding: "0.4rem 0.85rem",
            background: "transparent",
            border: "1px solid var(--header-border)",
            borderRadius: "6px",
            color: dark ? "#84e115" : "rgba(255,255,255,.75)",
            fontFamily: F, fontWeight: 700, fontSize: "0.65rem",
            letterSpacing: "1px", textTransform: "uppercase",
            cursor: "pointer",
            transition: "all .2s",
          }}
        >
          {dark ? <Sun size={12} /> : <Moon size={12} />}
          {dark ? "light" : "dark"}
        </button>
      </header>

      <div style={{ display: "flex", height: "calc(100vh - 56px)" }}>

        {/* ── SIDEBAR ─────────────────────────────────────────── */}
        <aside style={{
          width: 285,
          background: "var(--bg-sidebar)",
          borderRight: "1px solid var(--border)",
          padding: "1.75rem 1.5rem",
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
          gap: "1.1rem",
          flexShrink: 0,
        }}>

          {/* Título sidebar */}
          <div>
            <p style={mkSectionTitle(dark)}>parâmetros</p>
            <div style={{ width: 22, height: 3, background: "#84e115", borderRadius: 2, marginTop: 5 }} />
          </div>

          {/* Banner de status da API */}
          {apiStatus === "loading" && (
            <div style={{
              padding: "0.65rem 0.85rem",
              background: dark ? "rgba(132,225,21,.06)" : "#f0fdf4",
              borderLeft: "3px solid #84e115",
              borderRadius: "0 5px 5px 0",
              fontSize: "0.7rem",
              fontWeight: 300,
              lineHeight: 1.45,
              color: dark ? "#d9f99d" : "#166534",
            }}>
              Conectando ao servidor... pode levar alguns segundos.
            </div>
          )}
          {apiStatus === "error" && (
            <div style={{
              padding: "0.65rem 0.85rem",
              background: dark ? "rgba(239,68,68,.08)" : "#fff5f5",
              borderLeft: "3px solid #ef4444",
              borderRadius: "0 5px 5px 0",
              fontSize: "0.7rem",
              fontWeight: 300,
              lineHeight: 1.45,
              color: dark ? "#fca5a5" : "#b91c1c",
            }}>
              Servidor indisponível — tente recarregar a página.
            </div>
          )}

          {/* Praça */}
          <div>
            <label style={mkLabel(dark)}>praça</label>
            <select
              value={form.praca}
              onChange={(e) => setForm({ ...form, praca: e.target.value })}
              style={inputStyle}
              disabled={apiStatus !== "ok"}
            >
              {apiStatus !== "ok" && <option value="">—</option>}
              {pracas.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>

          {/* Produto */}
          <div>
            <label style={mkLabel(dark)}>produto</label>
            <select
              value={form.produto}
              onChange={(e) => setForm({ ...form, produto: e.target.value })}
              style={inputStyle}
              disabled={apiStatus !== "ok"}
            >
              {apiStatus !== "ok" && <option value="">—</option>}
              {produtos.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>

          {/* Verba */}
          <div>
            <label style={mkLabel(dark)}>verba mensal</label>
            <input
              type={verbaFocused ? "number" : "text"}
              value={
                verbaFocused
                  ? form.investimentoMensal
                  : form.investimentoMensal.toLocaleString("pt-BR", {
                      style: "currency",
                      currency: "BRL",
                      minimumFractionDigits: 0,
                      maximumFractionDigits: 0,
                    })
              }
              onFocus={() => setVerbaFocused(true)}
              onBlur={() => setVerbaFocused(false)}
              onChange={(e) => {
                const val = Number(e.target.value);
                if (!isNaN(val)) setForm({ ...form, investimentoMensal: val });
              }}
              style={{ ...inputStyle, cursor: "text" }}
            />
          </div>

          {/* Mês início */}
          <div>
            <label style={mkLabel(dark)}>mês calendário (início)</label>
            <select value={form.mesInicio} onChange={(e) => setForm({ ...form, mesInicio: Number(e.target.value) })} style={inputStyle}>
              {MONTHS_FULL.map((m, i) => i > 0 && <option key={i} value={i}>{m}</option>)}
            </select>
          </div>

          {/* Duração */}
          <div>
            <label style={mkLabel(dark)}>duração da projeção</label>
            <select value={form.mesesProjecao} onChange={(e) => setForm({ ...form, mesesProjecao: Number(e.target.value) })} style={inputStyle}>
              {[6, 12, 18, 24, 36].map((m) => (
                <option key={m} value={m}>{m} meses</option>
              ))}
            </select>
          </div>

          {/* Alerta de sinergia */}
          {alert && (
            <div style={{
              padding: "0.65rem 0.85rem",
              background: alert.ok ? "var(--accent-bg)" : (dark ? "rgba(239,68,68,.08)" : "#fff5f5"),
              borderLeft: `3px solid ${alert.ok ? "#84e115" : "#ef4444"}`,
              borderRadius: "0 5px 5px 0",
              fontSize: "0.7rem",
              fontWeight: 300,
              lineHeight: 1.45,
              color: alert.ok ? (dark ? "#c8f050" : "#044d41") : (dark ? "#fca5a5" : "#b91c1c"),
            }}>
              {alert.msg}
            </div>
          )}

          <div style={{ flex: 1 }} />

          {/* Botão CTA — Verde Escuro → hover Verde Prestes */}
          <CTAButton onClick={handleSimulate} loading={loading} disabled={apiStatus !== "ok" || !form.praca} />
        </aside>

        {/* ── MAIN ──────────────────────────────────────────────── */}
        <main style={{
          flex: 1,
          padding: "1.75rem 2rem",
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
          gap: "1.2rem",
        }}>

          {/* ── LINHA DO TEMPO DA CAMPANHA ───────────────────────── */}
          <section style={cardStyle}>
            <div style={{ marginBottom: "1.4rem" }}>
              <p style={mkSectionTitle(dark)}>linha do tempo da campanha</p>
              <p style={{ fontFamily: F, fontWeight: 300, fontSize: "0.7rem", color: "var(--text-muted)", marginTop: 5 }}>
                estágios automáticos a partir de{" "}
                <strong style={{ fontWeight: 700, color: dark ? "#ffffff" : "#044d41" }}>
                  {MONTHS_FULL[form.mesInicio]}
                </strong>
                {" "}· {form.mesesProjecao} meses de projeção
              </p>
            </div>

            {/* Track da linha */}
            <div style={{ position: "relative", padding: "0.25rem 0 1rem" }}>
              {/* Linha de fundo (do centro do nó 1 ao nó 4) */}
              <div style={{
                position: "absolute",
                top: "calc(0.25rem + 19px)",
                left: "12.5%", right: "12.5%",
                height: 2,
                background: "var(--border)",
              }} />
              {/* Linha de progresso (verde prestes — accent 10%) */}
              <div style={{
                position: "absolute",
                top: "calc(0.25rem + 19px)",
                left: "12.5%",
                height: 2,
                // cada gap representa 25% da distância total (75% total / 3 gaps)
                width: `calc(${progressPct} * 0.75%)`,
                background: dark
                  ? "linear-gradient(to right, #84e115, #a8f040)"
                  : "linear-gradient(to right, #044d41, #84e115)",
                transition: "width .5s ease",
                zIndex: 1,
              }} />

              {/* Nós dos estágios */}
              <div style={{ display: "flex", justifyContent: "space-between", position: "relative", zIndex: 2 }}>
                {CAMPAIGN_STAGES.map((s) => {
                  const active = stageActive(s.mes_ciclo);
                  const cal    = calMonth(s.mes_ciclo);
                  const sd     = stageData(s.mes_ciclo);

                  return (
                    <div key={s.mes_ciclo} style={{ display: "flex", flexDirection: "column", alignItems: "center", flex: 1 }}>
                      {/* Círculo */}
                      <div style={{
                        width: 40, height: 40, borderRadius: "50%",
                        border: "2px solid",
                        borderColor: active
                          ? (dark ? "#84e115" : "#044d41")
                          : "var(--node-idle-brd)",
                        background: active ? "var(--node-active-bg)" : "var(--node-idle-bg)",
                        color: active ? "var(--node-active-txt)" : "var(--node-idle-txt)",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        fontFamily: F, fontWeight: 800, fontSize: "0.85rem",
                        opacity: active ? 1 : 0.4,
                        transition: "all .3s",
                      }}>
                        {s.mes_ciclo}
                      </div>

                      {/* Texto abaixo */}
                      <div style={{ marginTop: "0.65rem", textAlign: "center", maxWidth: 120 }}>
                        <p style={{
                          fontFamily: F, fontWeight: 700, fontSize: "0.62rem",
                          textTransform: "lowercase",
                          letterSpacing: "0.5px",
                          color: active
                            ? (dark ? "#ffffff" : "#044d41")
                            : "var(--text-muted)",
                          opacity: active ? 1 : 0.4,
                          margin: 0,
                        }}>
                          {s.label}
                        </p>
                        <p style={{
                          fontFamily: F, fontWeight: 300, fontSize: "0.62rem",
                          color: "var(--text-muted)",
                          marginTop: 2,
                          opacity: active ? 0.8 : 0.3,
                        }}>
                          m{s.mes_ciclo} · {cal.abbr}
                        </p>

                        {/* Badge de leads — aparece após simulação */}
                        {sd && (
                          <div style={{
                            marginTop: "0.45rem",
                            background: "var(--accent-bg)",
                            border: "1px solid var(--accent-border)",
                            borderRadius: 5,
                            padding: "0.25rem 0.55rem",
                          }}>
                            <p style={{ fontFamily: F, fontWeight: 300, fontSize: "0.58rem", color: "var(--text-muted)", margin: 0 }}>leads</p>
                            <p style={{
                              fontFamily: F, fontWeight: 800, fontSize: "0.85rem",
                              color: dark ? "#84e115" : "#044d41",
                              margin: 0,
                            }}>
                              {fmt(sd.leads)}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </section>

          {/* ── KPI CARDS ─────────────────────────────────────────── */}
          {timeline.length > 0 && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1rem" }}>
              {[
                { lbl: "leads estimados",    val: fmt(totalLeads),  sub: "total acumulado no período",  Icon: Users      },
                { lbl: "leads qualificados", val: fmt(totalQualif), sub: "modelo preditivo",            Icon: Target     },
                { lbl: "CPL médio",          val: fmtBRL(avgCpl),   sub: "custo por lead",              Icon: DollarSign },
                { lbl: "pico de leads",      val: fmt(peakLeads),   sub: "máximo mensal",               Icon: TrendingUp },
              ].map(({ lbl, val, sub, Icon }, i) => (
                <div key={i} style={{ ...cardStyle, borderLeft: "4px solid #84e115" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <p style={mkLabel(dark)}>{lbl}</p>
                    {/* Ícone accent 10% */}
                    <Icon size={15} style={{ color: "#84e115", flexShrink: 0, marginTop: 1 }} />
                  </div>
                  <p style={{
                    fontFamily: F, fontWeight: 800, fontSize: "1.45rem",
                    color: dark ? "#ffffff" : "#044d41",
                    lineHeight: 1.15, margin: "0.3rem 0 0",
                  }}>
                    {val}
                  </p>
                  <p style={{ fontFamily: F, fontWeight: 300, fontSize: "0.68rem", color: "var(--text-muted)", marginTop: 4 }}>
                    {sub}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* ── GRÁFICO DE ÁREA ───────────────────────────────────── */}
          {timeline.length > 0 && (
            <section style={{ ...cardStyle, flex: 1 }}>
              <div style={{ marginBottom: "1rem" }}>
                <p style={mkSectionTitle(dark)}>tração predita do ativo</p>
                <p style={{ fontFamily: F, fontWeight: 300, fontSize: "0.7rem", color: "var(--text-muted)", marginTop: 5 }}>
                  projeção ols log-log · {form.mesesProjecao} meses · R$ {form.investimentoMensal.toLocaleString("pt-BR")}/mês
                </p>
              </div>

              <div style={{ height: 260 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={timeline} margin={{ top: 8, right: 16, left: 0, bottom: 16 }}>
                    <defs>
                      <linearGradient id="gL" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%"  stopColor="#044d41" stopOpacity={dark ? .4 : .12} />
                        <stop offset="95%" stopColor="#044d41" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="gQ" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%"  stopColor="#84e115" stopOpacity={dark ? .5 : .28} />
                        <stop offset="95%" stopColor="#84e115" stopOpacity={0} />
                      </linearGradient>
                    </defs>

                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke={dark ? "rgba(255,255,255,.05)" : "#f0f0f0"}
                      vertical={false}
                    />
                    <XAxis
                      dataKey="mes_ciclo"
                      tickFormatter={(val, i) => `m${val} (${MONTHS_ABBR[timeline[i]?.mes_calendario]})`}
                      stroke={dark ? "rgba(255,255,255,.08)" : "#e8e8e8"}
                      tick={{ fill: dark ? "rgba(255,255,255,.35)" : "#6b6b6b", fontSize: 10, fontFamily: F }}
                      dy={8}
                    />
                    <YAxis
                      stroke={dark ? "rgba(255,255,255,.08)" : "#e8e8e8"}
                      tick={{ fill: dark ? "rgba(255,255,255,.35)" : "#6b6b6b", fontSize: 10, fontFamily: F }}
                    />
                    <Tooltip
                      contentStyle={{
                        background: dark ? "#272727" : "#ffffff",
                        border: `1px solid ${dark ? "rgba(255,255,255,.1)" : "#e8e8e8"}`,
                        borderRadius: 8,
                        fontFamily: F,
                      }}
                      labelStyle={{
                        color: dark ? "#ffffff" : "#044d41",
                        fontWeight: 700, fontSize: "0.78rem", marginBottom: 6,
                      }}
                      itemStyle={{ color: "var(--text-muted)", fontWeight: 300, fontSize: "0.75rem" }}
                      formatter={(value, name) => [
                        fmt(Number(value)),
                        name === "leads" ? "leads brutos" : "leads qualificados",
                      ]}
                      labelFormatter={(l) => `mês de ciclo: ${l}`}
                    />

                    {/* Verde Escuro para leads brutos / Verde Prestes (accent) para qualificados */}
                    <Area type="monotone" dataKey="leads"              stroke="#044d41" strokeWidth={2.5} fill="url(#gL)" />
                    <Area type="monotone" dataKey="leads_qualificados" stroke="#84e115" strokeWidth={2}   fill="url(#gQ)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Legenda */}
              <div style={{ display: "flex", gap: "1.5rem", justifyContent: "center", marginTop: "0.75rem" }}>
                {[
                  { c: "#044d41", l: "leads brutos" },
                  { c: "#84e115", l: "leads qualificados" },
                ].map(({ c, l }) => (
                  <div key={l} style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <div style={{ width: 22, height: 2, background: c, borderRadius: 1 }} />
                    <span style={{ fontFamily: F, fontWeight: 300, fontSize: "0.68rem", color: "var(--text-muted)" }}>
                      {l}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* ── ESTADO VAZIO ──────────────────────────────────────── */}
          {timeline.length === 0 && !loading && (
            <div style={{
              flex: 1, minHeight: 260,
              display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
              border: "2px dashed var(--border)",
              borderRadius: "8px",
              padding: "3.5rem",
              textAlign: "center",
            }}>
              <div style={{
                width: 56, height: 56, borderRadius: "50%",
                background: dark ? "rgba(132,225,21,.06)" : "rgba(4,77,65,.05)",
                display: "flex", alignItems: "center", justifyContent: "center",
                marginBottom: "1rem",
              }}>
                <TrendingUp size={24} style={{ color: dark ? "rgba(132,225,21,.35)" : "rgba(4,77,65,.25)" }} />
              </div>
              <p style={{ fontFamily: F, fontWeight: 700, fontSize: "0.88rem", color: "var(--text-muted)", marginBottom: "0.35rem" }}>
                aguardando parâmetros
              </p>
              <p style={{ fontFamily: F, fontWeight: 300, fontSize: "0.65rem", color: "var(--text-muted)", textTransform: "lowercase", letterSpacing: "2px" }}>
                configure e lance a simulação
              </p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════════════════
// BOTÃO CTA DA SIDEBAR
// Verde Escuro padrão → hover Verde Prestes (accent 10%)
// ════════════════════════════════════════════════════════════
function CTAButton({ onClick, loading, disabled }: { onClick: () => void; loading: boolean; disabled: boolean }) {
  const [hov, setHov] = useState(false);
  const inactive = loading || disabled;

  return (
    <button
      onClick={onClick}
      disabled={inactive}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        width: "100%",
        padding: "0.88rem",
        background: inactive
          ? "rgba(4,77,65,.3)"
          : hov
          ? "#84e115"
          : "linear-gradient(135deg, #044d41 0%, #00342c 100%)",
        color: inactive ? "rgba(255,255,255,.4)" : hov ? "#1c1c1c" : "#ffffff",
        border: "none",
        borderRadius: "6px",
        fontFamily: "'Lufga', 'Outfit', system-ui, sans-serif",
        fontWeight: 700,
        fontSize: "0.65rem",
        letterSpacing: "2.5px",
        textTransform: "uppercase",
        cursor: inactive ? "not-allowed" : "pointer",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "0.5rem",
        transition: "background .25s, color .25s",
      }}
    >
      {loading ? "calculando..." : "lançar simulação"}
      {!loading && <Play size={12} />}
    </button>
  );
}
