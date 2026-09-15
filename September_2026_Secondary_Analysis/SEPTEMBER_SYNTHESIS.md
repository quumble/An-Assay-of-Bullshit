# September 2026 Synthesis — An Assay of Bullshit

**Status:** Scientific synthesis after completion of the September harmonized primary, secondary, and post-primary interpretability analyses.

## Executive synthesis

The May studies established that the six tested language-model snapshots differed measurably in how they generated creative text. Those differences appeared in punctuation, openings, pronoun use, formatting, length, titles, and other observable behaviors.

September answers the more important question that May could not:

> **Which apparent model-specific behaviors survive when the surrounding conditions change?**

The answer is neither that models possess immutable stylistic fingerprints nor that their apparent signatures are merely local artifacts.

Instead, the evidence supports an **invariance-structure account of language-model behavior**.

Some model-associated tendencies transfer strongly across independently collected samples and modest changes in prompting. Others are highly sensitive to genre or production constraints. Even behaviors that reliably distinguish models can change substantially in magnitude or expression when the task environment changes.

The central result is therefore not simply that model identity can be predicted from text. It is that **model-associated behavioral regularities have measurable boundary conditions**.

## What September establishes

1. **A substantial model-associated signal survives independent data collection.**  
   A classifier trained on 5,398 Study 2 poems identified the producing model among six alternatives in the independent 180-poem Study 1 set with 48.9% accuracy, against a balanced-class chance reference of 16.7%. This establishes that the body-level signature was not confined to a single collection run or exact prompt regime.

2. **The transferable signal is not reducible to obvious output structure.**  
   When the classifier was restricted to grammar/person and punctuation features, excluding word count, line count, stanza count, words-per-line structure, and mean word length, cross-study six-model attribution remained 43.3%, compared with 48.9% using the full 22-feature body vector. Under phrasing transfer, nonstructural style alone reached 55.8% versus 61.9% for the full vector. Under length-cap transfer, nonstructural style reached 49.6%, approximately matching and slightly exceeding the 48.4% full-vector result. The transferable signal therefore includes conventional microstylistic behavior rather than merely instruction compliance or output length.

3. **Genre change is much more disruptive than independent resampling within poetry, and the difference is not explained by training-set size.**  
   The original P1 cross-study classifier used 5,398 training examples, whereas each P3 cross-genre fold used only 360. IA1 removed that confound by repeatedly training P1 on only 360 Study 2 poems. Across 1,000 deterministic resamples, matched-size cross-study accuracy had a median of 46.1% and a 95% resampling interval of 40.6–52.2%. The observed P3 genre-holdout accuracies were only 24.4% for story, 25.0% for animal, and 17.8% for poem. Thus the large cross-study/cross-genre contrast persists after equalizing the training-data budget. In these studies, genre reorganizes model-associated behavior far more strongly than merely drawing a new sample of the same broad task.

4. **Several individual behaviors show unusually strong cross-study stability.**  
   The ordering of the six models across Study 1 poetry and Study 2 was highly stable for semicolon rate (Spearman ρ ≈ .986), em-dash rate (ρ ≈ .829), words per line (ρ ≈ .829), and overall pronoun POS ratio (ρ ≈ .829). Previously salient May observations also survived harmonization: opening-token entropy showed ρ ≈ .943, title rate ≈ .939, opening-token concentration ≈ .928, and em-dash prevalence ≈ .812. Within Study 2, semicolon rate and em-dash rate were also among the largest individual model-separation effects. This convergence shows that at least some May signatures were repeatable model-associated regularities rather than preprocessing artifacts.

5. **The model signature has both a creative-body layer and a delivery layer.**  
   The primary analyses intentionally examined body-only features. When S2 added only preamble presence, title presence, preamble length, and title length, cross-study six-model accuracy rose from 48.9% to 67.2%. Descriptive six-model-provider attribution rose from 70.6% to 90.6%. Similar gains appeared under phrasing and length transfer. The way a model packages and presents an answer therefore contains substantial additional model-associated information beyond the requested creative artifact itself.

## What September changed relative to May

May primarily established **difference**.

The models differed in observable and sometimes striking ways, but those findings were necessarily local to the environments in which they were measured. A punctuation habit, title tendency, opening pattern, or classifier result could still have reflected a particular prompt set, genre, sample, parser, or production constraint.

September establishes **conditional persistence**.

Some of the May differences recur under independently collected data and altered prompts. Some remain informative when obvious structural variables are removed. Others collapse, reverse, or reorganize under environmental change.

