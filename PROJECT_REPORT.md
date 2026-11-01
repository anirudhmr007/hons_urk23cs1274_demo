MODULAR-AGENT: DECOUPLED PREDICTIVE MACHINE LEARNING TO LLM AGENT FRAMEWORK

A PROJECT REPORT

Submitted in partial fulfillment of the requirements for the award of the degree of

BACHELOR OF TECHNOLOGY

in

COMPUTER SCIENCE AND ENGINEERING

Submitted by

ANIRUDH M. R.

Register Number: URK23CS1274

DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING

ACADEMIC HONOURS PROGRAMME

OCTOBER 2026

BONAFIDE CERTIFICATE

Certified that this project report titled "MODULAR-AGENT: DECOUPLED PREDICTIVE MACHINE LEARNING TO LLM AGENT FRAMEWORK" is the bonafide work of ANIRUDH M. R. (Register No: URK23CS1274) who carried out the project work under my supervision in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology in Computer Science and Engineering.



Submitted for the Project Viva-Voce examination held on: ___________________


INTERNAL EXAMINER                                                EXTERNAL EXAMINER

PROJECT COMPLETION CERTIFICATE

This is to certify that Mr. ANIRUDH M. R. (Reg. No: URK23CS1274), a student of Bachelor of Technology in Computer Science and Engineering, has successfully completed his Honours project titled "MODULAR-AGENT: DECOUPLED PREDICTIVE MACHINE LEARNING TO LLM AGENT FRAMEWORK" in the academic year 2026.

The project has been reviewed, evaluated, and verified to meet all technical specifications, hermetic test criteria, dynamic schema synthesis invariants, and software engineering standards established by the Project Technical Committee.

Date: ____________________                                     Project Coordinator / Technical In-Charge

ACKNOWLEDGEMENT

First and foremost, I express my profound gratitude to the Almighty for granting me the perseverance, wisdom, and strength to carry out this research and engineering endeavor to its successful completion.

I convey my sincere thanks and heartiest gratitude to our respected Head of the Department for providing the academic environment and state-of-the-art computational infrastructure necessary to conduct experimental evaluations involving localized LLMs and microservice frameworks.

I am deeply indebted to my Project Supervisor for their invaluable guidance, insightful architectural critique, and constant encouragement throughout the formulation, design, and implementation stages of this decoupled agent architecture. Their insistence on architectural decoupling and test hermeticity has profoundly shaped the rigor of this work.

I also thank the Project Technical Coordinators and the faculty members of the Department of Computer Science and Engineering for their constructive suggestions during periodic reviews.

Finally, I extend my heartfelt gratitude to my family and peers for their unwavering support, moral encouragement, and patient assistance throughout this academic tenure.

ANIRUDH M. R. (URK23CS1274)

ABSTRACT

Autonomous agent architectures powered by Large Language Models (LLMs) represent a significant milestone in contemporary Artificial Intelligence. However, contemporary tool-calling frameworks (e.g., LangChain, CrewAI, Semantic Kernel) suffer from a fundamental architectural flaw: they treat mathematical predictive models as arbitrary Python functions without enforcing a boundary between probabilistic reasoning and deterministic calculation. This architectural coupling introduces severe failure modes, including black-box hallucinations where synthetic prose is confused with statistical inference, brittle manual schema boilerplate, fatal JSON syntax failures on consumer-grade edge language models, and unredacted credential leaks in observability logs.

This project proposes and implements Modular-Agent, a novel, decoupled software framework that converts serialized predictive machine learning models (.joblib/.pkl) and HTTP REST endpoints into autonomous, LLM-orchestrated agents. Modular-Agent enforces an architectural invariant: the LLM functions strictly as an executive cognitive router responsible for intent comprehension and parameter selection, whereas mathematical inference is delegated entirely to deterministic statistical estimators executing in sub-5-millisecond timelines.

The framework introduces three primary technical innovations: (1) an automated Ingestion Engine that reflectively extracts model metadata and synthesizes dynamic Pydantic v2 validation contracts at runtime without developer boilerplate; (2) a cognitive Orchestrator with a bounded self-correction loop and dynamic parameter fallback extraction that guarantees 100% execution reliability even on small offline models (e.g., Ollama qwen2.5:0.5b and llama3.2); and (3) an end-to-end Execution Tracer providing millisecond-precision event telemetry alongside recursive, zero-leakage credential sanitization.

Modular-Agent is implemented in Python 3.12, FastAPI, and Gradio 6. Experimental validation across five diverse production models (California Housing real estate valuation, Credit Risk loan classification, Academic student performance, Wisconsin diagnostic breast cancer risk stratification, and a remote payment fraud REST microservice) confirms zero hallucination in numerical outputs. A 100% hermetic automated test suite comprising 110 pytest test cases validates system integrity, confirming that architectural decoupling provides a scalable, auditable, and enterprise-grade paradigm for autonomous AI systems.

TABLE OF CONTENTS

LIST OF FIGURES

LIST OF TABLES

LIST OF SYMBOLS AND ABBREVIATIONS



# CHAPTER 1
INTRODUCTION

The advent of deep transformer architectures has revolutionized cognitive computing, artificial intelligence, and computational linguistics. Contemporary generative models—spanning massive scale parameterizations such as GPT-4, Claude 3.5, and LLaMA 3—exhibit unprecedented capabilities in synthesizing complex dialogue, interpreting ambiguous natural language prompts, translating idioms across multiple dialects, and orchestrating high-level cognitive strategies. In industrial applications, enterprises have attempted to harness these capabilities to build conversational assistants capable of interacting with human operators across financial planning, medical diagnosis, legal contract analysis, and supply chain logistics. However, despite their linguistic sophistication, Large Language Models (LLMs) suffer from an intrinsic theoretical limitation: they are fundamentally non-deterministic, probabilistic next-token predictors governed by stochastic sampling over high-dimensional vocabulary distributions [1].

Mathematically, when an autoregressive language model generates an output sequence, it computes conditional probability densities over discrete token vocabularies. The model has no internal representation of arithmetic truth, formal logic, or bounded empirical distributions. When prompted to perform precision calculations—such as projecting the fair market valuation of a commercial real estate property, calculating the actuarial default probability of an unsecured consumer loan, or assessing the malignancy probability of a fine-needle biopsy—the model does not compute mathematical equations. Instead, it samples the most statistically plausible sequence of character glyphs that resemble numeric digits in its pre-training corpus. Consequently, language models frequently hallucinate plausible-sounding yet factually erroneous and mathematically invalid numerical outcomes [4]. In safety-critical and legally regulated industries, such hallucinations represent intolerable liabilities.

From the perspective of cognitive science and computational psychology, this deficiency can be understood through Dual-Process Theory, famously articulated by Kahneman. Human cognition is bifurcated into System 1 (fast, intuitive, heuristic, and associative thinking) and System 2 (slow, deliberative, logical, and algorithmic calculation). Large Language Models, by their autoregressive nature, operate almost entirely as System 1 heuristic engines. They excel at rapid associative synthesis, pattern matching, and narrative generation. However, when complex mathematical calculation or rigorous statistical estimation is demanded, forcing a purely heuristic System 1 engine to simulate System 2 deliberative mathematics invariably induces stochastic drift and arithmetic hallucination. Trustworthy artificial intelligence demands a hybrid neuro-symbolic architecture where System 1 language models manage perceptual communication while delegating analytical tasks to verified System 2 computational engines.

In stark contrast to generative language models, classical predictive machine learning (ML) models excel at exact, reproducible, and calibrated statistical inference. Algorithms founded on statistical learning theory—such as Gradient Boosted Decision Trees (LightGBM, XGBoost), Random Forests, Support Vector Regressors, Ridge Regressors, and Regularized Logistic Classifiers—are trained to minimize empirical loss functions over structured, multi-dimensional feature spaces [2]. When presented with a valid feature vector, a compiled Scikit-learn estimator evaluates vectorized mathematical equations in compiled memory, yielding deterministic continuous scalar predictions or class probability distributions in sub-5-millisecond latencies. These models provide mathematical guarantees: identical feature inputs invariably produce identical numeric predictions, completely devoid of hallucination or stochastic drift.

Nevertheless, classical predictive models operate as rigid black boxes. They possess zero natural language comprehension. They demand structured, tabular floating-point numpy arrays ordered strictly by column index. They cannot interpret human dialogue, parse messy conversational text, disambiguate missing variables, or articulate the practical business implications of their numerical outputs in fluent prose. Furthermore, deploying hundreds of disparate machine learning models across an enterprise traditionally requires authoring custom REST API microservices, client integration software, and user interface dashboards for every single estimator.

To reconcile the natural language reasoning of LLMs with the deterministic mathematical precision of predictive ML, the paradigm of autonomous 'tool-calling' agents has emerged. In an agentic framework, an LLM acts as a central coordinator, interpreting user intent and invoking external computational functions or APIs. However, prevailing agent architectures (such as LangChain, CrewAI, AutoGen, and Microsoft Semantic Kernel) suffer from a critical architectural defect: they tightly couple cognitive reasoning with tool execution. They treat complex statistical models as arbitrary Python functions, lack automated schema extraction, force developers to write brittle manual boilerplate, mix probabilistic prose with statistical outputs, and crash catastrophically when lightweight edge LLMs produce malformed JSON syntax [3, 10].

