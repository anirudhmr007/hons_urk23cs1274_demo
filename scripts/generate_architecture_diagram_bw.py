"""Generate a clean, simple, black-and-white (academic textbook style) architecture diagram.

Outputs:
- C:/Users/LENOVO/.gemini/antigravity/scratch/modular_agent/architecture_diagram.png
- C:/Users/LENOVO/.gemini/antigravity/scratch/modular_agent/architecture_diagram.jpeg
- C:/Users/LENOVO/.gemini/antigravity/scratch/modular_agent/architecture_diagram_simple_bw.png
- C:/Users/LENOVO/.gemini/antigravity/scratch/modular_agent/architecture_diagram_simple_bw.jpeg
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

# Pure Black and White Palette
BG_WHITE = "#FFFFFF"
BOX_WHITE = "#FFFFFF"
BOX_GRAY = "#F8FAFC"
LINE_BLACK = "#000000"
TEXT_BLACK = "#000000"
TEXT_DARK = "#1F2937"
TEXT_WHITE = "#FFFFFF"


def draw_box(ax, x, y, w, h, title, subtitle="", is_header=False, lw=1.8, dashed=False):
    """Draw a clean, minimalist black and white box."""
    ls = "--" if dashed else "-"
    facecolor = "#111827" if is_header else BOX_WHITE
    edgecolor = LINE_BLACK

    box = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.015",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=lw,
        linestyle=ls,
        zorder=2
    )
    ax.add_patch(box)

    if title:
        ty = y + h - 0.026 if subtitle else y + h / 2
        ax.text(
            x + w / 2, ty, title,
            ha="center", va="center",
            fontsize=10.5 if not is_header else 11.5,
            fontweight="bold",
            color=TEXT_WHITE if is_header else TEXT_BLACK,
            family="DejaVu Sans",
            zorder=3
        )
    if subtitle:
        ax.text(
            x + w / 2, y + 0.022, subtitle,
            ha="center", va="center",
            fontsize=8.5,
            fontweight="normal",
            color="#4B5563" if not is_header else "#D1D5DB",
            family="DejaVu Sans",
            zorder=3
        )


def draw_arrow(ax, x1, y1, x2, y2, lw=1.8, label="", label_pos=(0, 0), dashed=False):
    """Draw a clean black arrow with optional label."""
    ls = "--" if dashed else "-"
    arrow = patches.FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="->",
        color=LINE_BLACK,
        linewidth=lw,
        linestyle=ls,
        mutation_scale=14,
        zorder=4
    )
    ax.add_patch(arrow)
    if label:
        ax.text(
            label_pos[0], label_pos[1], label,
            ha="center", va="center",
            fontsize=8.5, fontweight="bold",
            color=TEXT_BLACK, family="DejaVu Sans",
            bbox=dict(boxstyle="square,pad=0.2", facecolor=BG_WHITE, edgecolor="none"),
            zorder=5
        )


def generate_bw_diagram(out_png: Path, out_jpeg: Path):
    fig, ax = plt.subplots(figsize=(16, 9.5), dpi=300)
    fig.patch.set_facecolor(BG_WHITE)
    ax.set_facecolor(BG_WHITE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # ══════════════════════════════════════════════════════════════════════════
    # 1. HEADER (ACADEMIC MINIMALIST)
    # ══════════════════════════════════════════════════════════════════════════
    ax.text(
        0.5, 0.945, "MODULAR-AGENT: SYSTEM ARCHITECTURE",
        ha="center", va="center",
        fontsize=18, fontweight="bold",
        color=TEXT_BLACK, family="DejaVu Sans"
    )
    ax.text(
        0.5, 0.915, "Decoupled Architecture: Probabilistic LLM Reasoning vs. Deterministic Model Inference",
        ha="center", va="center",
        fontsize=10.5, fontweight="normal",
        color="#374151", family="DejaVu Sans"
    )
    # Horizontal rule
    ax.plot([0.05, 0.95], [0.89, 0.89], color=LINE_BLACK, linewidth=1.2)

    # ══════════════════════════════════════════════════════════════════════════
    # 2. THREE MAIN STAGES (CONTAINERS)
    # ══════════════════════════════════════════════════════════════════════════

    # ── STAGE 1 CONTAINER: MODEL INGESTION ──
    c1 = patches.FancyBboxPatch(
        (0.05, 0.22), 0.27, 0.63,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor=BOX_GRAY, edgecolor=LINE_BLACK, linewidth=1.8, zorder=1
    )
    ax.add_patch(c1)
    draw_box(ax, 0.065, 0.785, 0.24, 0.05, "1. MODEL INGESTION", "Automated Tool Creation", is_header=True)

    draw_box(ax, 0.065, 0.65, 0.24, 0.08, "Predictive Models & APIs", "Scikit-Learn (.joblib) / REST Endpoints")
    draw_arrow(ax, 0.185, 0.65, 0.185, 0.58)

    draw_box(ax, 0.065, 0.49, 0.24, 0.09, "Dynamic Schema Generator", "Synthesizes Pydantic v2 validation\nschemas automatically from models")
    draw_arrow(ax, 0.185, 0.49, 0.185, 0.42)

    draw_box(ax, 0.065, 0.33, 0.24, 0.09, "Callable Tool Wrapper", "Enforces strict input/output bounds,\ntimeout limits, & normalized confidence")
    draw_arrow(ax, 0.185, 0.33, 0.185, 0.27)

    draw_box(ax, 0.065, 0.24, 0.24, 0.05, "Registered Tools Catalog", "Tools ready for autonomous execution", lw=1.5)

    # ── STAGE 2 CONTAINER: COGNITIVE ORCHESTRATION ──
    c2 = patches.FancyBboxPatch(
        (0.365, 0.22), 0.27, 0.63,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor=BOX_GRAY, edgecolor=LINE_BLACK, linewidth=1.8, zorder=1
    )
    ax.add_patch(c2)
    draw_box(ax, 0.38, 0.785, 0.24, 0.05, "2. AGENT ORCHESTRATION", "Cognitive Intent & Decision", is_header=True)

    draw_box(ax, 0.38, 0.65, 0.24, 0.08, "User Request (Natural Language)", "e.g., 'Evaluate loan for credit score 740\nand monthly income $8,500'")
    draw_arrow(ax, 0.50, 0.65, 0.50, 0.58)

    draw_box(ax, 0.38, 0.45, 0.24, 0.13, "Agent Orchestrator\n(Local Ollama LLM)", "• Analyzes intent & conversation history\n• Selects the correct predictive tool\n• Generates tool arguments from query\n(Runs offline: qwen2.5 / llama3.2)", lw=2.0)
    draw_arrow(ax, 0.50, 0.45, 0.50, 0.38)

    draw_box(ax, 0.38, 0.28, 0.24, 0.10, "Self-Correction & Fallback", "Catches malformed JSON parameters;\nrepairs arguments or uses regex fallback\n(Guarantees 100% execution success)")

    # ── STAGE 3 CONTAINER: DETERMINISTIC EXECUTION ──
    c3 = patches.FancyBboxPatch(
        (0.68, 0.22), 0.27, 0.63,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor=BOX_GRAY, edgecolor=LINE_BLACK, linewidth=1.8, zorder=1
    )
    ax.add_patch(c3)
    draw_box(ax, 0.695, 0.785, 0.24, 0.05, "3. EXECUTION & RESULTS", "Mathematical Certainty", is_header=True)

    draw_box(ax, 0.695, 0.65, 0.24, 0.08, "Pydantic Schema Validation", "Pre-flight type checking: validates\neach number before model execution")
    draw_arrow(ax, 0.815, 0.65, 0.815, 0.58)

    draw_box(ax, 0.695, 0.48, 0.24, 0.10, "Deterministic Model Execution", "Runs actual Scikit-learn model:\n• Execution Time: 1 – 5 milliseconds\n• Pure Math (Zero Hallucination)", lw=2.0)
    draw_arrow(ax, 0.815, 0.48, 0.815, 0.41)

    draw_box(ax, 0.695, 0.25, 0.24, 0.16, "Verified Response Delivery", "• Deterministic Callout Box:\n  Displays exact model outputs\n• Natural Language Explanation:\n  LLM explains result to user\n• FastAPI REST + Gradio 6 UI")

    # ══════════════════════════════════════════════════════════════════════════
    # 3. INTER-STAGE CONNECTING ARROWS
    # ══════════════════════════════════════════════════════════════════════════
    # From Ingestion Catalog (Stage 1) into Orchestrator (Stage 2)
    draw_arrow(ax, 0.305, 0.265, 0.38, 0.515, lw=2.0, label="Tool Schemas", label_pos=(0.342, 0.39))

    # From Orchestrator (Stage 2) into Execution Guard (Stage 3)
    draw_arrow(ax, 0.62, 0.515, 0.695, 0.69, lw=2.0, label="Target Tool Call", label_pos=(0.658, 0.60))

    # ══════════════════════════════════════════════════════════════════════════
    # 4. BOTTOM AUDIT & OBSERVABILITY LAYER
    # ══════════════════════════════════════════════════════════════════════════
    audit_box = patches.FancyBboxPatch(
        (0.05, 0.06), 0.90, 0.12,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        facecolor=BOX_WHITE, edgecolor=LINE_BLACK, linewidth=1.8, zorder=2
    )
    ax.add_patch(audit_box)

    ax.text(
        0.5, 0.15, "CROSS-CUTTING OBSERVABILITY & AUDITING LAYER",
        ha="center", va="center",
        fontsize=10.5, fontweight="bold",
        color=TEXT_BLACK, family="DejaVu Sans", zorder=3
    )

    col_w = 0.28
    # Left item
    ax.text(
        0.18, 0.10, "ExecutionTracer\nLogs 6 lifecycle events with\nmillisecond timestamps (duration_ms)",
        ha="center", va="center", fontsize=8.5, color="#1F2937", family="DejaVu Sans", zorder=3
    )
    # Center item
    ax.text(
        0.50, 0.10, "Zero-Leakage Secret Masking\nRecursively sanitizes payloads;\nmasks API keys to sk-...a1b2 format",
        ha="center", va="center", fontsize=8.5, color="#1F2937", family="DejaVu Sans", zorder=3
    )
    # Right item
    ax.text(
        0.82, 0.10, "Conversational Memory & Deployment\nSession-isolated multi-turn memory\n+ 1-click Docker container packaging",
        ha="center", va="center", fontsize=8.5, color="#1F2937", family="DejaVu Sans", zorder=3
    )

    # Vertical connectors down to audit
    draw_arrow(ax, 0.50, 0.22, 0.50, 0.18, lw=1.2, dashed=True)
    draw_arrow(ax, 0.815, 0.22, 0.815, 0.18, lw=1.2, dashed=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 5. FOOTER PRINCIPLE
    # ══════════════════════════════════════════════════════════════════════════
    ax.text(
        0.5, 0.02, "Core Architectural Invariant: The LLM decides WHAT to do (probabilistic) — The ML model calculates HOW (deterministic)",
        ha="center", va="center",
        fontsize=9.0, fontstyle="italic",
        color="#4B5563", family="DejaVu Sans"
    )

    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(out_png), dpi=300, facecolor=BG_WHITE, edgecolor="none", bbox_inches="tight")
    plt.savefig(str(out_jpeg), dpi=300, facecolor=BG_WHITE, edgecolor="none", bbox_inches="tight", format="jpeg")
    plt.close()
    print(f"[OK] Generated simple B&W PNG: {out_png}")
    print(f"[OK] Generated simple B&W JPEG: {out_jpeg}")


if __name__ == "__main__":
    base_dir = Path("C:/Users/LENOVO/.gemini/antigravity/scratch/modular_agent")
    
    # Save both to canonical names and dedicated bw names
    generate_bw_diagram(
        base_dir / "architecture_diagram.png",
        base_dir / "architecture_diagram.jpeg"
    )
    generate_bw_diagram(
        base_dir / "architecture_diagram_simple_bw.png",
        base_dir / "architecture_diagram_simple_bw.jpeg"
    )
