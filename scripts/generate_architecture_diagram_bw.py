"""
Professional black-and-white architecture diagram for Modular-Agent.
Clean flowchart style with thick visible arrows, numbered steps, and clear flow.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch
from pathlib import Path


def box(ax, x, y, w, h, text, sub=None, lw=1.5, fontsize=10, fill="white"):
    """Clean rectangular box with optional subtitle."""
    rect = patches.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.008",
        facecolor=fill, edgecolor="black", linewidth=lw, zorder=2)
    ax.add_patch(rect)
    if sub:
        ax.text(x + w/2, y + h/2 + 0.014, text, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", zorder=3)
        ax.text(x + w/2, y + h/2 - 0.014, sub, ha="center", va="center",
                fontsize=fontsize - 2.2, color="#333333", zorder=3)
    else:
        ax.text(x + w/2, y + h/2, text, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", zorder=3)


def header_box(ax, x, y, w, h, text, sub=None, fontsize=10.5):
    """Dark header box (black fill, white text)."""
    rect = patches.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.008",
        facecolor="#1a1a1a", edgecolor="black", linewidth=1.5, zorder=2)
    ax.add_patch(rect)
    if sub:
        ax.text(x + w/2, y + h/2 + 0.012, text, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", color="white", zorder=3)
        ax.text(x + w/2, y + h/2 - 0.012, sub, ha="center", va="center",
                fontsize=fontsize - 2.5, color="#cccccc", zorder=3)
    else:
        ax.text(x + w/2, y + h/2, text, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", color="white", zorder=3)


def thick_arrow(ax, x1, y1, x2, y2, lw=2.5):
    """Thick, clearly visible solid arrow."""
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(
                    arrowstyle="-|>", color="black", lw=lw,
                    mutation_scale=18, shrinkA=2, shrinkB=2),
                zorder=4)


def thin_arrow(ax, x1, y1, x2, y2, lw=1.5, dashed=False):
    """Thinner connecting arrow."""
    style = "dashed" if dashed else "solid"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(
                    arrowstyle="-|>", color="black", lw=lw, linestyle=style,
                    mutation_scale=14, shrinkA=2, shrinkB=2),
                zorder=4)


def arrow_label(ax, x, y, text, fontsize=8):
    """Label next to an arrow."""
    ax.text(x, y, text, ha="center", va="center",
            fontsize=fontsize, fontstyle="italic", color="black",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
            zorder=5)


def main():
    fig, ax = plt.subplots(figsize=(15, 10), dpi=300)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # ── TITLE ─────────────────────────────────────────────────────────
    ax.text(0.50, 0.965, "MODULAR-AGENT  —  SYSTEM ARCHITECTURE",
            ha="center", va="center", fontsize=17, fontweight="bold")
    ax.text(0.50, 0.940, "Three-Stage Decoupled Pipeline: Ingestion  →  Orchestration  →  Execution",
            ha="center", va="center", fontsize=10, color="#444444")
    ax.plot([0.06, 0.94], [0.925, 0.925], color="black", lw=1.0)

    # ══════════════════════════════════════════════════════════════════
    # ROW 1 — INPUT SOURCES  (Top of diagram)
    # ══════════════════════════════════════════════════════════════════
    box(ax, 0.08, 0.86, 0.22, 0.05,
        "Scikit-Learn Model", "(.joblib / .pkl file)", fontsize=9.5)
    box(ax, 0.39, 0.86, 0.22, 0.05,
        "REST API Endpoint", "(HTTP POST /predict)", fontsize=9.5)
    box(ax, 0.70, 0.86, 0.22, 0.05,
        "Demo Sentiment Model", "(Built-in NLP pipeline)", fontsize=9.5)

    # Arrows down from inputs → Ingestion Engine
    thick_arrow(ax, 0.19, 0.858, 0.40, 0.805)
    thick_arrow(ax, 0.50, 0.858, 0.50, 0.805)
    thick_arrow(ax, 0.81, 0.858, 0.60, 0.805)

    # ══════════════════════════════════════════════════════════════════
    # STEP 1 — INGESTION ENGINE
    # ══════════════════════════════════════════════════════════════════
    ax.text(0.035, 0.78, "STEP\n  1", ha="center", va="center",
            fontsize=12, fontweight="bold",
            bbox=dict(facecolor="#e0e0e0", edgecolor="black", boxstyle="round,pad=0.4", lw=1.2))

    header_box(ax, 0.08, 0.755, 0.84, 0.05,
               "INGESTION ENGINE  —  Automated Model-to-Tool Conversion")

    # Three sub-components in a row
    box(ax, 0.08, 0.68, 0.26, 0.06,
        "Model Inspector", "Reads features, classes, methods", fontsize=9)
    box(ax, 0.37, 0.68, 0.26, 0.06,
        "Schema Generator", "Creates Pydantic v2 contracts", fontsize=9)
    box(ax, 0.66, 0.68, 0.26, 0.06,
        "Tool Registry", "Registers validated callable tools", fontsize=9)

    # Horizontal flow arrows within Step 1
    thick_arrow(ax, 0.34, 0.71, 0.37, 0.71)
    thick_arrow(ax, 0.63, 0.71, 0.66, 0.71)

    # Vertical arrow down to Step 2
    thick_arrow(ax, 0.50, 0.675, 0.50, 0.635)
    arrow_label(ax, 0.565, 0.655, "tool definitions")

    # ══════════════════════════════════════════════════════════════════
    # STEP 2 — USER QUERY + AGENT ORCHESTRATOR
    # ══════════════════════════════════════════════════════════════════
    ax.text(0.035, 0.59, "STEP\n  2", ha="center", va="center",
            fontsize=12, fontweight="bold",
            bbox=dict(facecolor="#e0e0e0", edgecolor="black", boxstyle="round,pad=0.4", lw=1.2))

    # User query entering from left
    box(ax, 0.08, 0.565, 0.20, 0.055,
        "User Query", '"Evaluate loan for $8500"', fontsize=9)
    thick_arrow(ax, 0.28, 0.592, 0.32, 0.592)

    # Main orchestrator box
    header_box(ax, 0.32, 0.555, 0.60, 0.07,
               "AGENT ORCHESTRATOR  —  Cognitive Reasoning & Tool Selection",
               "Local Ollama LLM (qwen2.5 / llama3.2)  •  Selects tool  •  Extracts arguments")

    # Vertical arrow down to Step 3
    thick_arrow(ax, 0.50, 0.55, 0.50, 0.505)
    arrow_label(ax, 0.57, 0.528, "tool call + args")

    # Self-correction side box
    box(ax, 0.72, 0.465, 0.20, 0.07,
        "Self-Correction", "If args invalid:\nretry (max 2) or\nregex fallback", fontsize=8.5, lw=1.0)
    # Arrow from orchestrator to self-correction
    thin_arrow(ax, 0.82, 0.555, 0.82, 0.535)
    # Arrow back up from self-correction
    thin_arrow(ax, 0.72, 0.50, 0.625, 0.57, lw=1.2)
    arrow_label(ax, 0.665, 0.545, "retry")

    # ══════════════════════════════════════════════════════════════════
    # STEP 3 — VALIDATION + MODEL EXECUTION
    # ══════════════════════════════════════════════════════════════════
    ax.text(0.035, 0.44, "STEP\n  3", ha="center", va="center",
            fontsize=12, fontweight="bold",
            bbox=dict(facecolor="#e0e0e0", edgecolor="black", boxstyle="round,pad=0.4", lw=1.2))

    box(ax, 0.08, 0.415, 0.26, 0.055,
        "Input Validation", "Pydantic checks every argument", fontsize=9)
    thick_arrow(ax, 0.34, 0.442, 0.37, 0.442)
    header_box(ax, 0.37, 0.41, 0.30, 0.065,
               "ML MODEL EXECUTION",
               "Deterministic  •  1–5 ms  •  Zero hallucination")
    thick_arrow(ax, 0.67, 0.442, 0.70, 0.442)
    box(ax, 0.70, 0.415, 0.22, 0.055,
        "Output Validation", "Verifies prediction format", fontsize=9)

    # Vertical arrow down to Step 4
    thick_arrow(ax, 0.50, 0.405, 0.50, 0.365)
    arrow_label(ax, 0.575, 0.385, "verified result")

    # ══════════════════════════════════════════════════════════════════
    # STEP 4 — RESPONSE DELIVERY
    # ══════════════════════════════════════════════════════════════════
    ax.text(0.035, 0.32, "STEP\n  4", ha="center", va="center",
            fontsize=12, fontweight="bold",
            bbox=dict(facecolor="#e0e0e0", edgecolor="black", boxstyle="round,pad=0.4", lw=1.2))

    box(ax, 0.08, 0.29, 0.26, 0.06,
        "Deterministic Callout Box", "Shows exact model prediction,\nseparated from LLM text", fontsize=8.8)
    box(ax, 0.37, 0.29, 0.26, 0.06,
        "LLM Explanation", "Natural language interpretation\nof the model result", fontsize=8.8)
    box(ax, 0.66, 0.29, 0.26, 0.06,
        "Session Memory", "Stores conversation context\nfor follow-up questions", fontsize=8.8)

    # Horizontal flow arrows within Step 4
    thick_arrow(ax, 0.34, 0.32, 0.37, 0.32)
    thick_arrow(ax, 0.63, 0.32, 0.66, 0.32)

    # Arrow down to delivery
    thick_arrow(ax, 0.50, 0.285, 0.50, 0.245)

    # Final delivery
    header_box(ax, 0.20, 0.20, 0.60, 0.045,
               "USER INTERFACE  —  FastAPI REST API  +  5-Tab Gradio 6 Dashboard")

    # ══════════════════════════════════════════════════════════════════
    # BOTTOM BAR — OBSERVABILITY (runs across all steps)
    # ══════════════════════════════════════════════════════════════════
    ax.plot([0.06, 0.94], [0.175, 0.175], color="black", lw=0.6, linestyle="dotted")

    ax.add_patch(patches.FancyBboxPatch(
        (0.06, 0.08), 0.88, 0.085,
        boxstyle="round,pad=0.010", facecolor="#f5f5f5",
        edgecolor="black", linewidth=1.2, zorder=2))

    ax.text(0.50, 0.148, "CROSS-CUTTING LAYER  (Active Across All Steps)",
            ha="center", va="center", fontsize=9.5, fontweight="bold", zorder=3)

    ax.text(0.19, 0.115, "Execution Tracer", ha="center", va="center",
            fontsize=9, fontweight="bold", zorder=3)
    ax.text(0.19, 0.095, "ISO timestamps + ms latency\nfor every lifecycle event",
            ha="center", va="center", fontsize=7.5, color="#333", zorder=3)

    ax.text(0.50, 0.115, "Secret Sanitizer", ha="center", va="center",
            fontsize=9, fontweight="bold", zorder=3)
    ax.text(0.50, 0.095, "Masks API keys to sk-...a1b2\nin all logs and UI output",
            ha="center", va="center", fontsize=7.5, color="#333", zorder=3)

    ax.text(0.81, 0.115, "Deployment Generator", ha="center", va="center",
            fontsize=9, fontweight="bold", zorder=3)
    ax.text(0.81, 0.095, "1-click Dockerfile &\ndocker-compose packaging",
            ha="center", va="center", fontsize=7.5, color="#333", zorder=3)

    # ── Footer ──
    ax.text(0.50, 0.04,
            "Core Invariant:   LLM decides WHAT tool to invoke   →   ML model calculates the exact answer   →   They never cross roles",
            ha="center", va="center", fontsize=8.5, fontstyle="italic", color="#555")

    # ── Save ──
    plt.tight_layout(pad=0.3)
    base = Path("C:/Users/LENOVO/.gemini/antigravity/scratch/modular_agent")
    for ext, fmt in [(".png", "png"), (".jpeg", "jpeg")]:
        for name in [f"architecture_diagram{ext}", f"architecture_diagram_simple_bw{ext}"]:
            plt.savefig(str(base / name), dpi=300, facecolor="white",
                        bbox_inches="tight", format=fmt)
    plt.close()
    print("[OK] All diagram files saved successfully.")


if __name__ == "__main__":
    main()