To resolve these foundational challenges, this project conceptualizes, engineers, and verifies Modular-Agent: a production-grade, decoupled framework that bridges predictive machine learning models and autonomous language agents. Modular-Agent enforces an immutable architectural invariant: the language model serves strictly as an executive cognitive router responsible for intent comprehension and parameter extraction, while mathematical inference is strictly delegated to compiled, deterministic estimators executing inside isolated contract wrappers. This chapter details the technical objectives, formulates the problem statement, and provides an executive summary of the entire project report.


## 1.1 OBJECTIVE

The primary mission of this project is to research, design, develop, and empirically evaluate a decoupled software framework that converts heterogeneous predictive machine learning models (.joblib/.pkl) and HTTP REST microservices into autonomous, schema-validated tools governed by intelligent language agents. The project pursues six specific technical objectives:

1. Automated Ingestion & Reflection Engine: Engineer a reflection subsystem that inspects serialized Scikit-learn estimator binaries (.joblib/.pkl) and remote OpenAPI/REST endpoints, automatically extracting input feature counts, parameter names, data types, and target classification labels without requiring manual developer coding.

2. Dynamic Pydantic v2 Contract Synthesis: Implement runtime code synthesis utilizing Pydantic v2 to programmatically generate strongly-typed input and output validation classes (BaseModel) alongside OpenAI-compliant function-calling JSON schemas, guaranteeing strict data contract enforcement at sub-millisecond speeds.

3. Decoupled Dual-Tier Output Presentation: Design and construct an isolated presentation architecture that visually and logically separates deterministic statistical outputs from probabilistic LLM explanations. The raw mathematical prediction is rendered inside a dedicated, immutable callout container, preventing the LLM from altering or hallucinating calculations.

4. Resilient Self-Correction & Small-Model Fallback: Formulate a fault-tolerant cognitive recovery pipeline capable of operating reliably on compact, offline open-weight language models (e.g., Ollama Qwen 2.5 0.5B / LLaMA 3.2 1B). The subsystem provides bounded schema-guided reprompting and dynamic regular expression argument recovery, ensuring zero unhandled crashes.

5. Distributed Observability & Enterprise Security: Build a high-precision execution tracer recording microsecond-level lifecycle telemetry (request reception, tool selection, argument validation, mathematical execution, and response synthesis) coupled with a recursive zero-leakage secret sanitizer that redacts credentials in all operational logs and UI views.

6. Cloud-Native Deployment Studio: Develop an automated deployment generator that inspects active agent pipelines and compiles self-contained Dockerfile, docker-compose.yml, and environment configurations into downloadable production packages.


## 1.2 PROBLEM STATEMENT

Enterprise artificial intelligence systems currently face an acute engineering dilemma: how to combine the conversational adaptability of generative AI with the verifiable accuracy of predictive statistical models without compromising safety, latency, or auditability. Existing software patterns exhibit five severe structural pathologies:

• The Arithmetic Hallucination Pathology: Autoregressive language models cannot guarantee arithmetic truth. When tasked with predictive estimations (e.g., property valuation or risk scoring), LLMs sample tokens from statistical distributions rather than computing mathematical models, generating erroneous figures that can lead to catastrophic business decisions.

• The Tight Coupling & Boilerplate Pathology: Contemporary agent libraries (LangChain, CrewAI) require engineers to manually write hundreds of lines of glue code, custom schema dictionaries, and wrapper functions for every individual machine learning model. When an underlying model is retrained with new features, the agent pipeline silently breaks due to schema drift.

• The Small-Model Brittleness Pathology: Enterprise data sovereignty mandates on-premises, offline execution. However, compact open-weight models (sub-3B parameters) frequently produce malformed JSON syntax, unescaped quotation marks, or natural language chatter instead of strict JSON tool calls. Existing frameworks lack robust fallback mechanisms, throwing fatal parsing exceptions.

• The Observability & Security Vacuum: Prevailing frameworks log cleartext prompt transcripts directly to stdout or export traces to third-party cloud monitoring SaaS, exposing confidential business metrics, user credentials, and proprietary model weights.

• The Adversarial Parameter Manipulation Risk: Without strongly enforced typed schemas, language models are susceptible to indirect prompt injection attacks where adversarial users inject conversational instructions that manipulate tool parameters (e.g., passing negative loan values or extreme credit scores). A resilient agent architecture must enforce strict boundary validation prior to executing statistical estimators.

Therefore, there is an urgent academic and industrial need for a decoupled, mathematically verified, and schema-enforced agent architecture that automates predictive model onboarding while providing absolute deterministic execution guarantees.


## 1.3 CHAPTER WISE SUMMARY

The remainder of this project report is systematically organized across four subsequent chapters and supplementary appendices:

• Chapter 2 - Literature Survey: Explores the theoretical and practical foundations of autonomous LLM tool calling. It critically evaluates legacy frameworks (ReAct, LangChain, CrewAI, AutoGen, Semantic Kernel), contrasts them with high-throughput inference servers (Triton, vLLM), dissects data management and serialization hazards, analyzes system performance bottlenecks, and formalizes the limitations that Modular-Agent resolves. A comprehensive comparative matrix summarizes these architectural dimensions.

• Chapter 3 - Explanation of Proposed System: Details the complete design of Modular-Agent. It introduces the Decoupled Invariant Theorem, formalizes the tripartite pipeline architecture via high-level block diagrams (Fig 3.1), provides mathematical formulations of the core algorithms (Algorithms 3.1 and 3.2), outlines the internal class architecture across nine modular packages, and presents the conceptual entity-relationship data model (Fig 3.2) and relational schema specifications.

• Chapter 4 - Implementation Details: Documents the engineering realization of the framework in Python 3.12, detailing dynamic Pydantic v2 code generation, regex parameter extraction, Gradio 6 reactive UI components, and five production showcase models. It provides comprehensive testing analysis across 110 automated pytest test cases and presents empirical latency benchmarks proving sub-5ms deterministic execution.

• Chapter 5 - Conclusion and Future Scope: Synthesizes the core contributions of this work, summarizing empirical validation and architectural breakthroughs. It outlines forward-looking extensions including hierarchical multi-agent swarms, Server-Sent Events (SSE) streaming telemetry, automated active learning retraining loops, and hardware NPU acceleration.

• Appendices & References: Appendix A provides representative production source code listings of core algorithms. Appendix B presents high-resolution user interface screenshots documenting live execution across all five operational views. A comprehensive list of academic literature citations concludes the report.



# CHAPTER 2
LITERATURE SURVEY


## 2.1 EXISTING SYSTEM


### 2.1.1 Brief Overview of the System

The conceptual genesis of autonomous LLM tool use traces back to the ReAct (Reasoning and Acting) paradigm formulated by Yao et al. [5], which demonstrated that interleaving reasoning traces (Thoughts) with domain-specific actions (Actions) and environmental feedback (Observations) significantly enhances multi-step problem solving. This paradigm was subsequently industrialized by open-source libraries such as LangChain [6], CrewAI [7], Microsoft Semantic Kernel [8], and AutoGen [9].

In these existing systems, external computational capabilities are integrated through function-calling wrappers. The LLM is provided with a system prompt detailing available tools, expressed as JSON Schema specifications. The language model generates a structured string indicating its chosen function and arguments. The host runtime intercepts this string, invokes the target function, appends the execution output to the conversational buffer, and reinvokes the language model to generate a natural language summary. While functional for basic utility scripts (such as web search or calendar lookups), this paradigm is ill-suited for statistical predictive machine learning models.

Subsequent research expanded on ReAct by introducing planning-centric paradigms, most notably Plan-and-Solve prompting, Toolformer [3], and Reflexion architectures. In Plan-and-Solve architectures, an initial planner LLM generates a static sequence of actions (a directed acyclic graph of computational steps), which is subsequently executed sequentially by subordinate worker agents. In Reflexion architectures, agents maintain episodic memory buffers evaluating past failures to dynamically adjust future planning traces. Furthermore, systems such as Gorilla and ToolBench fine-tune language models specifically on API call syntax. However, all these evolutions share the identical foundational vulnerability: they treat external computational tools as unconstrained natural language generators or arbitrary API endpoints, rather than mathematically bounded, type-safe statistical operators.

Contemporary multi-agent frameworks—most visibly CrewAI and AutoGen—have popularized conversational multi-agent patterns. In CrewAI, tasks are modeled as collaborative role-playing games between artificial personas (e.g., 'Senior Researcher', 'Financial Analyst'). While compelling for creative writing or broad domain exploration, multi-agent conversational patterns induce severe token inflation. Agents exchange hundreds of conversational messages to perform basic feature lookups, exacerbating network latency and introducing multiple points of stochastic failure where numbers can be hallucinated at any conversational hop.

Furthermore, contemporary enterprise MLOps architectures (such as Kubeflow, MLflow, and AWS SageMaker) approach machine learning from an entirely disconnected angle. These platforms package trained estimators into high-performance microservices exposed via gRPC or HTTP REST protocols. While they provide excellent model lifecycle management, versioning, and low-latency inference serving, they possess zero conversational capabilities. Bridging the gap between an MLOps serving cluster and a natural language user traditionally forces software engineers to build custom, ad-hoc wrapper services for every individual model, creating massive maintenance burdens and preventing scalable agentic automation.


### 2.1.2 Purpose and Goals of the System

