"""Chapter 1 & Chapter 2 text and logic for Modular-Agent Extended Project Report.
Provides in-depth academic rigor, literature review, and comparative analysis.
"""

def get_ch1_ch2_code():
    return '''
    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 1: INTRODUCTION
    # ══════════════════════════════════════════════════════════════════════════
    chapter_title("CHAPTER 1\\nINTRODUCTION")

    p(
        "The advent of deep transformer architectures has revolutionized cognitive computing, artificial intelligence, "
        "and computational linguistics. Contemporary generative models—spanning massive scale parameterizations such as "
        "GPT-4, Claude 3.5, and LLaMA 3—exhibit unprecedented capabilities in synthesizing complex dialogue, interpreting "
        "ambiguous natural language prompts, translating idioms across multiple dialects, and orchestrating high-level cognitive "
        "strategies. In industrial applications, enterprises have attempted to harness these capabilities to build conversational "
        "assistants capable of interacting with human operators across financial planning, medical diagnosis, legal contract "
        "analysis, and supply chain logistics. However, despite their linguistic sophistication, Large Language Models (LLMs) "
        "suffer from an intrinsic theoretical limitation: they are fundamentally non-deterministic, probabilistic next-token "
        "predictors governed by stochastic sampling over high-dimensional vocabulary distributions [1]."
    )
    p(
        "Mathematically, when an autoregressive language model generates an output sequence, it computes conditional probability "
        "densities over discrete token vocabularies. The model has no internal representation of arithmetic truth, formal logic, "
        "or bounded empirical distributions. When prompted to perform precision calculations—such as projecting the fair market "
        "valuation of a commercial real estate property, calculating the actuarial default probability of an unsecured consumer "
        "loan, or assessing the malignancy probability of a fine-needle biopsy—the model does not compute mathematical equations. "
        "Instead, it samples the most statistically plausible sequence of character glyphs that resemble numeric digits in its "
        "pre-training corpus. Consequently, language models frequently hallucinate plausible-sounding yet factually erroneous and "
        "mathematically invalid numerical outcomes [4]. In safety-critical and legally regulated industries, such hallucinations "
        "represent intolerable liabilities."
    )
    p(
        "From the perspective of cognitive science and computational psychology, this deficiency can be understood through Dual-Process "
        "Theory, famously articulated by Kahneman. Human cognition is bifurcated into System 1 (fast, intuitive, heuristic, and associative "
        "thinking) and System 2 (slow, deliberative, logical, and algorithmic calculation). Large Language Models, by their autoregressive "
        "nature, operate almost entirely as System 1 heuristic engines. They excel at rapid associative synthesis, pattern matching, "
        "and narrative generation. However, when complex mathematical calculation or rigorous statistical estimation is demanded, forcing a "
        "purely heuristic System 1 engine to simulate System 2 deliberative mathematics invariably induces stochastic drift and arithmetic "
        "hallucination. Trustworthy artificial intelligence demands a hybrid neuro-symbolic architecture where System 1 language models "
        "manage perceptual communication while delegating analytical tasks to verified System 2 computational engines."
    )
    p(
        "In stark contrast to generative language models, classical predictive machine learning (ML) models excel at exact, "
        "reproducible, and calibrated statistical inference. Algorithms founded on statistical learning theory—such as Gradient "
        "Boosted Decision Trees (LightGBM, XGBoost), Random Forests, Support Vector Regressors, Ridge Regressors, and Regularized "
        "Logistic Classifiers—are trained to minimize empirical loss functions over structured, multi-dimensional feature spaces [2]. "
        "When presented with a valid feature vector, a compiled Scikit-learn estimator evaluates vectorized mathematical equations in "
        "compiled memory, yielding deterministic continuous scalar predictions or class probability distributions in sub-5-millisecond "
        "latencies. These models provide mathematical guarantees: identical feature inputs invariably produce identical numeric "
        "predictions, completely devoid of hallucination or stochastic drift."
    )
    p(
        "Nevertheless, classical predictive models operate as rigid black boxes. They possess zero natural language comprehension. "
        "They demand structured, tabular floating-point numpy arrays ordered strictly by column index. They cannot interpret human "
        "dialogue, parse messy conversational text, disambiguate missing variables, or articulate the practical business implications "
        "of their numerical outputs in fluent prose. Furthermore, deploying hundreds of disparate machine learning models across an "
        "enterprise traditionally requires authoring custom REST API microservices, client integration software, and user interface "
        "dashboards for every single estimator."
    )
    p(
        "To reconcile the natural language reasoning of LLMs with the deterministic mathematical precision of predictive ML, the "
        "paradigm of autonomous 'tool-calling' agents has emerged. In an agentic framework, an LLM acts as a central coordinator, "
        "interpreting user intent and invoking external computational functions or APIs. However, prevailing agent architectures "
        "(such as LangChain, CrewAI, AutoGen, and Microsoft Semantic Kernel) suffer from a critical architectural defect: they tightly "
        "couple cognitive reasoning with tool execution. They treat complex statistical models as arbitrary Python functions, lack "
        "automated schema extraction, force developers to write brittle manual boilerplate, mix probabilistic prose with statistical "
        "outputs, and crash catastrophically when lightweight edge LLMs produce malformed JSON syntax [3, 10]."
    )
    p(
        "To resolve these foundational challenges, this project conceptualizes, engineers, and verifies Modular-Agent: a production-grade, "
        "decoupled framework that bridges predictive machine learning models and autonomous language agents. Modular-Agent enforces an "
        "immutable architectural invariant: the language model serves strictly as an executive cognitive router responsible for intent "
        "comprehension and parameter extraction, while mathematical inference is strictly delegated to compiled, deterministic "
        "estimators executing inside isolated contract wrappers. This chapter details the technical objectives, formulates the "
        "problem statement, and provides an executive summary of the entire project report."
    )

    sub_heading("1.1 OBJECTIVE")
    p(
        "The primary mission of this project is to research, design, develop, and empirically evaluate a decoupled software "
        "framework that converts heterogeneous predictive machine learning models (.joblib/.pkl) and HTTP REST microservices into "
        "autonomous, schema-validated tools governed by intelligent language agents. The project pursues six specific technical objectives:"
    )
    p(
        "1. Automated Ingestion & Reflection Engine: Engineer a reflection subsystem that inspects serialized Scikit-learn estimator "
        "binaries (.joblib/.pkl) and remote OpenAPI/REST endpoints, automatically extracting input feature counts, parameter names, "
        "data types, and target classification labels without requiring manual developer coding."
    )
    p(
        "2. Dynamic Pydantic v2 Contract Synthesis: Implement runtime code synthesis utilizing Pydantic v2 to programmatically generate "
        "strongly-typed input and output validation classes (BaseModel) alongside OpenAI-compliant function-calling JSON schemas, "
        "guaranteeing strict data contract enforcement at sub-millisecond speeds."
    )
    p(
        "3. Decoupled Dual-Tier Output Presentation: Design and construct an isolated presentation architecture that visually and "
        "logically separates deterministic statistical outputs from probabilistic LLM explanations. The raw mathematical prediction "
        "is rendered inside a dedicated, immutable callout container, preventing the LLM from altering or hallucinating calculations."
    )
    p(
        "4. Resilient Self-Correction & Small-Model Fallback: Formulate a fault-tolerant cognitive recovery pipeline capable of operating "
        "reliably on compact, offline open-weight language models (e.g., Ollama Qwen 2.5 0.5B / LLaMA 3.2 1B). The subsystem provides "
        "bounded schema-guided reprompting and dynamic regular expression argument recovery, ensuring zero unhandled crashes."
    )
    p(
        "5. Distributed Observability & Enterprise Security: Build a high-precision execution tracer recording microsecond-level lifecycle "
        "telemetry (request reception, tool selection, argument validation, mathematical execution, and response synthesis) coupled with "
        "a recursive zero-leakage secret sanitizer that redacts credentials in all operational logs and UI views."
    )
    p(
        "6. Cloud-Native Deployment Studio: Develop an automated deployment generator that inspects active agent pipelines and compiles "
        "self-contained Dockerfile, docker-compose.yml, and environment configurations into downloadable production packages."
    )

    sub_heading("1.2 PROBLEM STATEMENT")
    p(
        "Enterprise artificial intelligence systems currently face an acute engineering dilemma: how to combine the conversational "
        "adaptability of generative AI with the verifiable accuracy of predictive statistical models without compromising safety, "
        "latency, or auditability. Existing software patterns exhibit five severe structural pathologies:"
    )
    p(
        "• The Arithmetic Hallucination Pathology: Autoregressive language models cannot guarantee arithmetic truth. When tasked with "
        "predictive estimations (e.g., property valuation or risk scoring), LLMs sample tokens from statistical distributions rather "
        "than computing mathematical models, generating erroneous figures that can lead to catastrophic business decisions."
    )
    p(
        "• The Tight Coupling & Boilerplate Pathology: Contemporary agent libraries (LangChain, CrewAI) require engineers to manually "
        "write hundreds of lines of glue code, custom schema dictionaries, and wrapper functions for every individual machine learning "
        "model. When an underlying model is retrained with new features, the agent pipeline silently breaks due to schema drift."
    )
    p(
        "• The Small-Model Brittleness Pathology: Enterprise data sovereignty mandates on-premises, offline execution. However, compact "
        "open-weight models (sub-3B parameters) frequently produce malformed JSON syntax, unescaped quotation marks, or natural language "
        "chatter instead of strict JSON tool calls. Existing frameworks lack robust fallback mechanisms, throwing fatal parsing exceptions."
    )
    p(
        "• The Observability & Security Vacuum: Prevailing frameworks log cleartext prompt transcripts directly to stdout or export traces "
        "to third-party cloud monitoring SaaS, exposing confidential business metrics, user credentials, and proprietary model weights."
    )
    p(
        "• The Adversarial Parameter Manipulation Risk: Without strongly enforced typed schemas, language models are susceptible to indirect "
        "prompt injection attacks where adversarial users inject conversational instructions that manipulate tool parameters (e.g., passing "
        "negative loan values or extreme credit scores). A resilient agent architecture must enforce strict boundary validation prior to "
        "executing statistical estimators."
    )
    p(
        "Therefore, there is an urgent academic and industrial need for a decoupled, mathematically verified, and schema-enforced "
        "agent architecture that automates predictive model onboarding while providing absolute deterministic execution guarantees."
    )

    sub_heading("1.3 CHAPTER WISE SUMMARY")
    p(
        "The remainder of this project report is systematically organized across four subsequent chapters and supplementary appendices:"
    )
    p(
        "• Chapter 2 - Literature Survey: Explores the theoretical and practical foundations of autonomous LLM tool calling. It critically "
        "evaluates legacy frameworks (ReAct, LangChain, CrewAI, AutoGen, Semantic Kernel), contrasts them with high-throughput inference "
        "servers (Triton, vLLM), dissects data management and serialization hazards, analyzes system performance bottlenecks, and formalizes "
        "the limitations that Modular-Agent resolves. A comprehensive comparative matrix summarizes these architectural dimensions."
    )
    p(
        "• Chapter 3 - Explanation of Proposed System: Details the complete design of Modular-Agent. It introduces the Decoupled Invariant "
        "Theorem, formalizes the tripartite pipeline architecture via high-level block diagrams (Fig 3.1), provides mathematical formulations "
        "of the core algorithms (Algorithms 3.1 and 3.2), outlines the internal class architecture across nine modular packages, and presents "
        "the conceptual entity-relationship data model (Fig 3.2) and relational schema specifications."
    )
    p(
        "• Chapter 4 - Implementation Details: Documents the engineering realization of the framework in Python 3.12, detailing dynamic "
        "Pydantic v2 code generation, regex parameter extraction, Gradio 6 reactive UI components, and five production showcase models. "
        "It provides comprehensive testing analysis across 110 automated pytest test cases and presents empirical latency benchmarks "
        "proving sub-5ms deterministic execution."
    )
    p(
        "• Chapter 5 - Conclusion and Future Scope: Synthesizes the core contributions of this work, summarizing empirical validation and "
        "architectural breakthroughs. It outlines forward-looking extensions including hierarchical multi-agent swarms, Server-Sent Events "
        "(SSE) streaming telemetry, automated active learning retraining loops, and hardware NPU acceleration."
    )
    p(
        "• Appendices & References: Appendix A provides representative production source code listings of core algorithms. Appendix B presents "
        "high-resolution user interface screenshots documenting live execution across all five operational views. A comprehensive list of "
        "academic literature citations concludes the report."
    )

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTER 2: LITERATURE SURVEY
    # ══════════════════════════════════════════════════════════════════════════
    chapter_title("CHAPTER 2\\nLITERATURE SURVEY")

    sub_heading("2.1 EXISTING SYSTEM")
    sub_sub_heading("2.1.1 Brief Overview of the System")
    p(
        "The conceptual genesis of autonomous LLM tool use traces back to the ReAct (Reasoning and Acting) paradigm formulated "
        "by Yao et al. [5], which demonstrated that interleaving reasoning traces (Thoughts) with domain-specific actions (Actions) "
        "and environmental feedback (Observations) significantly enhances multi-step problem solving. This paradigm was subsequently "
        "industrialized by open-source libraries such as LangChain [6], CrewAI [7], Microsoft Semantic Kernel [8], and AutoGen [9]."
    )
    p(
        "In these existing systems, external computational capabilities are integrated through function-calling wrappers. The LLM is "
        "provided with a system prompt detailing available tools, expressed as JSON Schema specifications. The language model generates "
        "a structured string indicating its chosen function and arguments. The host runtime intercepts this string, invokes the target "
        "function, appends the execution output to the conversational buffer, and reinvokes the language model to generate a natural "
        "language summary. While functional for basic utility scripts (such as web search or calendar lookups), this paradigm is ill-suited "
        "for statistical predictive machine learning models."
    )
    p(
        "Subsequent research expanded on ReAct by introducing planning-centric paradigms, most notably Plan-and-Solve prompting, Toolformer [3], "
        "and Reflexion architectures. In Plan-and-Solve architectures, an initial planner LLM generates a static sequence of actions (a directed "
        "acyclic graph of computational steps), which is subsequently executed sequentially by subordinate worker agents. In Reflexion "
        "architectures, agents maintain episodic memory buffers evaluating past failures to dynamically adjust future planning traces. "
        "Furthermore, systems such as Gorilla and ToolBench fine-tune language models specifically on API call syntax. However, all these "
        "evolutions share the identical foundational vulnerability: they treat external computational tools as unconstrained natural language "
        "generators or arbitrary API endpoints, rather than mathematically bounded, type-safe statistical operators."
    )
    p(
        "Contemporary multi-agent frameworks—most visibly CrewAI and AutoGen—have popularized conversational multi-agent "
        "patterns. In CrewAI, tasks are modeled as collaborative role-playing games between artificial personas (e.g., 'Senior Researcher', "
        "'Financial Analyst'). While compelling for creative writing or broad domain exploration, multi-agent conversational patterns induce "
        "severe token inflation. Agents exchange hundreds of conversational messages to perform basic feature lookups, exacerbating network "
        "latency and introducing multiple points of stochastic failure where numbers can be hallucinated at any conversational hop."
    )
    p(
        "Furthermore, contemporary enterprise MLOps architectures (such as Kubeflow, MLflow, and AWS SageMaker) approach machine learning "
        "from an entirely disconnected angle. These platforms package trained estimators into high-performance microservices exposed via gRPC "
        "or HTTP REST protocols. While they provide excellent model lifecycle management, versioning, and low-latency inference serving, "
        "they possess zero conversational capabilities. Bridging the gap between an MLOps serving cluster and a natural language user "
        "traditionally forces software engineers to build custom, ad-hoc wrapper services for every individual model, creating massive "
        "maintenance burdens and preventing scalable agentic automation."
    )

    sub_sub_heading("2.1.2 Purpose and Goals of the System")
    p(
        "The primary purpose of legacy agent frameworks is to augment generative models with external factual retrieval (Retrieval-Augmented "
        "Generation) and general API invocation. Their architectural goals prioritize broad language model compatibility, multi-agent role-playing "
        "metaphors, and developer flexibility over mathematical correctness, type safety, and runtime fault tolerance [10]. Existing systems "
        "assume that tool invocation is either binary (success or failure) and that the LLM possesses sufficient cognitive capacity to interpret "
        "arbitrary execution exceptions without specialized architectural intervention."
    )
    p(
        "In enterprise software engineering, this design philosophy creates critical vulnerabilities when interacting with machine learning models. "
        "The purpose of a predictive machine learning model is not generative conversation; it is mathematical estimation governed by strict "
        "statistical invariants. By treating an actuarial risk model or an oncological diagnostic classifier as just another arbitrary Python "
        "string-returning function, legacy frameworks sacrifice type safety, execution bounds, and auditability in pursuit of universal flexibility."
    )
    p(
        "From an enterprise compliance perspective, regulatory frameworks such as the NIST Artificial Intelligence Risk Management Framework "
        "(AI RMF 1.0) [13] and the European Union Artificial Intelligence Act strictly mandate traceability, mathematical reproducibility, "
        "and clear demarcations between probabilistic inferences and deterministic decisions. Legacy agent architectures, by blending tool "
        "executions and language model interpretations into a single undifferentiated dialogue transcript, violate these core compliance "
        "standards, exposing deploying organizations to substantial legal, financial, and reputational hazards."
    )
    p(
        "Moreover, in regulated financial environments governed by the Basel Committee on Banking Supervision (BCBS 239) and healthcare "
        "deployments regulated by the Health Insurance Portability and Accountability Act (HIPAA), algorithmic systems must demonstrate "
        "unimpeachable data lineage. When a credit decision is executed, auditors require an immutable cryptographic trace proving that "
        "the final interest rate was derived directly from an accredited logistic or random forest credit model rather than synthesized "
        "probabilistically by a generative model's sampling temperature. Legacy architectures, lacking visual and structural segregation, "
        "fail to provide the necessary evidential guarantees required by statutory compliance authorities."
    )

    sub_heading("2.2 SYSTEM ARCHITECTURE AND COMPONENTS")
    p(
        "In conventional architectures, the execution flow is organized around a tightly coupled monolithic prompt-evaluation loop. "
        "Every tool output is injected directly into the dialogue memory buffer as raw string tokens. The major components of existing architectures comprise:"
    )
    p(
        "1. The Prompt & Context Assembler: This component maintains an append-only conversational memory buffer. At each interaction turn, "
        "it concatenates the system instructions, the complete historical transcript of user and assistant messages, and the serializations "
        "of all registered tool definitions. As dialogue progresses, this monolithic text string expands quadratically, consuming precious "
        "token context windows and driving up operational inference costs [12]."
    )
    p(
        "2. The Autoregressive Inference Client: The assembled prompt context is dispatched via HTTP REST sockets to a remote cloud inference "
        "provider (e.g., OpenAI API). The remote server executes billions of matrix multiplications, returning either conversational prose "
        "or a JSON string indicating a tool invocation. Because this component relies on remote internet transport, network latency and "
        "token generation overhead dominate the execution timeline, typically consuming 2,000 to 5,000 milliseconds per turn."
    )
    p(
        "3. The Untyped Tool Dispatcher: The runtime inspects the returned string using standard JSON deserialization libraries. It matches "
        "the tool name against an in-memory dictionary of registered callable functions. Crucially, existing dispatchers perform no dynamic "
        "type verification; they pass the raw dictionary generated by the language model directly to the target Python function's arguments. "
        "If the LLM emits a string representation of a number ('2400.0') when the downstream machine learning estimator expects a numeric "
        "floating-point scalar, the dispatcher fails to coerce the data type, crashing the underlying algorithm."
    )
    p(
        "4. The Observation Re-Injection Loop: Once the tool executes, its return value (whether an integer, dictionary, or error traceback) "
        "is stringified and appended directly into the dialogue transcript as a new message. The agent runtime immediately loops back to "
        "subsystem 1, re-dispatching the entire historical context back to the language model. This creates a monolithic coupling where the "
        "LLM is granted ultimate authority to interpret, paraphrase, rewrite, or inadvertently alter the output of the computational tool."
    )
    p(
        "A critical architectural comparison arises when evaluating specialized inference serving systems such as NVIDIA Triton Inference Server, "
        "vLLM, TorchServe, and TensorFlow Serving against agentic frameworks. Triton and TorchServe are engineered for raw tensor throughput, "
        "dynamic batching, model concurrency, and hardware GPU acceleration, achieving microsecond inference latencies. However, they lack any "
        "natural language understanding, cognitive context, or dialogue state tracking. Conversely, agent frameworks excel at natural language "
        "interaction but completely lack model lifecycle governance, type validation, and execution isolation. Modular-Agent bridges this "
        "exact architectural chasm by implementing a decoupled orchestration tier that interfaces with compiled estimators while preserving "
        "the conversational benefits of autonomous language agents."
    )
    p(
        "Furthermore, contemporary inference servers operate in an isolated compute plane that requires client software to format tensors "
        "strictly according to binary buffer protocols (such as gRPC or KServe v2). While optimal for high-throughput batch pipelines, "
        "this design renders them inaccessible to non-technical human operators without complex middleware. Modular-Agent synthesizes the "
        "strengths of both paradigms: it leverages compiled in-memory Scikit-learn routines to achieve the sub-5-millisecond performance of "
        "dedicated inference servers while utilizing lightweight language model routers to provide the accessibility of conversational agents."
    )

    sub_heading("2.3 DATA MANAGEMENT")
    p(
        "Data management in legacy frameworks is notoriously unstructured. Arguments passed to tools are treated as arbitrary JSON objects. "
        "When an engineer builds an agent in LangChain or CrewAI, the data contracts governing tool inputs rely almost entirely on informal "
        "docstring text. For example, a developer might annotate a Python function with the docstring: 'Expects four features: square footage, "
        "bedrooms, bathrooms, and location rating.' The framework parses this docstring to construct an informal JSON Schema. However, "
        "no runtime Pydantic validation contracts are compiled."
    )
    p(
        "Consequently, when a compact language model processes a complex prompt, it frequently emits slight schema variations—such as passing "
        "'sqft' instead of 'square_footage', emitting an array of strings, or supplying null values for mandatory fields. In legacy runtimes, "
        "these variations trigger unhandled TypeError or ValueError exceptions, abruptly terminating the user session."
    )
    p(
        "Furthermore, data serialization across tool boundaries poses significant security and integrity challenges. In Python environments, "
        "statistical models are commonly persisted using pickle or joblib. Deserializing untrusted binaries (.pkl files) introduces severe "
        "remote code execution (RCE) vulnerabilities if malicious byte sequences are embedded in the serialized graph. Existing agent libraries "
        "provide zero security vetting or sandboxing for loaded model binaries. Moreover, legacy systems do not track schema evolution: "
        "if an updated Random Forest model expecting five features is placed in production replacing an older model that expected four features, "
        "the agent crashes at runtime without providing meaningful diagnostics or automated contract reconciliation."
    )
    p(
        "Another severe data management deficiency in existing frameworks is multi-turn state pollution. In long-running conversational sessions, "
        "previous tool outputs accumulate in the context window. When an agent invokes a tool ten turns into a dialogue, the prompt context "
        "contains dozens of historical numbers, dates, and scalar measurements. Generative models easily suffer from attention distraction, "
        "accidentally extracting historical parameters from turn 2 instead of the user's latest updates in turn 10. Without explicit state "
        "partitioning and ephemeral parameter extraction, legacy agents suffer from acute contextual crosstalk and silent data corruption."
    )

    sub_heading("2.4 SYSTEM PERFORMANCE")
    p(
        "The performance profile of existing tool-calling systems is severely bottlenecked by their reliance on monolithic, cloud-based "
        "language model round-trips. In typical multi-agent frameworks, completing a single analytical inquiry requires multiple sequential "
        "LLM calls: an initial planning call, a tool selection call, an observation interpretation call, and a final synthesis call. Each "
        "call incurs significant network round-trip latency (800 to 2,500 ms per API request) and high token generation overhead."
    )
    p(
        "Empirical benchmarks across enterprise deployments indicate that a multi-step query executed through LangGraph or CrewAI routinely "
        "consumes between 6,000 and 15,000 milliseconds, with token consumption exceeding 3,000 tokens per interaction. In stark contrast, "
        "the actual computational execution of a compiled Scikit-learn estimator consumes less than 5 milliseconds of CPU time. The ratio of "
        "overhead to meaningful computation exceeds 1000:1. Because existing frameworks lack local edge model optimization and intelligent "
        "single-turn cognitive routing, they are economically and computationally unviable for high-volume enterprise deployments."
    )
    p(
        "Moreover, multi-agent frameworks suffer from compounding failure rates. In probability theory, if a single agent step has a success "
        "probability p = 0.90, a four-step conversational chain exhibits a cumulative success probability of p^4 = (0.90)^4 = 0.656. In practice, "
        "this means over one-third of multi-agent transactions fail due to intermediate parsing errors, schema drift, or conversational drift. "
        "By eliminating superfluous intermediate multi-agent chatter and enforcing single-turn deterministic execution, Modular-Agent achieves "
        "dramatically superior throughput, reliability, and computational efficiency."
    )

    sub_heading("2.5 LIMITATIONS AND CHALLENGES")
    p(
        "A rigorous synthesis of literature and empirical testing reveals six major structural limitations in prevailing AI agent tool-calling frameworks:"
    )
    p(
        "1. Tight Coupling and Lack of Verification: Generative models and computational tools are merged into a single unstructured text stream. "
        "The language model is free to paraphrase, round, or alter the exact numerical outputs returned by statistical models, reintroducing "
        "hallucination into deterministic domains."
    )
    p(
        "2. Manual Boilerplate and High Maintenance: Integrating each new machine learning model requires writing bespoke schema dictionaries, "
        "argument parsers, and custom API routes. As enterprise model catalogs expand to hundreds of estimators, maintenance overhead becomes unsustainable."
    )
    p(
        "3. Fragility on Lightweight Offline Language Models (The Small Model Gap): Compact language models (<3B parameters, such as Qwen 2.5 0.5B or "
        "LLaMA 3.2 1B) frequently emit malformed JSON, unescaped quotation marks, trailing commas, or natural language preambles (e.g., 'Sure, here is "
        "the JSON:'). Existing runtimes possess no automated self-correction mechanisms; a single malformed brace immediately crashes the execution loop."
    )
    p(
        "4. Telemetry Data Exfiltration and Cleartext Secret Logging: Prevailing observability solutions (e.g., LangSmith) require transmitting "
        "complete dialogue transcripts and tool parameters to third-party cloud analytics platforms. Furthermore, default console logging "
        "mechanisms write unredacted string dumps to stdout, permanently exposing private API keys, bearer tokens, and confidential user data."
    )
    p(
        "5. Lack of Standardized Production Packaging: Existing agent frameworks provide no built-in mechanisms to export an operational "
        "agent pipeline into production-ready containerized architectures. Developers are left to manually configure Dockerfiles, resolve "
        "conflicting dependencies, configure ASGI web servers, and wire frontend dashboards from scratch."
    )
    p(
        "6. Prompt Injection and Parameter Tampering Vulnerabilities: Without strictly typed runtime boundary checks, existing agents are "
        "defenseless against prompt injection exploits where an adversary embeds instructions in natural language text that hijack tool argument "
        "extraction. For example, an attacker can manipulate medical dosages or credit parameters by exploiting untyped string-to-numeric casting. "
        "Modular-Agent resolves this vulnerability by introducing Pydantic schema validation as an unbypassable gateway before model execution."
    )
    p(
        "To provide a clear, rigorous comparison between legacy systems and the proposed architecture, Table 2.1 synthesizes these structural "
        "dimensions across five key evaluation metrics."
    )

    table_caption("Table 2.1 Comparative Analysis of Contemporary AI Agent Tool-Calling Frameworks")
    comp_tab = doc.add_table(rows=6, cols=5)
    comp_tab.alignment = WD_TABLE_ALIGNMENT.CENTER
    comp_headers = ["Feature / Dimension", "LangChain / LangGraph", "CrewAI", "Semantic Kernel", "Modular-Agent (Proposed)"]
    comp_data = [
        ["Model Ingestion", "Manual wrapper functions", "Manual Python tools", "Manual C#/Python plugins", "Automated Zero-Code (.joblib/REST)"],
        ["Execution Boundary", "Weak (Outputs blended in text)", "Weak (Outputs blended in text)", "Weak (Outputs blended in text)", "Strict (Dedicated Callout Box)"],
        ["Small LLM Self-Repair", "Throws raw parsing exceptions", "Loops recursively on errors", "Requires manual prompt tuning", "Bounded Retry + Regex Fallback"],
        ["Audit & Secret Masking", "Cloud SaaS (LangSmith)", "Unmasked stdout logs", "Basic OpenTelemetry", "Local ms Tracer + Recursive Masking"],
        ["Local Offline Operation", "Secondary (Cloud-first)", "Secondary (Cloud-first)", "Secondary (Cloud-first)", "Native Ollama First-Class Citizen"],
    ]
    for c_idx, h_text in enumerate(comp_headers):
        cell = comp_tab.rows[0].cells[c_idx]
        set_cell_background(cell, "1A1A1A")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p_c = cell.paragraphs[0]; p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_c = add_run(p_c, h_text, bold=True, size=9.5)
        r_c.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row in enumerate(comp_data):
        for c_idx, val in enumerate(row):
            cell = comp_tab.rows[r_idx + 1].cells[c_idx]
            if c_idx == 4:
                set_cell_background(cell, "F0F0F0")
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p_c = cell.paragraphs[0]; p_c.alignment = WD_ALIGN_PARAGRAPH.LEFT
            add_run(p_c, val, bold=(c_idx == 4 or c_idx == 0), size=9.0)
'''
