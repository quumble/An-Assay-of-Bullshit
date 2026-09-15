# Literature Positioning — An Assay of Bullshit

**Date:** September 2026  
**Purpose:** Position the September manuscript before drafting.  
**Scope:** Targeted literature review, not a systematic or exhaustive review. The search prioritizes work on LLM stylistic attribution, cross-domain stylometry, prompt and distribution sensitivity, behavioral testing, and construct-valid evaluation.

## Executive conclusion

The literature supports a strong paper, but it narrows the novelty claim.

It is already established that:

- outputs from different language models can contain model- or family-specific stylistic signals;
- some such signals can support attribution across text domains;
- genre and topic are longstanding confounds in human stylometry;
- LLM evaluation results can change substantially under prompt variation and distribution shift;
- behavioral testing and construct-validity traditions already treat invariance under some transformations as evidence about what a measurement really captures.

Accordingly, the manuscript should **not** claim that it is the first to discover language-model stylistic fingerprints, the first to perform cross-domain model attribution, or the first to show that LLM behavior depends on context.

The more defensible and more interesting contribution is the connection among these literatures:

> **We use model attribution as an assay of the boundary conditions of model-associated behavior. Rather than asking only whether model identity is recoverable, we ask which observable components of a model-associated signature survive changes in independent sampling, prompt wording, production constraint, and genre; which components reorganize; and where the attribution itself ceases to travel.**

The novelty is therefore primarily in the **scientific target and integrated design**, rather than in the existence of stylometric model differences alone.

---

# 1. Nearest prior work

## 1.1 Model fingerprints and generator attribution

The nearest direct predecessor is McGovern et al., *Your Large Language Models are Leaving Fingerprints*. Using lexical and morphosyntactic frequency features, they show that relatively simple classifiers can distinguish LLM outputs and that these “fingerprints” can remain useful out of domain. They explicitly describe persistent lexical and morphosyntactic differences across text domains and some persistence within model families. This is genuine prior evidence for cross-domain stylistic regularity in LLM outputs.

Bitton, Bitton, and Nisan similarly frame different LLM families as possessing identifiable stylistic fingerprints, including when models are instructed to produce different writing styles. Their work is currently best treated as a relevant preprint rather than as the anchor citation.

Even closer in methodology is Lu et al. (Findings of ACL 2026), who combine stylometric and semantic representations for model attribution. Their framing of “style inertia,” use of lexical, syntactic, and structural features, and evaluation under cross-domain conditions make this an important contemporary neighbor. Their objective, however, remains robust attribution performance rather than characterization of the conditions under which particular behavioral claims remain valid.

OpenTuringBench and recent multilingual machine-generated-text attribution work further demonstrate that generator attribution is now a substantial research problem in its own right, including out-of-domain and cross-lingual evaluation.

RAID provides a complementary result from machine-generated-text detection rather than six-way model attribution: detectors that appear effective under familiar conditions can fail substantially under unseen domains, models, decoding strategies, or adversarial modifications. This is important background for the broader principle that attribution performance is conditional on the evaluation environment.

### What this literature already establishes

We should grant this literature substantial territory.

LLM outputs can carry identifiable model-associated stylistic information. That information is sometimes sufficiently stable to support out-of-domain attribution. Modern attribution methods can extract lexical, morphosyntactic, structural, semantic, and other model-specific signals.

### What it generally does not make the primary scientific object

The principal question is usually:

> **Can the producing model be identified robustly?**

Our question is different:

> **What does successful or unsuccessful attribution tell us about the stability of the underlying model-associated behavior?**

For us, attribution accuracy is an **assay**. The scientific object is the environmental domain across which behavioral information remains recognizable.

That distinction needs to be explicit, because the paper would otherwise look like a lower-dimensional model-attribution study competing with methods optimized for classification performance.

---

# 2. Classical stylometry already warns us about genre

The human-authorship literature provides important intellectual precedent.