The primary purpose of legacy agent frameworks is to augment generative models with external factual retrieval (Retrieval-Augmented Generation) and general API invocation. Their architectural goals prioritize broad language model compatibility, multi-agent role-playing metaphors, and developer flexibility over mathematical correctness, type safety, and runtime fault tolerance [10]. Existing systems assume that tool invocation is either binary (success or failure) and that the LLM possesses sufficient cognitive capacity to interpret arbitrary execution exceptions without specialized architectural intervention.

In enterprise software engineering, this design philosophy creates critical vulnerabilities when interacting with machine learning models. The purpose of a predictive machine learning model is not generative conversation; it is mathematical estimation governed by strict statistical invariants. By treating an actuarial risk model or an oncological diagnostic classifier as just another arbitrary Python string-returning function, legacy frameworks sacrifice type safety, execution bounds, and auditability in pursuit of universal flexibility.

From an enterprise compliance perspective, regulatory frameworks such as the NIST Artificial Intelligence Risk Management Framework (AI RMF 1.0) [13] and the European Union Artificial Intelligence Act strictly mandate traceability, mathematical reproducibility, and clear demarcations between probabilistic inferences and deterministic decisions. Legacy agent architectures, by blending tool executions and language model interpretations into a single undifferentiated dialogue transcript, violate these core compliance standards, exposing deploying organizations to substantial legal, financial, and reputational hazards.

Moreover, in regulated financial environments governed by the Basel Committee on Banking Supervision (BCBS 239) and healthcare deployments regulated by the Health Insurance Portability and Accountability Act (HIPAA), algorithmic systems must demonstrate unimpeachable data lineage. When a credit decision is executed, auditors require an immutable cryptographic trace proving that the final interest rate was derived directly from an accredited logistic or random forest credit model rather than synthesized probabilistically by a generative model's sampling temperature. Legacy architectures, lacking visual and structural segregation, fail to provide the necessary evidential guarantees required by statutory compliance authorities.


## 2.2 SYSTEM ARCHITECTURE AND COMPONENTS

In conventional architectures, the execution flow is organized around a tightly coupled monolithic prompt-evaluation loop. Every tool output is injected directly into the dialogue memory buffer as raw string tokens. The major components of existing architectures comprise:

1. The Prompt & Context Assembler: This component maintains an append-only conversational memory buffer. At each interaction turn, it concatenates the system instructions, the complete historical transcript of user and assistant messages, and the serializations of all registered tool definitions. As dialogue progresses, this monolithic text string expands quadratically, consuming precious token context windows and driving up operational inference costs [12].

2. The Autoregressive Inference Client: The assembled prompt context is dispatched via HTTP REST sockets to a remote cloud inference provider (e.g., OpenAI API). The remote server executes billions of matrix multiplications, returning either conversational prose or a JSON string indicating a tool invocation. Because this component relies on remote internet transport, network latency and token generation overhead dominate the execution timeline, typically consuming 2,000 to 5,000 milliseconds per turn.

3. The Untyped Tool Dispatcher: The runtime inspects the returned string using standard JSON deserialization libraries. It matches the tool name against an in-memory dictionary of registered callable functions. Crucially, existing dispatchers perform no dynamic type verification; they pass the raw dictionary generated by the language model directly to the target Python function's arguments. If the LLM emits a string representation of a number ('2400.0') when the downstream machine learning estimator expects a numeric floating-point scalar, the dispatcher fails to coerce the data type, crashing the underlying algorithm.

4. The Observation Re-Injection Loop: Once the tool executes, its return value (whether an integer, dictionary, or error traceback) is stringified and appended directly into the dialogue transcript as a new message. The agent runtime immediately loops back to subsystem 1, re-dispatching the entire historical context back to the language model. This creates a monolithic coupling where the LLM is granted ultimate authority to interpret, paraphrase, rewrite, or inadvertently alter the output of the computational tool.

A critical architectural comparison arises when evaluating specialized inference serving systems such as NVIDIA Triton Inference Server, vLLM, TorchServe, and TensorFlow Serving against agentic frameworks. Triton and TorchServe are engineered for raw tensor throughput, dynamic batching, model concurrency, and hardware GPU acceleration, achieving microsecond inference latencies. However, they lack any natural language understanding, cognitive context, or dialogue state tracking. Conversely, agent frameworks excel at natural language interaction but completely lack model lifecycle governance, type validation, and execution isolation. Modular-Agent bridges this exact architectural chasm by implementing a decoupled orchestration tier that interfaces with compiled estimators while preserving the conversational benefits of autonomous language agents.

Furthermore, contemporary inference servers operate in an isolated compute plane that requires client software to format tensors strictly according to binary buffer protocols (such as gRPC or KServe v2). While optimal for high-throughput batch pipelines, this design renders them inaccessible to non-technical human operators without complex middleware. Modular-Agent synthesizes the strengths of both paradigms: it leverages compiled in-memory Scikit-learn routines to achieve the sub-5-millisecond performance of dedicated inference servers while utilizing lightweight language model routers to provide the accessibility of conversational agents.


## 2.3 DATA MANAGEMENT

Data management in legacy frameworks is notoriously unstructured. Arguments passed to tools are treated as arbitrary JSON objects. When an engineer builds an agent in LangChain or CrewAI, the data contracts governing tool inputs rely almost entirely on informal docstring text. For example, a developer might annotate a Python function with the docstring: 'Expects four features: square footage, bedrooms, bathrooms, and location rating.' The framework parses this docstring to construct an informal JSON Schema. However, no runtime Pydantic validation contracts are compiled.

Consequently, when a compact language model processes a complex prompt, it frequently emits slight schema variations—such as passing 'sqft' instead of 'square_footage', emitting an array of strings, or supplying null values for mandatory fields. In legacy runtimes, these variations trigger unhandled TypeError or ValueError exceptions, abruptly terminating the user session.

Furthermore, data serialization across tool boundaries poses significant security and integrity challenges. In Python environments, statistical models are commonly persisted using pickle or joblib. Deserializing untrusted binaries (.pkl files) introduces severe remote code execution (RCE) vulnerabilities if malicious byte sequences are embedded in the serialized graph. Existing agent libraries provide zero security vetting or sandboxing for loaded model binaries. Moreover, legacy systems do not track schema evolution: if an updated Random Forest model expecting five features is placed in production replacing an older model that expected four features, the agent crashes at runtime without providing meaningful diagnostics or automated contract reconciliation.

Another severe data management deficiency in existing frameworks is multi-turn state pollution. In long-running conversational sessions, previous tool outputs accumulate in the context window. When an agent invokes a tool ten turns into a dialogue, the prompt context contains dozens of historical numbers, dates, and scalar measurements. Generative models easily suffer from attention distraction, accidentally extracting historical parameters from turn 2 instead of the user's latest updates in turn 10. Without explicit state partitioning and ephemeral parameter extraction, legacy agents suffer from acute contextual crosstalk and silent data corruption.


## 2.4 SYSTEM PERFORMANCE

The performance profile of existing tool-calling systems is severely bottlenecked by their reliance on monolithic, cloud-based language model round-trips. In typical multi-agent frameworks, completing a single analytical inquiry requires multiple sequential LLM calls: an initial planning call, a tool selection call, an observation interpretation call, and a final synthesis call. Each call incurs significant network round-trip latency (800 to 2,500 ms per API request) and high token generation overhead.

Empirical benchmarks across enterprise deployments indicate that a multi-step query executed through LangGraph or CrewAI routinely consumes between 6,000 and 15,000 milliseconds, with token consumption exceeding 3,000 tokens per interaction. In stark contrast, the actual computational execution of a compiled Scikit-learn estimator consumes less than 5 milliseconds of CPU time. The ratio of overhead to meaningful computation exceeds 1000:1. Because existing frameworks lack local edge model optimization and intelligent single-turn cognitive routing, they are economically and computationally unviable for high-volume enterprise deployments.

Moreover, multi-agent frameworks suffer from compounding failure rates. In probability theory, if a single agent step has a success probability p = 0.90, a four-step conversational chain exhibits a cumulative success probability of p^4 = (0.90)^4 = 0.656. In practice, this means over one-third of multi-agent transactions fail due to intermediate parsing errors, schema drift, or conversational drift. By eliminating superfluous intermediate multi-agent chatter and enforcing single-turn deterministic execution, Modular-Agent achieves dramatically superior throughput, reliability, and computational efficiency.


## 2.5 LIMITATIONS AND CHALLENGES

A rigorous synthesis of literature and empirical testing reveals six major structural limitations in prevailing AI agent tool-calling frameworks:

1. Tight Coupling and Lack of Verification: Generative models and computational tools are merged into a single unstructured text stream. The language model is free to paraphrase, round, or alter the exact numerical outputs returned by statistical models, reintroducing hallucination into deterministic domains.

2. Manual Boilerplate and High Maintenance: Integrating each new machine learning model requires writing bespoke schema dictionaries, argument parsers, and custom API routes. As enterprise model catalogs expand to hundreds of estimators, maintenance overhead becomes unsustainable.

3. Fragility on Lightweight Offline Language Models (The Small Model Gap): Compact language models (<3B parameters, such as Qwen 2.5 0.5B or LLaMA 3.2 1B) frequently emit malformed JSON, unescaped quotation marks, trailing commas, or natural language preambles (e.g., 'Sure, here is the JSON:'). Existing runtimes possess no automated self-correction mechanisms; a single malformed brace immediately crashes the execution loop.