Raw structure provides an especially useful contrast. Model rankings for word count, line count, and stanza count did not remain stable across the two poetry studies; some correlations were negative. Meanwhile punctuation, openings, title behavior, and several compositional measures remained much more recognizable.

Thus “style” should not be treated as a unitary construct.

The evidence distinguishes at least:

**Macrostructural behavior**, such as length, lines, stanza structure, and other strongly task-responsive production choices.

**Microstylistic behavior**, including punctuation and grammatical/person tendencies that can remain recognizable across modest distribution shifts.

**Delivery behavior**, including whether and how the model titles, prefaces, or otherwise frames the requested output.

These layers differ in stability.

## Context dependence is not evidence against a model effect

The September results resolve an important conceptual tension.

A behavior can show a substantial model effect while also showing a substantial model × environment interaction.

For example, semicolon use strongly distinguished models, yet in Study 1 its model × genre interaction was larger than its overall model main effect. Em-dash use likewise showed both substantial model separation and substantial genre interaction.

Therefore:

> **A behavioral tendency can statistically belong to a model without being expressed invariantly across contexts.**

This is the central interpretive distinction.

A model may reliably be more or less likely than another model to exhibit some behavior within a range of environments, while genre, prompt constraints, or other production conditions modulate the magnitude or even the ordering of that behavior.

Stable model association and contextual dependence are not contradictory findings.

## Evidentiary hierarchy

The September evidence should retain its existing hierarchy in the manuscript.

P1–P5 are the frozen primary analyses specified before the September outcomes were inspected. They establish cross-study transfer, descriptive provider transfer, genre transfer, prompt/length transfer, and opening-token entropy behavior.

S1–S5 are the planned secondary analyses specified before inspection of the primary September results. They characterize individual feature stability, body versus response-surface information, corrected Study 2 effect sizes, survival of salient May observations, and model × genre interactions.

IA1–IA3 are explicitly outcome-informed exploratory analyses developed after inspection of P1–P5. They resolve the training-size confound, decompose the classifier by fixed feature families, and organize the results into a descriptive transfer map. They strengthen interpretation but should not be presented as prospectively specified confirmatory tests.

## What the evidence does not establish

The results do not establish immutable model fingerprints. They do not show that a model has a context-independent writing style, personality, or internal psychological trait. They do not identify mechanisms inside the models that generate the observed patterns.

The provider comparisons apply only descriptively to the six named model snapshots tested and should not be generalized to Anthropic and OpenAI models as populations.

The studies also do not provide a fully crossed and equally powered train-environment × test-environment experiment. The current transfer map is asymmetric because Study 1 and Study 2 differ substantially in design and sample size. A genuinely reciprocal invariance matrix remains a target for prospective work.

## Scientific interpretation

The most defensible description of the finding is:

> **Language-model behavioral signatures have an invariance structure. Some observable model-associated behaviors survive changes in sampling, prompt wording, and production constraints; others are strongly task-contingent, and sufficiently large contextual changes can reorganize the signature itself.**

Classification is useful here as an assay rather than as the scientific endpoint.

If model identity remains recoverable after an environmental change, some model-associated behavioral information has survived that transformation. Feature-level analyses can then identify which observable behaviors contribute to that persistence and which fail to travel.

This reframes the scientific question from:

> “Can these models be distinguished?”

to:

> **“Under what transformations of the environment does a behavioral attribution to a model remain valid?”**

## Broader methodological claim

Statements of the form **“Model X has property Y”** are underspecified unless the relevant environmental domain is also known.

A stronger empirical characterization asks which changes preserve Y, which attenuate it, and which reorganize it.

The Bullshit Assay therefore suggests a general evaluation principle:

> **Model-level behavioral claims should be accompanied, where possible, by evidence about their invariance under distribution shift.**

A measured difference observed in one benchmark, prompt format, genre, or interaction regime should not automatically be treated as a general property of the model.

Conversely, contextual modulation does not imply that the original model effect was unreal.

The scientifically useful object is the boundary between the two.

## Manuscript-level conclusion

May discovered model-associated signatures.

September established that those signatures are **selectively transferable, structurally heterogeneous, and context-dependent**.

The resulting picture is not one of fixed stylistic fingerprints. It is one of repeatable behavioral tendencies whose expression depends on the environment.

The main contribution of the September analysis is therefore a way of making model-level behavioral claims more precise:

> **A property attributed to a language model should be understood partly in terms of the contexts across which that attribution continues to hold.**