Stamatatos's authorship-attribution survey explicitly identifies genre and topic as factors that must be separated from authorship, and later work shows substantial degradation when known and unknown texts differ in topic or genre.

The Topic Confusion Task was designed precisely to distinguish genuine authorial signal from topic-driven classification, and found that some feature families—particularly certain syntactic or part-of-speech features—are less susceptible to topic variation than others.

Sundararajan and Woodard likewise ask what actually represents “style” in cross-domain authorship attribution rather than content or domain membership.

This literature matters for two reasons.

First, our finding that genre dramatically reorganizes model-associated signatures should not be presented as conceptually unprecedented. Human stylometry has wrestled with essentially the same distinction between **author signal and environmental signal** for decades.

Second, it strengthens the interpretation of IA2. Separating macrostructural features from grammar/person and punctuation is not merely an ad hoc classifier ablation. It belongs to a longstanding stylometric problem:

> Which observable features plausibly represent portable stylistic regularities, and which primarily encode the writing situation?

Our contribution is to pose that problem for **language-model snapshots whose identity is experimentally known and whose production environment can be deliberately manipulated**.

---

# 3. Prompt sensitivity and distribution-shift research

A separate LLM literature establishes that measured model behavior is highly conditional on evaluation inputs.

Sclar et al. show that seemingly inconsequential prompt-format changes can produce very large changes in observed benchmark performance. Their recommendation that evaluation account for plausible prompt variation is directly relevant to the idea that a behavioral claim should not inherit unwarranted generality from a single prompt realization.

Hua et al. complicate this story by showing that some apparent prompt sensitivity can itself arise from evaluation artifacts. This is particularly relevant to our harmonized preprocessing and parser discipline: observed instability can come from either the model or the measurement apparatus, so the latter must be held as constant as possible.

Siska et al. make an even broader point. Benchmark conclusions implicitly depend on a distribution over test prompts, and model rankings may change when reasonable distributional assumptions change. A benchmark score is therefore conditional on a distribution of interest rather than a context-free fact about a model.

LENS extends this concern to naturally changing user-prompt distributions, showing that distribution shift in real-world prompts can correspond to substantial changes in model performance.

### Relation to our paper

This literature usually asks whether **task performance, benchmark ranking, or evaluation outcomes** survive a changed prompt distribution.

We instead ask whether **model-associated behavioral identity** survives.

Those are related but distinct objects.

A model might retain the same task accuracy while expressing itself differently enough that its stylistic signature changes. Conversely, a recognizable stylistic signature might persist even while task performance deteriorates.

Our study therefore applies a distribution-shift question to the attribution of **behavioral properties**, rather than only to capability scores.

---

# 4. Behavioral testing and construct validity

The broader methodological framing has clear antecedents.

CheckList argues that held-out accuracy alone gives an incomplete picture of NLP model behavior and advocates behavioral tests tied to capabilities and controlled perturbations, including invariance-style expectations.

Elazar et al. explicitly define one form of consistency in pretrained language models through invariance of behavior under meaning-preserving input changes. Their empirical finding that models can be inconsistent despite appearing knowledgeable provides another precedent for treating invariance across transformations as evidence about the strength of a behavioral attribution.

More recently, Bean et al. place LLM benchmark design in a construct-validity framework, emphasizing that benchmark tasks and scoring procedures must justify the claims researchers infer from them. The connection to this manuscript is direct: observing a model difference under one measurement regime does not automatically validate a broader statement about the model.

A very recent 2026 preprint on construct validity in LLM-as-a-judge evaluation formalizes related ideas in terms of invariance under construct-preserving transformations and sensitivity under construct-changing transformations. The object of study is different—the evaluator rather than the generator—but it signals that “invariance” is increasingly being used explicitly in LLM measurement theory.

There is therefore ample precedent for the general principle that **claims about model behavior should be stress-tested under controlled transformations**.

The opening for this paper is narrower:

> Behavioral-testing and construct-validity work asks whether an evaluation continues to measure what it claims to measure. We ask how the *model-associated property itself* behaves as its production environment changes.

---

# 5. The gap our study can legitimately occupy

The relevant literatures largely run in parallel.

**LLM attribution research** asks whether generator identity can be recovered from output.

**Stylometry research** asks which textual cues characterize authors and which are confounded by genre, topic, or domain.

**Prompt-robustness research** asks whether model performance and model rankings survive changes in inputs or test distributions.

**Behavioral-testing and construct-validity research** asks whether a measurement supports the behavioral claim researchers infer from it.

The Bullshit Assay connects these questions.

Its central object is not classification accuracy itself, but the **transport of model-associated behavioral information across specified changes in environment**.

The design contributes several things jointly that are much less common in the existing literature:

1. The same six named model snapshots are examined across several distinct kinds of environmental change: independent data collection, prompt phrasing, explicit production constraints, and genre.

2. Transfer is not treated as a single binary “in-domain/out-of-domain” distinction. Different transformations are compared as different stresses on the same model-associated signature.

3. The transferable signal is decomposed into fixed, human-interpretable behavioral families—macrostructure, grammar/person, punctuation, combined nonstructural style, and response-delivery behavior—rather than optimized solely for attribution accuracy.

4. Feature-level stability is examined directly alongside classifier transfer.

5. Model main effects are examined jointly with model × genre interactions, allowing the paper to demonstrate that a behavior can be genuinely model-associated while still being strongly context-conditioned.

6. A major alternative explanation—the approximately fifteen-fold P1/P3 training-size difference—is explicitly tested and does not explain the cross-study/cross-genre contrast.

The integrated conclusion is therefore not simply that “model fingerprints exist.”

It is:

> **Model-associated behavioral signatures possess measurable boundary conditions, and different components of those signatures have different domains of stability.**

---

# 6. Claims that are already established and should not be sold as novel

The manuscript should avoid claiming novelty for the following propositions.

**LLMs have distinguishable writing styles.**  
Established by multiple attribution and stylometry papers.

**Model identity can sometimes be recovered across text domains.**  
Already directly demonstrated.

**Genre or topic can confound stylistic attribution.**  
Long established in human stylometry.

**Prompt changes can alter apparent model behavior.**  
Substantial recent LLM literature.

**Distribution shift can alter benchmark conclusions or model rankings.**  
Established in evaluation and robustness research.

**Invariance under transformations is a useful evaluation concept.**  
Established in behavioral testing, consistency work, robustness research, and increasingly construct-validity work.

The manuscript will be stronger if it concedes all six points early.

---

# 7. Claims that appear defensibly distinctive

The strongest novelty claim is **not** a priority claim about discovering a new phenomenon.

It is a claim about the empirical organization of several known phenomena.

A defensible formulation is:

> **Prior work has shown both that LLM outputs carry model-specific stylistic information and that model evaluations can be sensitive to distribution shift. We connect these observations by treating model attribution as an assay of the boundary conditions of model-associated behavior: across independent collection, prompt wording, production constraint, and genre, we ask not only whether a model remains recognizable, but which observable components of its behavioral signature persist, which reorganize, and where the attribution itself ceases to travel.**

A somewhat stronger formulation, subject to a final citation sweep before submission, is:

> **Few existing studies jointly compare multiple environmental transformations while decomposing model attribution into interpretable behavioral components and explicitly treating transfer failure as evidence about the scope of model-level behavioral claims.**

That is probably where the manuscript's novelty belongs.

The empirical contribution is therefore **comparative boundary mapping**, not merely fingerprint detection.

---

# 8. Terminology recommendations

## “Fingerprint”

Use primarily when describing prior literature.

Avoid adopting it as our own technical term. It implies uniqueness, permanence, and context invariance more strongly than the results warrant.

Prefer:

- **model-associated behavioral signature**
- **stylistic signature**
- **transferable signal**
- **behavioral regularity**

## “Invariance”

Retain it, but define it carefully.

“Invariance” already has several meanings across machine learning, causal inference, representation learning, behavioral testing, and measurement theory. Our results do not identify a causally invariant representation and do not establish absolute invariance.

If used, define it operationally as something like:

> **the degree to which model-associated observable differences remain recognizable across a specified environmental transformation.**

I would avoid presenting **“behavioral invariance structure”** as newly coined terminology.

A very recent non-peer-reviewed online discussion even uses the exact phrase “Behavioral Invariance Structure” for the question of which experimental transformations preserve observable model behavior. This is not important scholarly prior art, but it is enough reason not to build a novelty claim around naming the concept.

## “Boundary conditions”

This is now my preferred headline language.

It says exactly what the study identifies without implying absolute invariance.

Good phrases include:

- **boundary conditions of model-associated behavior**
- **contextual stability of model-associated style**
- **signature transfer across environments**
- **domain of validity of a behavioral attribution**

“Transportability” can be useful in prose, but it also has technical meanings in causal-inference literature. I would use it descriptively rather than brand the method around it.

## “Trait”

Avoid except when explicitly rejecting the inference.

The data identify statistical behavioral regularities, not psychological traits or internal personalities.

---

# 9. Core reference set

A compact manuscript could probably be built around roughly fifteen indispensable references, with additional citations added locally.

### LLM attribution and stylometry

- McGovern, Hope, Stureborg, Suhara & Alikaniotis (2025), **Your Large Language Models are Leaving Fingerprints**. Nearest direct precedent for cross-domain lexical/morphosyntactic LLM fingerprints.
- Lu et al. (2026), **Synergizing Stylometrics with Semantics: Dual-Path Framework for LLM Detection and Attribution**, Findings of ACL. Important contemporary stylometric attribution work and “style inertia” framing.
- Bitton, Bitton & Nisan (2025), **Detecting Stylistic Fingerprints of Large Language Models**, preprint. Relevant neighboring claim; cite with publication-status caution.
- La Cava & Tagarelli et al. (2025), **OpenTuringBench**, EMNLP. Robust machine-generated-text detection/attribution benchmark.
- Dugan et al. (2024), **RAID**, ACL. Large robustness benchmark showing detector degradation across models, domains, decoding, and adversarial conditions.

### Stylometry and domain confounding

- Stamatatos (2009), **A Survey of Modern Authorship Attribution Methods**, JASIST. Foundational overview.
- Stamatatos (2018), **Masking Topic-Related Information to Enhance Authorship Attribution**, JASIST. Cross-topic/domain robustness.
- Altakrori et al. (2021), **The Topic Confusion Task**, Findings of EMNLP. Separates stylistic attribution from topic confounding.
- Sundararajan & Woodard (2018), **What Represents “Style” in Authorship Attribution?**, COLING. Cross-domain feature interpretation.

### Prompt and distribution sensitivity

- Sclar et al. (2024), **Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design**, ICLR.
- Siska et al. (2024), **Examining the Robustness of LLM Evaluation to the Distributional Assumptions of Benchmarks**, ACL. Particularly important for claim scope.
- Hua et al. (2025), **Flaw or Artifact? Rethinking Prompt Sensitivity in Evaluating LLMs**, EMNLP. Important measurement-artifact qualification.
- Seegmiller & Preum (2026), **Measuring Distribution Shift in User Prompts and Its Effects on LLM Performance**, ACL. Current real-world prompt-distribution work.

### Behavioral testing and construct validity

- Ribeiro et al. (2020), **Beyond Accuracy: Behavioral Testing of NLP Models with CheckList**, ACL. Foundational behavioral-testing precedent.
- Elazar et al. (2021), **Measuring and Improving Consistency in Pretrained Language Models**, TACL. Explicit invariance/consistency precedent.
- Bean et al. (2025), **Measuring What Matters: Construct Validity in Large Language Model Benchmarks**, NeurIPS Datasets & Benchmarks. Strong measurement-theory anchor.