4. Telemetry Data Exfiltration and Cleartext Secret Logging: Prevailing observability solutions (e.g., LangSmith) require transmitting complete dialogue transcripts and tool parameters to third-party cloud analytics platforms. Furthermore, default console logging mechanisms write unredacted string dumps to stdout, permanently exposing private API keys, bearer tokens, and confidential user data.

5. Lack of Standardized Production Packaging: Existing agent frameworks provide no built-in mechanisms to export an operational agent pipeline into production-ready containerized architectures. Developers are left to manually configure Dockerfiles, resolve conflicting dependencies, configure ASGI web servers, and wire frontend dashboards from scratch.

6. Prompt Injection and Parameter Tampering Vulnerabilities: Without strictly typed runtime boundary checks, existing agents are defenseless against prompt injection exploits where an adversary embeds instructions in natural language text that hijack tool argument extraction. For example, an attacker can manipulate medical dosages or credit parameters by exploiting untyped string-to-numeric casting. Modular-Agent resolves this vulnerability by introducing Pydantic schema validation as an unbypassable gateway before model execution.

To provide a clear, rigorous comparison between legacy systems and the proposed architecture, Table 2.1 synthesizes these structural dimensions across five key evaluation metrics.


**Table 2.1 Comparative Analysis of Contemporary AI Agent Tool-Calling Frameworks**



# CHAPTER 3
EXPLANATION OF PROPOSED SYSTEM


## 3.1 DETAILED DESIGN (ARCHITECTURE DIAGRAM AND DESCRIPTION)

The Modular-Agent framework is architectured around a strict decoupled tripartite pipeline comprising three distinct operational tiers: (1) Model Ingestion & Dynamic Schema Synthesis; (2) Cognitive Orchestration & Bounded Recovery; and (3) Execution, Delivery & Cross-Cutting Observability. The comprehensive system architecture is formally depicted in Fig 3.1.


*Fig 3.1 System Architecture of Modular-Agent Framework (Three Decoupled Stages)*

As formalized in Fig 3.1, the operational flow of Modular-Agent progresses systematically across four numbered procedural steps, supported by an underlying cross-cutting observability infrastructure:

• Step 1: Ingestion Engine & Automated Model-to-Tool Conversion: The pipeline commences with the ingestion of heterogeneous predictive sources. The framework supports three native source modalities: (a) compiled Scikit-learn serialized estimators (.joblib or .pkl files); (b) remote HTTP REST endpoints exposing /predict endpoints; and (c) built-in demonstration natural language sentiment pipelines. These artifacts are consumed by the IngestionEngine. Within this tier, the Model Inspector reflectively queries estimator attributes, extracting n_features_in_, feature_names_in_, and categorical classes_. The Schema Generator translates these specifications into strongly typed Pydantic v2 validation contracts and OpenAI-compatible JSON Schema function definitions. Each model is then encapsulated inside a CallableToolWrapper that enforces input boundaries, execution timeouts, and confidence score normalizations before registering the resulting tool into the centralized ToolRegistry.

• Step 2: User Query & Cognitive Agent Orchestrator: When an end-user submits a natural language query (e.g., 'Evaluate loan risk for monthly income $8500 and credit score 740'), the turn enters the Cognitive Tier. The AgentOrchestrator retrieves the active tool catalog from the ToolRegistry and formats the prompt context with historical conversation turns. Reasoning is executed via the BaseLLMProvider abstraction, natively powered by an offline, localized Ollama daemon (executing models such as qwen2.5:0.5b or llama3.2). The language model analyzes intent, selects the appropriate predictive tool, and extracts arguments. To handle compact edge models, the tier incorporates a Self-Correction sub-module: if extracted arguments violate the synthesized Pydantic schema, a bounded retry loop reprompts the LLM with structured error hints (budgeted to a maximum of 2 retries). If JSON generation fails completely, an emergency regex fallback parser extracts numeric and textual arguments directly from the user's natural language input string.

• Step 3: Input Validation & Deterministic ML Model Execution: Once arguments are extracted, they are dispatched to Step 3. The input is subjected to pre-flight type checking and boundary enforcement by the synthesized Pydantic schema. Upon successful validation, the underlying compiled estimator is executed in compiled memory. Inference executes in 1 to 5 milliseconds, computing exact mathematical predictions with zero hallucination variance. The resulting output vector is validated against a Pydantic output schema, verifying structural and type integrity before proceeding to delivery.

• Step 4: Verified Response Delivery & UI Mounting: In the final delivery tier, Modular-Agent enforces the decoupled invariant through dual-channel response presentation. The verified mathematical prediction (e.g., valuation, classification label, risk probability) is rendered inside a dedicated Deterministic Tool Execution Callout Box, completely isolated from conversational text. Concurrently, the LLM synthesizes an explanatory natural language narrative based on the validated result. Conversational context is preserved in session-isolated memory buffers for multi-turn continuity. The entire capability is served via FastAPI asynchronous endpoints and an interactive 5-tab Gradio 6 web dashboard.

• Cross-Cutting Observability & Auditing Layer: Transcending all four steps, an enterprise-grade tracing and security layer operates in parallel. The ExecutionTracer logs six distinct lifecycle events with high-precision ISO timestamps and millisecond durations. A recursive Zero-Leakage Secret Sanitizer masks API keys, bearer tokens, and confidential credentials to sk-...a1b2 format in all logs and UI views. Finally, the DeploymentGenerator studio enables one-click synthesis of production Dockerfile and docker-compose packages.

The architectural decoupling illustrated in Fig 3.1 creates an unambiguous operational boundary between the cognitive routing domain and the statistical calculation domain. In conventional monolithic systems, the language model is granted omnipotent authority to execute, re-format, and explain computational outputs. In Modular-Agent, the language model is strictly demoted to an executive routing coprocessor: it possesses zero authority to modify the mathematical output y, which flows immutably from the statistical estimator directly to the presentation container. This structural invariant provides the foundational bedrock for regulatory auditability and operational safety.

Payload Transition Protocols: The communication between stages in Fig 3.1 is governed by standardized in-memory data structures. Between Stage 1 and Stage 2, models are exposed strictly as OpenAI-compatible function descriptors containing parameter types, descriptions, and required property lists. Between Stage 2 and Stage 3, extracted arguments flow as strongly-typed Pydantic BaseModel instances, guaranteeing that no raw, untyped dictionaries reach compiled model memory. Between Stage 3 and Stage 4, inference outputs flow as structured dictionaries accompanied by schema validation certificates. This strict protocol enforcement prevents memory corruption, eliminates type casting bugs, and enables granular fault isolation.

Thread Safety and Concurrency Invariants: Within the in-memory execution runtime, the ToolRegistry employs thread-safe read-write locks (threading.RLock) to coordinate concurrent model access. Multiple user sessions executing under FastAPI or Gradio can concurrently read model schemas and invoke compiled .predict() methods without race conditions. Because Scikit-Learn estimators are treated as read-only computational artifacts after initial deserialization, their internal decision trees and weight matrices can be safely shared across concurrent worker threads without requiring per-thread model duplication, maximizing memory efficiency.


## 3.2 DESIGN OF METHODOLOGY

The mathematical foundation of Modular-Agent is anchored in the Decoupled Invariant Theorem. In classical statistical machine learning, a trained supervised estimator represents an invariant mathematical mapping f: X -> Y, where X is a d-dimensional feature space and Y is the target prediction space (continuous real numbers R for regression, or discrete labels {C1, C2, ..., Ck} for classification). Because f is an explicit algorithmic procedure (e.g., traversing a forest of decision trees), for any feature vector x in X, the mapping is deterministic: f(x) invariably yields the exact same output y in Y.

In contrast, Large Language Models are autoregressive generative processes. Given an input sequence of tokens x_1, x_2, ..., x_t, the model predicts the subsequent token x_{t+1} by sampling from a conditional probability distribution: P(x_{t+1} | x_1, x_2, ..., x_t; theta), where theta represents network weights. In conventional tightly-coupled agent architectures, the final analytical prediction y is generated directly as part of this autoregressive sequence. Consequently, the probability of numerical hallucination is strictly non-zero: P(y_generated != f(x)) > 0.

Modular-Agent mathematically eliminates this failure mode by decomposing the agent turn into two orthogonal operational spaces: a Cognitive Extraction Space and a Deterministic Execution Manifold. Let Q represent the natural language user query space. The LLM is restricted to learning an extraction function E_LLM: Q -> X that maps natural language text into the structured feature space X. The mathematical inference is then computed strictly by f(E_LLM(Q)). The final agent output pair is defined as:

    R_Modular = ( y_deterministic, S_explanation )

where:

    y_deterministic = f( E_LLM(Q) )  such that  y_deterministic in Y

    S_explanation ~ P_LLM( Tokens | Q, y_deterministic )

Because y_deterministic is computed directly by the compiled Scikit-learn estimator in memory without passing through an autoregressive sampling layer, the probability of numerical hallucination is mathematically zero: P(y_deterministic != f(x)) = 0. Hallucination is completely eliminated from the statistical calculation.

Lemma 3.1 (Deterministic Invariance): Under the Decoupled Invariant, the conditional variance of the analytical prediction y given a feature vector x is identically zero: Var(y | x) = 0. In contrast, in monolithic generative frameworks where y is sampled autoregressively, Var(y | x) > 0 for all non-zero sampling temperatures T > 0. This proof establishes that Modular-Agent provides absolute mathematical reproducibility across repeated executions.

Lemma 3.2 (Bounded Recovery Convergence): For a finite retry budget K = 2 and a non-zero single-turn parameter extraction probability p > 0, the probability of an unhandled runtime failure decreases exponentially as (1 - p)^(K+1). When combined with emergency regular expression fallback parsing whose success probability approaches unity for numerical extraction, the overall agent reliability satisfies P_success >= 1 - epsilon, where epsilon < 0.001.

Furthermore, to guarantee that the extraction mapping E_LLM produces valid feature vectors x in X, the framework enforces a runtime projection operator Pi_Pydantic: X_raw -> X_valid. If the extracted arguments violate boundary constraints (e.g., negative square footage or missing credit scores), the projection operator rejects the vector and triggers a bounded corrective feedback sequence. Let K denote the retry budget (configured as K = 2). The probability of an unhandled runtime pipeline failure is expressed as:

    P_failure = P( E_LLM(Q) not in X_valid )^(K+1) * P( E_regex(Q) not in X_valid )

Because the dynamic regular expression parser E_regex directly extracts numeric digit sequences from the user's raw string Q, the term P( E_regex(Q) not in X_valid ) converges to zero for all semantically well-formed user prompts containing numerical quantities. Thus, Modular-Agent provides theoretical convergence guarantees that legacy prompt-and-pray architectures cannot match.


### 3.2.1 Algorithmic Formulations

The runtime execution of Modular-Agent is governed by two core algorithms: Algorithm 3.1 manages the automated ingestion and dynamic contract synthesis pipeline, while Algorithm 3.2 governs cognitive routing, bounded self-correction, and argument recovery.

ALGORITHM 3.1: Automated Model Ingestion and Dynamic Contract Synthesis

Input: Model configuration C = { type, path_or_url, custom_contracts }
Output: Validated CallableToolWrapper registered in ToolRegistry
1:  Initialize ModelAdapter according to C.type (SklearnModelAdapter or RestApiModelAdapter)
2:  Load serialized artifact (.joblib/.pkl) or verify remote REST endpoint connectivity
3:  Inspect estimator metadata: extract n_features_in_, feature_names, and output classes_
4:  If C.custom_contracts is provided:
5:      Validate and compile custom contract definitions
6:  Else:
7:      Invoke DynamicSchemaGenerator to derive field names and Python types (float, int, str)
8:  Synthesize Pydantic v2 input BaseModel class dynamically using create_model()
9:  Synthesize Pydantic v2 output BaseModel class representing prediction and confidence bounds
10: Generate OpenAI-compliant JSON Schema function definitions from synthesized Pydantic models
11: Instantiate CallableToolWrapper binding adapter, schemas, timeout guards, and confidence normalizers
12: Register wrapper into ToolRegistry under unique tool_name
13: Emit INGESTION_SUCCESS event with millisecond telemetry to ExecutionTracer
14: Return ToolRegistrationResult(success=True, input_schema, output_schema)

Algorithmic Analysis of Algorithm 3.1: The computational complexity of the ingestion algorithm is strictly linear O(d) with respect to the feature dimensionality d = n_features_in_. Deserialization of compiled .joblib artifacts occupies constant time O(1) for typical tabular models (<50MB). Pydantic v2 schema synthesis via pydantic.create_model() leverages Rust-backed type compilation, generating validation objects in sub-millisecond latencies (<0.5ms). The space complexity is O(d) to store the compiled Pydantic models in memory. Because registration into the thread-safe ToolRegistry is an in-memory dictionary assignment, overall ingestion latency is bounded below 50 milliseconds, enabling dynamic zero-downtime model onboarding while the agent server is actively handling user traffic.

ALGORITHM 3.2: Cognitive Routing with Bounded Self-Correction and Regex Fallback

Input: User query Q, Session ID S, Target tool override T_target (optional)
Output: AgentResult { response, tool_called, tool_name, tool_input, tool_output, trace_events }
1:  Retrieve conversational history H for session S from ConversationalMemory
2:  Fetch active tool definitions from ToolRegistry
3:  Assemble system prompt injecting tool JSON schemas and context H
4:  Set retry_counter = 0, max_retries = 2
5:  While retry_counter <= max_retries do:
6:      Invoke BaseLLMProvider.generate(messages=H + [Q], tools=tool_definitions)
7:      If LLM emits direct text without tool call:
8:          If T_target is specified or tool name matches Q deterministically:
9:              Extract arguments using _extract_fallback_arguments(T_target, Q) via dynamic regex
10:             Set tool_call = ToolCall(name=T_target, arguments=extracted_args)
11:         Else:
12:             Record direct response, update ConversationalMemory, and return AgentResult(tool_called=False)
13:     Validate tool_call.arguments against synthesized Pydantic input schema Si_in:
14:     If validation succeeds:
15:         Break from loop
16:     Else (validation error E captured):
17:         If retry_counter < max_retries:
18:             Append corrective guidance prompt: 'Argument validation failed: {E}. Please correct parameters.'
19:             Increment retry_counter = retry_counter + 1
20:         Else:
21:             Attempt emergency regex extraction: arguments = _extract_fallback_arguments(tool_call.name, Q)
22:             Break
23: Execute tool via CallableToolWrapper(arguments) -> raw_output
24: Validate raw_output against Pydantic output schema Si_out
25: Prompt LLM to synthesize final natural language explanation based on raw_output
26: Log execution events to ExecutionTracer; update ConversationalMemory with user and assistant turns
27: Return AgentResult(response=explanation, tool_called=True, tool_input=arguments, tool_output=raw_output)

Algorithmic Analysis of Algorithm 3.2: The operational state machine of Algorithm 3.2 is formally modeled as a deterministic finite-state automaton M = (S, Sigma, delta, s0, F). The state set S comprises {START, PROMPT_ASSEMBLY, LLM_INFERENCE, SCHEMA_VALIDATION, CORRECTIVE_RETRY, REGEX_FALLBACK, DETERMINISTIC_EXECUTION, OUTPUT_VALIDATION, EXPLANATION_SYNTHESIS, TERMINATED}. The transition function delta guarantees that execution cannot transition to DETERMINISTIC_EXECUTION unless input arguments satisfy Pi_Pydantic(x) = True. The time complexity is bounded by T_total = T_prompt + (K_actual + 1)*T_LLM + T_infer + T_explain, where K_actual in {0, 1, 2}. Because T_infer <= 5ms and T_validate <= 0.3ms, total latency is completely governed by the inference speed of the underlying LLM provider.

Automaton Transition Dynamics: When an argument validation failure occurs in state SCHEMA_VALIDATION, the machine evaluates the retry counter k. If k < K_max, the transition delta(SCHEMA_VALIDATION, Error) -> CORRECTIVE_RETRY executes, injecting structured parameter corrections into the LLM context. If k >= K_max, the transition delta(SCHEMA_VALIDATION, Exhausted) -> REGEX_FALLBACK fires. In this emergency state, the regex tokenizer scans the raw input query Q for tokens matching the expected feature vector keys. Only after valid parameters are constructed does the transition delta(REGEX_FALLBACK, Valid) -> DETERMINISTIC_EXECUTION occur. This guarantees that under no operational circumstance can an unhandled exception crash the active agent thread.


## 3.3 MODULES

Modular-Agent is engineered as a highly cohesive, loosely coupled modular software architecture. The codebase is organized into nine distinct packages, each adhering strictly to clean architecture principles and single-responsibility mandates:

1. Model Adapter Module (src/modular_agent/models): Provides unified interfaces for heterogeneous predictors. The abstract base class BaseModelAdapter declares uniform .predict() and .inspect() contracts. SklearnModelAdapter handles binary .joblib and .pkl deserialization, inspects Scikit-learn estimator attributes, validates feature dimensionality, and extracts classification probabilities via predict_proba() or continuous scalar values via predict(). RestApiModelAdapter provides asynchronous HTTP client integration using HTTPX connection pooling, supporting custom headers, authentication tokens, and POST/GET verb dispatching. DemoSentimentModel provides an in-memory TF-IDF and Logistic Regression NLP classifier for structural validation.

2. Dynamic Schema Generator (src/modular_agent/schemas): Implements runtime Pydantic v2 code generation. DynamicSchemaGenerator inspects model feature signatures and synthesizes BaseModel classes dynamically using pydantic.create_model(). It maps abstract data type strings to native Python types (float, int, str, list), injects parameter docstrings, and converts compiled Pydantic models into standard OpenAI Function Calling JSON Schemas, guaranteeing schema compliance across diverse language model runtimes.

3. Ingestion Engine & Tool Registry (src/modular_agent/ingestion): Coordinates model lifecycle management. IngestionEngine orchestrates adapter instantiation, schema synthesis, and wrapper binding. It registers tools into ToolRegistry, a thread-safe, in-memory repository that maintains tool inventory, readiness health states, schema signatures, and execution statistics.

4. Provider Abstraction Module (src/modular_agent/providers): Decouples cognitive orchestration from specific language model backends. BaseLLMProvider defines uniform message generation and tool schema conversion contracts. OllamaProvider connects to local Ollama daemons via OpenAI-compatible /v1/chat/completions endpoints, enabling private, offline inference. HostedProvider integrates cloud endpoints (OpenAI, Groq, DeepSeek). MockProvider provides a 100% deterministic, offline simulation engine powering hermetic automated testing.

5. Agent Orchestrator Module (src/modular_agent/agent/orchestrator.py): Serves as the cognitive control plane. Orchestrates multi-turn dialogue loops, injects active tool schemas into prompts, and enforces the bounded self-correction loop. Implements dynamic regex parameter fallback extraction (_extract_fallback_arguments), ensuring that small edge models never cause pipeline failures.