Useful secondary context could include Geirhos et al. on shortcut learning and D'Amour et al. on underspecification, both of which make the broader ML point that apparently successful systems can behave differently under changed deployment conditions.

---

# 10. Recommended manuscript positioning

The literature suggests adjusting the paper's rhetorical sequence slightly.

Do **not** begin with “LLMs have stylistic fingerprints.”

Begin with the inference:

> Researchers routinely make model-level statements of the form “Model X tends to do Y.”

Then establish that several adjacent fields already make that inference difficult.

Stylometry shows that authorship and domain can be entangled.

LLM attribution shows that generator-specific information exists and can sometimes transfer across domains.

Prompt-robustness research shows that measured model behavior can depend strongly on the test distribution.

Construct-validity research shows that a measurement result licenses only some behavioral claims.

That leads naturally to the unresolved question:

> **When an observable behavior is attributed to a language model, across which changes in environment does that attribution continue to hold?**

The Bullshit Assay then becomes a deliberately simple empirical vehicle for answering this question.

Six known generators produce text under environments that differ in study, prompt wording, output constraint, and genre. If model identity remains recoverable, some model-associated information has survived the transformation. If particular feature families retain their model ordering or predictive information, the nature of that survival becomes interpretable. If transfer collapses, that identifies a boundary on the original attribution.

This framing makes classification subordinate to measurement theory rather than making the manuscript another detector paper.

---

# 11. Revised title direction

The literature search makes the former title **The Invariance Structure of Language-Model Behavior** conceptually defensible, but probably not optimal.

“Invariance” is already heavily occupied terminology, and “fingerprint” is already an established attribution metaphor.

I would now prefer one of these directions:

**From Fingerprints to Boundary Conditions: Model-Associated Style Under Distribution Shift**

**The Boundary Conditions of Language-Model Style**

**How Far Does a Language-Model Signature Travel? Model-Associated Behavior Across Study, Prompt, Constraint, and Genre**

Of these, **From Fingerprints to Boundary Conditions** is probably the strongest scholarly title because it immediately locates the paper relative to the existing attribution literature while announcing the conceptual advance.

The more accessible **How Far Does a Language-Model Signature Travel?** is probably the strongest title if readability and memorability matter more than disciplinary signaling.

---

# 12. Introduction architecture after the literature review

The Introduction can now be written in approximately five moves.

**Paragraph 1 — The problem of model-level attribution.**  
Researchers describe models as verbose, sycophantic, cautious, stylistically distinctive, more likely to refuse, more likely to use particular linguistic forms, and so forth. Such claims implicitly generalize beyond the exact test context.

**Paragraph 2 — We know identifiable model signal exists.**  
Introduce LLM fingerprinting, generator attribution, and stylometric evidence, including cross-domain results. Concede this literature fully.

**Paragraph 3 — But behavioral measurements are environmentally conditional.**  
Bring in classical cross-domain stylometry plus prompt/distribution sensitivity in LLM evaluation.

**Paragraph 4 — The missing question concerns the scope of the property claim.**  
Attribution work asks whether identity can be recovered; robustness work usually asks whether performance survives; neither question alone tells us which observable model-associated behaviors remain stable under which environmental transformations.

**Paragraph 5 — Present the assay and contribution.**  
We harmonize two independently collected studies involving six model snapshots and test model-associated behavioral transfer across study, genre, prompt phrasing, and production constraints. We then decompose the transferred information into interpretable behavioral components and examine cases where strong model effects coexist with strong model × context interactions.

The Introduction should end not with:

> “Can we identify six models from their writing?”

but with:

> **“What properties of a language model remain recognizably its own when the surrounding conditions change?”**

The answer supplied by the paper is:

> **Some do, some do not, and the boundary is measurable.**