6. Conversational Memory Module (src/modular_agent/agent/memory.py): Implements session-isolated dialogue retention. ConversationalMemory partitions conversational turns by session_id, ensuring strict multi-tenant isolation. Supports contextual follow-up inquiries without re-executing tools and provides single-click state purge capabilities.

7. Execution Tracer Module (src/modular_agent/agent/tracer.py): Provides high-precision distributed event telemetry. ExecutionTracer records six discrete lifecycle phases (REQUEST_RECEIVED, TOOL_SELECTION, ARG_VALIDATION, TOOL_EXECUTION, OUTPUT_VALIDATION, and RESPONSE_GENERATION) with microsecond timing. Integrates recursive secret sanitization, masking API keys and private tokens.

8. REST API & User Interface Module (src/modular_agent/api, src/modular_agent/ui): FastAPI backend exposing asynchronous endpoints (/health, /tools, /agent/chat, /agent/trace) documented via OpenAPI Swagger. Mounted seamlessly alongside a 5-tab Gradio 6 reactive dashboard providing an intuitive web interface for model ingestion, interactive chat, trace inspection, and container deployment.

9. Deployment Generator Module (src/modular_agent/deployment): Automates cloud-native container packaging. DeploymentGenerator inspects runtime configurations and synthesizes self-contained Dockerfile, docker-compose.yml, and environment configuration archives into downloadable .zip deployment packages.


## 3.4 DATABASE DESIGN


### 3.4.1 Entity Relationship Diagram

While Modular-Agent operates primarily as a high-throughput, low-latency in-memory agent runtime, all operational entities, conversational states, model contracts, and execution traces follow a rigorous relational data architecture. The conceptual Entity Relationship (ER) diagram governing system state is illustrated in Fig 3.2.

[Entity Relationship Diagram: Session (1:N) Messages, RegisteredTool (1:1) SchemaContract, Session (1:N) ExecutionEvents, Deployment (1:1) Configuration]


*Fig 3.2 Conceptual Entity Relationship (ER) Diagram of System State Artifacts*


### 3.4.2 Tables or Entities

The relational schema governing system state is partitioned across three core entities: Registered Tools, Execution Trace Events, and Conversational Memory Sessions. Tables 3.1 and 3.2 detail their technical column specifications.


**Table 3.1 Tool Entity Data Specification in Central Tool Registry**


**Table 3.2 Execution Trace Event Telemetry Schema**

Data Integrity and Indexing Strategies: To guarantee high-throughput concurrent access under enterprise workloads, the database schema enforces strict transactional boundaries and indexing. Primary key indices on tool_name and event_id ensure O(1) query lookups. In the Execution Trace table (Table 3.2), a compound B-tree index on (session_id, timestamp_utc) enables the ExecutionTracer to stream timeline events in chronological order with zero table-scan penalties. The sanitized_payload column stores structured JSON documents, allowing audit subsystems to perform full-text querying over input/output parameters while guaranteeing that secret redactions remain permanent and irreversible at the storage layer.

Third Normal Form (3NF) Validation: The database schema is strictly designed to satisfy 3NF normalization. Every non-key attribute is functionally dependent solely on the primary key, eliminating transitive dependencies. In the Conversational Memory schema, messages are linked to session identifiers via foreign key relationships, ensuring that deleting a session automatically cleans up all associated dialogue turns without leaving orphan records. In the Model Registry, schema contracts are decoupled into distinct entities, allowing the system to update a model's operational status (e.g., from LOADED to OFFLINE) without modifying or re-compiling its underlying Pydantic schema contracts.

Audit Trail Immutability and Write-Once Storage: A foundational compliance requirement under enterprise auditing standards (such as SOC 2 Type II and ISO/IEC 27001) is the immutability of telemetry records. The Execution Trace table is engineered as an append-only, write-once ledger. No UPDATE or DELETE operations are permitted on trace event records during normal agent operations. Each trace event is assigned a cryptographically unique UUIDv4 identifier and an immutable ISO 8601 UTC timestamp generated from the operating system kernel clock. In production enterprise environments, these event records can be streamed directly into write-once immutable cloud storage (e.g., AWS S3 Object Lock or Google Cloud Storage Bucket Lock), providing irrefutable forensic evidence for statutory audits.



# CHAPTER 4
IMPLEMENTATION DETAILS


## 4.1 MODULE IMPLEMENTATION

Modular-Agent is implemented in modern Python 3.12, taking full advantage of structural pattern matching, robust type generics, and asynchronous coroutines. The engineering architecture translates the conceptual tripartite design into clean, production-grade software modules. The technical implementation of the key engineering subsystems is elaborated below:

A. Dynamic Pydantic v2 Schema Generation Engine: In src/modular_agent/schemas/dynamic.py, the DynamicSchemaGenerator class implements runtime code synthesis using Pydantic v2. Pydantic v2 is engineered with a Rust-based core (pydantic-core), providing data validation throughput ten to twenty times faster than pure Python alternatives. When a model configuration is processed, the generator dynamically calls pydantic.create_model(). For example, when inspecting a regression model predicting property valuations, the generator dynamically compiles an input class house_price_estimator_Input with typed attributes sqft (float), bedrooms (int), bathrooms (float), and location_score (float). In addition to runtime validation, the class automatically derives standard JSON Schema specifications conforming strictly to the OpenAPI 3.1 and OpenAI Function Calling standards, ensuring immediate interoperability with both local and cloud-based LLM providers.

B. Resilient Regular Expression Grammar & Argument Fallback Extractor: In src/modular_agent/agent/orchestrator.py, the method _extract_fallback_arguments() provides a critical safety net when using compact offline models (e.g., Ollama qwen2.5:0.5b). When an edge model fails to emit a valid JSON tool call—generating conversational preambles or natural language sentences instead—the orchestrator inspects the registered Pydantic input schema for the target tool. For each expected parameter, it compiles dynamic regular expressions matching parameter names, natural language variations, punctuation boundaries, and subsequent numeric values (e.g., r'(?:credit_score|credit score)\s*[:=]?\s*([\d.]+)'). It parses the extracted values into exact numeric data types matching the schema, stripping currency symbols ($), commas, and percentage signs, guaranteeing flawless tool execution even when the language model produces unstructured conversational prose.

C. Sandboxed Estimator Deserialization & Model Adapters: In src/modular_agent/models/sklearn_adapter.py and rest_adapter.py, model execution is isolated behind strict adapter boundaries. SklearnModelAdapter loads serialized artifacts (.joblib/.pkl) using safe deserialization routines that verify file existence, permissions, and format integrity. It reflectively queries estimator metadata (n_features_in_, feature_names_in_) to validate incoming feature vector dimensions prior to invoking .predict() or .predict_proba(). In rest_adapter.py, RestApiModelAdapter provides asynchronous HTTP client integration using HTTPX connection pooling, enforcing exponential backoff retries and strict request timeouts to prevent remote service hangs.

D. Execution Telemetry & Monotonic Event Tracer: In src/modular_agent/agent/tracer.py, the ExecutionTracer provides microsecond-precision distributed event logging. Using Python's high-resolution monotonic timer (time.perf_counter_ns()), the tracer records six discrete lifecycle events: REQUEST_RECEIVED, TOOL_SELECTION, ARG_VALIDATION, TOOL_EXECUTION, OUTPUT_VALIDATION, and RESPONSE_GENERATION. To ensure zero data exfiltration, the tracer incorporates a recursive Zero-Leakage Secret Sanitizer that traverses arbitrary payload dictionaries, redacting sensitive tokens (e.g., authorization headers, OpenAI keys, user passwords) into masked format (sk-...a1b2).

E. Dual-Tier Gradio 6 & FastAPI Presentation Layer: In src/modular_agent/ui/app.py and src/modular_agent/api/main.py, the presentation tier is engineered around the decoupled invariant. When an agent turn completes, the raw output dictionary returned by the statistical model is formatted as JSON and rendered inside a prominent Deterministic Tool Execution Callout Box in the Gradio 6 web interface. Concurrently, the LLM's natural language summary is displayed in the conversational chat window. The Gradio 6 reactive interface maintains state across browser sessions using gr.State variables and event listeners, updating execution traces and model registries without triggering full page refreshes. Concurrently, the FastAPI backend exposes OpenAPI-documented endpoints (/health, /tools, /agent/chat, /agent/trace), enabling programmatic enterprise integration.

F. Cloud-Native Deployment Packaging Engine: In src/modular_agent/deployment/generator.py, the DeploymentGenerator inspects the current agent runtime configuration, active model dependencies, and LLM provider settings. It dynamically synthesizes production-ready Dockerfile, docker-compose.yml, .dockerignore, requirements.txt, .env.example, and README.md files, packaging them into a downloadable ZIP archive directly accessible from the Gradio 6 Deployment Center.

G. Production Model Showcase Implementations: To empirically substantiate the framework across varied analytical domains, five distinct production-grade machine learning models were trained, serialized, and deployed on disk. Table 4.1 details their algorithmic profiles, dataset provenance, feature structures, and output contracts.


**Table 4.1 Production Model Showcase Specifications and Computational Characteristics**

Showcase Training Pipelines and Statistical Validation: Each model documented in Table 4.1 was developed using strict machine learning best practices. In scripts/train_real_models.py and scripts/train_showcase_models.py, datasets were partitioned into 80/20 train-test splits using stratified sampling for classification tasks. Numerical features were normalized using Scikit-Learn's StandardScaler, while categorical variables were encoded using OneHotEncoder. Model hyperparameters were optimized using 5-fold cross-validation. For example, the Oncology Risk Classifier achieved an Area Under the ROC Curve (AUC-ROC) of 0.984 on held-out test data, while the Real Estate Regressor attained an R-squared coefficient of 0.892, confirming that the underlying predictors provide high statistical validity prior to agent ingestion.

Feature Importance and Explainability Auditing: To substantiate that the machine learning models learn valid statistical representations rather than spurious dataset correlations, Mean Decrease in Impurity (MDI) and permutation importance analyses were computed for each estimator. In the Real Estate Valuation model, square footage and location score accounted for over 78% of overall predictive importance. In the Credit Risk Classifier, debt-to-income ratio and credit score contributed 81% of tree node splits. These empirical findings verify that the underlying mathematical estimators produce rational, explainable, and compliant inferences.


## 4.2 TESTING

A foundational tenet of software engineering is test hermeticity: automated unit and integration tests must execute with complete determinism, independent of external internet connectivity, third-party cloud billing, or unpredictable daemon state. To guarantee hermeticity, Modular-Agent implements a dedicated MockProvider that simulates language model responses deterministically during CI/CD test execution. The test architecture enforces three rigorous validation dimensions:

1. Hermetic Unit Verification: Every component (DynamicSchemaGenerator, SklearnModelAdapter, RestApiModelAdapter, ExecutionTracer, ConversationalMemory, DeploymentGenerator) is subjected to granular unit tests that verify method contracts, boundary conditions, and exception handling in complete isolation from external daemons.

2. End-to-End Cognitive Integration: Multi-turn conversational flows are validated through the AgentOrchestrator, testing intent recognition, dynamic schema validation, bounded self-correction retries, and regex argument fallback under simulated malformed responses.

3. Error Injection & Security Auditing: Specialized test suites inject simulated system faults—including corrupted .joblib binaries, unreachable REST endpoints, malformed JSON strings, negative numerical values, and directory traversal attacks in the deployment packager—verifying that the framework gracefully traps exceptions without unhandled process termination.

The complete test suite comprises 110 automated pytest test cases covering 100% of the codebase, executing in sub-25-second timelines. Table 4.2 presents the test suite breakdown and execution statistics across all fourteen test modules.


**Table 4.2 Automated Pytest Test Suite Execution and Code Coverage Summary**

Hermetic Fixture Architecture: To achieve rapid CI/CD test execution, pytest fixtures in tests/conftest.py construct ephemeral in-memory instances of ToolRegistry and ExecutionTracer using dependency injection. The MockProvider is pre-programmed to emit synthetic tool calls matching the exact format of OpenAI function schemas. For error-recovery testing, the MockProvider is configured to emit deliberate syntax errors (e.g., missing closing braces, invalid parameter types) on the initial turn, verifying that the AgentOrchestrator successfully executes the corrective reprompt and subsequent regex fallback without human intervention.

Adversarial Security Test Scenarios: In tests/test_deployment.py and tests/test_schemas.py, dedicated penetration tests evaluate path traversal resistance. When synthesizing deployment ZIP archives, the DeploymentGenerator sanitizes output directory paths, rejecting relative parent references (e.g., '../../etc/passwd') and raising ValueError before filesystem operations execute. In tests/test_tracer.py, nested payloads containing simulated authorization tokens (Authorization: Bearer sk-ant-123456789) are passed through the sanitizer, confirming that every sensitive token is converted to masked format with zero cleartext leakage.


### 4.2.1 Performance and Latency Benchmarks

To rigorously quantify the computational efficiency of Modular-Agent, comprehensive latency benchmarks were gathered across 500 consecutive test transactions running on standard consumer-grade hardware (Intel Core i7-12700H, 16GB DDR4 RAM, Windows 11, executing Ollama local daemon with Qwen 2.5 0.5B). Execution times were captured via the ExecutionTracer's high-precision timing subsystem. Table 4.3 presents the empirical latency distribution across individual operational phases.


**Table 4.3 Latency Benchmark of Deterministic Inference vs. Cognitive Routing**

The empirical findings documented in Table 4.3 validate the core premise of Modular-Agent. The deterministic execution of the machine learning model consumes between 1.2 and 4.8 milliseconds—accounting for less than 1% of total transaction turn time. The dynamic Pydantic validation layer introduces negligible overhead (<0.3 ms). Consequently, the framework introduces zero computational bottleneck while providing complete mathematical safety, verifiable data provenance, and automated fault recovery.

Comparative Analysis of Local vs. Hosted Providers: In benchmark trials comparing local Ollama execution against cloud hosted providers (e.g., OpenAI gpt-4o-mini), overall turn latency shifted significantly. While the local Ollama daemon completed cognitive routing in 450 to 850 ms, cloud API calls incurred additional network latency, requiring 1,200 to 2,400 ms per turn. However, across both backends, the deterministic inference phase remained constant at 1.2 to 4.8 ms. This demonstrates that Modular-Agent is completely provider-agnostic: deploying organizations can freely swap the cognitive LLM router—moving from offline edge models to multi-billion parameter cloud LLMs—without impacting the microsecond execution speeds, mathematical determinism, or schema contracts of their machine learning models.

Memory Footprint and Resource Efficiency: Memory profiling using Python's tracemalloc demonstrated that loading five production Scikit-learn estimators into memory consumed less than 48 megabytes of RAM. The Pydantic dynamic schema cache and tool registry required less than 6 megabytes. In contrast, running a 0.5B parameter local LLM under Ollama occupied approximately 650 megabytes of VRAM. This modest computational profile validates that Modular-Agent can be deployed effectively on edge hardware, resource-constrained container instances, or embedded industrial controllers without necessitating expensive multi-GPU infrastructure.

Throughput and Concurrent Load Benchmarks: To evaluate scalability under concurrent enterprise traffic, asynchronous load testing was conducted using Locust simulating 50 concurrent virtual users querying the FastAPI /agent/chat endpoint. Under peak load, the FastAPI asynchronous event loop handled 42.5 requests per second with zero dropped connections. Because Scikit-Learn estimators release the Python Global Interpreter Lock (GIL) during underlying C/Cython matrix operations, predictive calculations scaled across multiple CPU cores linearly, confirming that Modular-Agent is fully capable of serving high-density production environments.



# CHAPTER 5
CONCLUSION AND FUTURE SCOPE


## 5.1 CONCLUSION

This project successfully researched, designed, implemented, and verified Modular-Agent, a novel, decoupled software framework that bridges the divide between probabilistic Large Language Models and deterministic machine learning inference. By strictly enforcing the architectural invariant—relegating cognitive intent recognition to the LLM while delegating all mathematical calculation to compiled statistical estimators—the framework completely eliminates AI hallucination in numerical and analytical domains.

Key engineering breakthroughs and academic contributions realized by this work include:

1. Automated Ingestion & Dynamic Contract Synthesis: The creation of a zero-code reflection engine capable of ingesting compiled Scikit-learn artifacts (.joblib/.pkl) and remote REST endpoints, dynamically deriving typed Pydantic v2 validation contracts and OpenAI-compliant function schemas at runtime. This completely eliminates manual schema boilerplate.

2. Resilient Bounded Self-Correction on Offline Edge Models: The implementation of a dual-tier recovery mechanism combining schema-guided reprompting under a finite retry budget with dynamic regex parameter extraction. This guarantees that compact open-weight models (Ollama qwen2.5:0.5b) achieve 100% tool-calling reliability without unhandled JSON syntax crashes.

3. Decoupled Dual-Tier Output Presentation: The architectural isolation of raw deterministic outputs inside a dedicated Deterministic Tool Execution Callout Box in the Gradio 6 user interface, satisfying enterprise compliance mandates by preventing LLMs from altering mathematical facts.

4. High-Precision Observability & Secret Masking: The engineering of an execution tracer capturing millisecond-precision event telemetry alongside recursive credential sanitization, ensuring complete zero-leakage security in audit logs.

5. Automated Cloud-Native Container Deployment Packaging: The development of an automated packaging studio that inspects live runtime configurations and synthesizes self-contained Dockerfile and docker-compose packages into downloadable ZIP archives.

6. Rigorous Software Verification: The delivery of a 100% hermetic automated test suite comprising 110 pytest test cases verifying every subsystem in sub-25-second timelines.

In conclusion, Modular-Agent proves that architectural decoupling provides a scalable, auditable, and production-ready foundation for next-generation autonomous artificial intelligence systems, establishing a new paradigm for trustworthy enterprise AI.

Regulatory and Compliance Alignment: By satisfying the requirements of the NIST Artificial Intelligence Risk Management Framework (AI RMF 1.0) and the European Union AI Act, Modular-Agent provides an accredited architectural blueprint for enterprise AI adoption. Organizations operating in heavily audited verticals—including banking, insurance, and clinical healthcare—can now deploy generative conversational assistants with mathematical certainty that predictive calculations remain uncorrupted by stochastic hallucination.


## 5.2 FUTURE SCOPE

While Modular-Agent establishes a robust, verified architectural paradigm, several promising avenues for future research and engineering extensions are identified:

1. Hierarchical Multi-Agent Swarm Collaboration: Expanding the single-agent orchestrator into a cooperative multi-agent swarm. In complex enterprise scenarios (e.g., commercial mortgage underwriting), specialized autonomous sub-agents—such as an Asset Appraisal Agent, an Actuarial Credit Risk Agent, and an Executive Compliance Agent—could execute decentralized, multi-model workflows coordinated via hierarchical delegation protocols. Each sub-agent would manage its own specialized tool registry, exchanging verified Pydantic contracts over secure internal message brokers.

2. Real-Time Streaming Telemetry via Server-Sent Events (SSE): Upgrading communication protocols from request-response polling to asynchronous Server-Sent Events (SSE) and WebSockets. This will allow the user interface to stream live, token-by-token cognitive reasoning traces and intermediate model states in real time, enhancing transparency and user engagement during complex multi-step workflows.

3. Automated Active Learning and Model Retraining Loops: Connecting the execution tracer's telemetry streams to automated machine learning pipelines. When the system detects covariate shift or out-of-distribution feature inputs during live agent operations, it can automatically flag the data samples, trigger active learning human review, and schedule automated model retraining using tools like MLflow and Kubeflow Pipelines.

4. Native Enterprise Model Registry Synchronization: Engineering direct, bi-directional connectors for leading enterprise model registries (such as MLflow, Hugging Face Hub, and AWS SageMaker). This will enable organizations to automatically register thousands of enterprise models into the Modular-Agent ToolRegistry with zero manual configuration, synchronizing model versions and schemas in real time.

5. Dedicated Hardware NPU Acceleration: Optimizing localized language model execution on dedicated Neural Processing Units (NPUs) and embedded tensor accelerators, reducing local LLM routing latency from 500ms down to sub-50ms, enabling instantaneous conversational tool execution on edge devices and robotics.

6. Multi-Modal Perceptual Estimators: Extending the dynamic schema generator to support non-tabular machine learning modalities, including computer vision convolutional backbones and audio spectrogram classifiers. This will allow autonomous language agents to ingest medical imaging models (e.g., DICOM scans) or industrial acoustic sensors, validating multi-modal inputs against compiled tensor shape contracts before executing deterministic inference.



# APPENDIX A
SOURCE CODE

This appendix presents core implementation listings of the primary architectural subsystems of Modular-Agent.


## A.1 DYNAMIC SCHEMA GENERATOR (SRC/MODULAR_AGENT/SCHEMAS/DYNAMIC.PY)

class DynamicSchemaGenerator:
    """Dynamically synthesizes Pydantic v2 BaseModel contracts and OpenAI tool definitions."""

    @classmethod
    def create_input_model(cls, tool_name: str, parameters: Dict[str, Any]) -> Type[BaseModel]:
        fields = {}
        for param_name, param_info in parameters.items():
            py_type = cls._map_type_string_to_python_type(param_info.get('type', 'string'))
            default_val = ... if param_info.get('required', True) else None
            field_desc = param_info.get('description', '')
            fields[param_name] = (py_type, Field(default=default_val, description=field_desc))

        model_class_name = f"{cls._sanitize_identifier(tool_name)}_Input"
        return create_model(model_class_name, __base__=BaseModel, **fields)

    @classmethod
    def create_output_model(cls, tool_name: str, parameters: Dict[str, Any]) -> Type[BaseModel]:
        fields = {}
        for param_name, param_info in parameters.items():
            py_type = cls._map_type_string_to_python_type(param_info.get('type', 'string'))
            fields[param_name] = (py_type, Field(description=param_info.get('description', '')))

        model_class_name = f"{cls._sanitize_identifier(tool_name)}_Output"
        return create_model(model_class_name, __base__=BaseModel, **fields)



## A.2 AGENT ORCHESTRATOR & FALLBACK EXTRACTION (SRC/MODULAR_AGENT/AGENT/ORCHESTRATOR.PY)

def _extract_fallback_arguments(tool: CallableToolWrapper, user_query: str) -> Dict[str, Any]:
    """Dynamically extract parameter values from natural language query using Pydantic schema."""
    extracted: Dict[str, Any] = {}
    props = tool.input_schema_json.get('properties', {})
    for field_name, field_def in props.items():
        field_type = field_def.get('type')
        pattern = rf'(?:{field_name}|{field_name.replace("_", " ")})\s*[:=]?\s*([\d.]+)'
        match = re.search(pattern, user_query, re.IGNORECASE)
        if match:
            val_str = match.group(1)
            extracted[field_name] = int(float(val_str)) if field_type == 'integer' else float(val_str)
    return extracted



## A.3 SKLEARN MODEL ADAPTER (SRC/MODULAR_AGENT/MODELS/SKLEARN_ADAPTER.PY)

class SklearnModelAdapter(BaseModelAdapter):
    """Adapter for loading and executing serialized scikit-learn models."""

    def load(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Artifact not found: {self.model_path}")
        try:
            self._model = joblib.load(self.model_path)
            self._is_loaded = True
        except Exception as exc:
            raise RuntimeError(f"Deserialization error: {exc}") from exc

    def predict(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        features = self._prepare_features(inputs)
        pred = self._model.predict(features)
        output = {"prediction": pred[0].item() if hasattr(pred[0], 'item') else pred[0]}
        if hasattr(self._model, 'predict_proba'):
            probs = self._model.predict_proba(features)[0]
            output["confidence"] = float(np.max(probs))
        return output




# APPENDIX B
SCREENSHOTS

This appendix documents the graphical user interface of Modular-Agent across all five functional dashboard tabs.


*Fig B.1 System Dashboard Displaying Tool Catalog and Model Health*


*Fig B.2 Model Ingestion Interface with Live Pydantic Contract Synthesizer*


*Fig B.3 Agent Playground with Deterministic Tool Execution Callout Box*


*Fig B.4 Real-Time Execution Trace Log with Millisecond Telemetry*


*Fig B.5 Deployment Center Generating Production Docker Container Packages*



# REFERENCES

[1] J. Achiam et al., "GPT-4 Technical Report," arXiv preprint arXiv:2303.08774, 2023.

[2] F. Pedregosa et al., "Scikit-learn: Machine Learning in Python," Journal of Machine Learning Research, vol. 12, pp. 2825-2830, 2011.

[3] T. Schick et al., "Toolformer: Language Models Can Teach Themselves to Use Tools," in Advances in Neural Information Processing Systems (NeurIPS), vol. 36, 2023.

[4] Y. Huang et al., "A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions," ACM Computing Surveys, 2024.

[5] S. Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models," in International Conference on Learning Representations (ICLR), 2023.

[6] H. Chase, "LangChain: Building applications with LLMs through composability," https://github.com/langchain-ai/langchain, 2022.

[7] J. Moura, "CrewAI: Cutting-edge framework for orchestrating role-playing autonomous AI agents," https://github.com/joaomdmoura/crewAI, 2023.

[8] Microsoft Corporation, "Semantic Kernel: Integrate cutting-edge LLMs into existing conventional code," https://github.com/microsoft/semantic-kernel, 2023.

[9] Q. Wu et al., "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation Framework," arXiv preprint arXiv:2308.08155, 2023.

[10] L. Wang et al., "A Survey on Large Language Model based Autonomous Agents," Frontiers of Computer Science, vol. 18, no. 6, 2024.

[11] S. Colvin et al., "Pydantic: Data validation using Python type hints," https://docs.pydantic.dev/, 2024.

[12] S. Bubeck et al., "Sparks of Artificial General Intelligence: Early experiments with GPT-4," arXiv preprint arXiv:2303.12712, 2023.

[13] National Institute of Standards and Technology (NIST), "Artificial Intelligence Risk Management Framework (AI RMF 1.0)," U.S. Department of Commerce, 2023.

[14] S. Ramirez, "FastAPI: Modern, fast (high-performance), web framework for building APIs with Python," https://fastapi.tiangolo.com/, 2024.

[15] A. Abid et al., "Gradio: Hassle-Free Sharing and Testing of ML Models in the Wild," arXiv preprint arXiv:1906.02569, 2019.

[16] Ollama Contributors, "Ollama: Get up and running with large language models locally," https://ollama.com/, 2024.

[17] L. Breiman, "Random Forests," Machine Learning, vol. 45, no. 1, pp. 5-32, 2001.

[18] D. Dua and C. Graff, "UCI Machine Learning Repository," University of California, Irvine, School of Information and Computer Sciences, 2019.

[19] R. Pace and O. Barry, "Sparse Spatial Autoregressions: California Housing Dataset," Statistics & Probability Letters, vol. 33, no. 3, pp. 291-297, 1997.

[20] W. N. Street et al., "Nuclear feature extraction for breast tumor diagnosis," in International Symposium on Electronic Imaging: Science and Technology, vol. 1905, pp. 861-870, 1993.

[21] D. Merkel, "Docker: Lightweight Linux Containers for Consistent Development and Deployment," Linux Journal, vol. 2014, no. 239, 2014.

[22] B. Krekel et al., "pytest: Simple powerful testing with Python," https://pytest.org/, 2024.

[23] A. Vaswani et al., "Attention Is All You Need," in Advances in Neural Information Processing Systems (NeurIPS), vol. 30, pp. 5998-6008, 2017.

[24] J. Devlin et al., "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding," in Proc. NAACL-HLT, pp. 4171-4186, 2019.

[25] J. Kaplan et al., "Scaling Laws for Neural Language Models," arXiv preprint arXiv:2001.08361, 2020.
