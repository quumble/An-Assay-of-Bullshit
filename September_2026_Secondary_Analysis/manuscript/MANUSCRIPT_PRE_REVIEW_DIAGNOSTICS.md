# From Fingerprints to Boundary Conditions: Model-Associated Style Under Distribution Shift

## Introduction

Researchers routinely characterize language models with statements of the form *Model X tends to do Y*. A model may be described as unusually verbose, more likely to refuse, prone to particular rhetorical forms, distinctive in its use of punctuation, or systematically different from another model on some behavioral measure. Such statements are often useful summaries of empirical results. But they also contain an implicit generalization: a behavior observed under one set of prompts, tasks, sampling conditions, and measurement choices is treated as informative about the model beyond the precise environment in which it was measured. The strength of that inference depends not only on whether the original difference is reliable, but also on how far it travels when the surrounding conditions change.

There is now substantial evidence that outputs from different large language models contain recognizable model-associated signals. Work on machine-generated-text attribution has identified lexical, morphosyntactic, syntactic, structural, and semantic features that distinguish outputs from different model families. McGovern et al. (2025), for example, showed that comparatively simple lexical and part-of-speech features can produce model-specific “fingerprints” that remain useful outside the domains on which they were learned. Bitton et al. (2025) likewise reported persistent stylistic differences among several major model families, while Lu et al. (2026) combined explicit stylometric features with semantic representations for robust model attribution and described the persistence of model-associated style as “style inertia.” This work establishes an important starting point: model identity can leave detectable traces in generated text, and those traces need not disappear immediately outside the setting in which they were first measured.

The problem of separating a source-specific writing signal from the environment in which writing is produced is older than language models. Computational stylometry has long distinguished authorship from topic, genre, and domain effects (Stamatatos, 2009). Cross-domain attribution studies have therefore asked which linguistic measurements continue to identify an author when the subject matter or writing situation changes. Sundararajan and Woodard (2018), for example, examined which linguistic features represent “style” under cross-topic and cross-genre conditions, while Altakrori et al. (2021) designed the Topic Confusion Task specifically to distinguish failures of authorship modeling from failures caused by topic shift. Their results illustrate a general difficulty: a feature may predict who produced a text in one environment without constituting a portable signature of that producer. Attribution accuracy alone does not reveal how much of the learned distinction belongs to the source and how much belongs to the conditions of production.

A parallel problem appears in contemporary evaluation of language models. Measured model behavior can change under seemingly modest alterations to the evaluation environment. Sclar et al. (2024) documented large performance variation under changes in prompt formatting and argued that evaluations should characterize performance across plausible prompt realizations rather than rely on a single arbitrarily selected format. Siska et al. (2024) showed that benchmark conclusions, including model rankings, depend on assumptions about the distribution of test prompts. At the same time, apparent instability need not always reflect instability in the model itself: Hua et al. (2025) found that some reported prompt sensitivity can be induced or exaggerated by evaluation procedures that score semantically equivalent outputs differently. These findings reinforce a broader lesson from behavioral testing and construct-validity work: an observed score supports only those claims that the measurement design can justify (Ribeiro et al., 2020; Elazar et al., 2021; Bean et al., 2025). Model behavior, task environment, and measurement procedure must therefore be distinguished rather than collapsed into a single observed outcome.

These literatures leave a narrower question that is especially relevant when researchers make behavioral claims about a model itself. Model-attribution research principally asks whether the generating model can be identified. Robustness research generally asks whether task performance or benchmark rankings survive changes in prompts or test distributions. Stylometry asks which textual measurements capture authorship rather than topic or genre. We connect these questions by treating model attribution not as an endpoint, but as an **assay of behavioral persistence**. If a classifier trained in one environment can still recover model identity after the environment changes, then some model-associated behavioral information has survived that transformation. If attribution collapses, the original signature may have been more tightly coupled to its production context. And if different families of observable features transfer differently, those differences can help identify what kind of behavior is actually persisting.

Our question is therefore not simply whether language models possess distinguishable stylistic signatures. Prior work gives good reason to expect that they do. We instead ask:

> **Which model-associated behavioral signatures survive changes in study, prompt wording, production constraint, and genre, and which apparent signatures are local to the environment in which they were measured?**

We examine this question using two independently conducted studies involving the same six named model snapshots from the Claude and GPT families. The first study sampled creative writing across three genres under comparatively small, balanced conditions. The second collected a much larger sample of poetry while systematically varying prompt phrasing and requested line limits. We harmonized the two datasets under a common parsing and feature-extraction procedure and represented each generated body using 22 interpretable measurements spanning output structure, word length, part-of-speech composition, pronoun use, and punctuation. This design creates several distinct changes of environment rather than a single undifferentiated “out-of-domain” condition: independent data collection within poetry, changes in prompt wording, changes in production constraints, and changes in genre.

The analyses proceed from attribution to interpretation. First, we test whether a six-way model classifier trained in one study transfers to the other, and whether model-associated information survives held-out genres, phrasings, and line-length conditions. We then examine the stability of individual behavioral measurements across studies, restore titles and preambles to distinguish the requested creative body from its surrounding delivery, and measure model-by-genre interactions for features that distinguish models strongly. Finally, in explicitly outcome-informed exploratory analyses, we equalize a major training-size difference between cross-study and cross-genre transfer and decompose attribution into fixed families of form/structure, grammar/person, punctuation, and combined nonstructural style. The purpose of these decompositions is not to optimize classification. It is to determine what kinds of observable behavior carry model-associated information across environmental change.

The resulting picture is neither one of immutable model fingerprints nor one in which apparent model signatures dissolve entirely under distribution shift. Substantial six-way model information transfers between independently collected poetry studies. Much of that transferable information remains when obvious structural variables such as length, line count, and stanza count are removed. Prompt wording and explicit length constraints alter the strength and composition of the signature without eliminating it. Genre change is markedly more disruptive, and this contrast remains when the cross-study classifier is restricted to the same training-data budget as the cross-genre analysis. At the feature level, some behaviors—particularly several punctuation, opening, grammatical, and presentation tendencies—remain comparatively stable, while coarse structural measures can reorganize substantially. Strong model effects can also coexist with strong model-by-genre interactions.

We describe these patterns as the **boundary conditions of model-associated behavior**. A measurable behavioral regularity can be genuinely associated with a model without being invariant across every context in which the model is used. Conversely, contextual modulation does not by itself show that the original model effect was spurious. The empirical question is where the attribution continues to hold and where it ceases to travel. On this view, claims of the form *Model X has property Y* become more informative when they also specify, or empirically investigate, the domain over which Y remains recognizable. The present study offers one limited demonstration of that approach: using stylistic attribution as an assay, we ask not only whether six language models write differently, but **how far those differences travel before the environment reorganizes them**.

## Methods

### Study design and analytic strategy

This study is a secondary synthesis of two independently conducted language-model experiments originally completed in May 2026. No new model outputs were generated for the September analysis. The original datasets were retained unchanged, and all cross-study analyses were performed on newly harmonized features derived from the frozen raw response text.

The September analysis was designed to test the persistence of model-associated behavioral signatures under several changes in production environment. The two source studies provide complementary forms of variation. Bullshit Assay 1 (BA1) sampled three creative-writing genres under several requested length conditions, allowing cross-genre transfer to be tested. Bullshit Assay 2 (BA2) sampled poetry at substantially greater scale while varying prompt phrasing and requested line limits, allowing transfer across wording and production constraints to be tested. Because both studies included the same six model positions, BA2 could additionally be used to train classifiers that were evaluated on independently collected BA1 poetry.

The September work was divided into three evidentiary layers. Primary analyses (P1–P5) and planned secondary analyses (S1–S5) were specified before the harmonized September outcomes were inspected. Post-primary interpretability analyses (IA1–IA3) were developed after inspection of P1–P5 and are therefore explicitly outcome-informed and exploratory. The latter were used to examine alternative explanations and interpret the composition of transferred model signal rather than to redefine the primary findings.

### Models

Both studies tested the same six named model snapshots: Claude Haiku 4.5 (`claude-haiku-4-5-20251001`), Claude Sonnet 4.6 (`claude-sonnet-4-6`), Claude Opus 4.7 (`claude-opus-4-7`), GPT-5.4 nano (`gpt-5.4-nano`), GPT-5.4 mini (`gpt-5.4-mini`), and GPT-5.4 (`gpt-5.4`).

The design contains one named model at each provider-by-tier position. Provider and tier comparisons are therefore descriptive only; neither factor is independently replicated at the model level, and no population-level inference about Anthropic, OpenAI, or model-size tiers is made.

### Source studies

BA1 was an exploratory creative-writing study containing 540 successful outputs. The design crossed six models with three creative-writing categories—story, animal, and poem—and three requested length conditions, with 10 outputs sampled per model-prompt cell. All generations used temperature 1.0, no system message, and a 400-token output cap. The resulting design contained 180 records per genre and 30 records per model within each genre.

BA2 was a prospectively preregistered poetry follow-up. The planned design contained 5,400 calls: six models × three prompt phrasings (`write`, `compose`, `gimme`) × three requested line caps (5, 10, and 20 lines) × 100 iterations per cell. Generations again used temperature 1.0, no system message, and a 400-token output cap.

The frozen BA2 raw dataset contains 5,398 successful, non-empty responses and two API-error records. The original May feature table contained 5,397 records because one successful raw response had been omitted during the May feature-generation process. The September pipeline therefore followed the prespecified rule of deriving inclusion directly from frozen raw responses.

**[Table 1 about here]**

### Harmonization of response text

The two May studies had originally been processed with different feature pipelines. The September analysis therefore re-derived all common features directly from raw response text under a single locked harmonization specification.

The central preprocessing distinction separated each response into up to three components: meta-preamble, title, and creative body. Body-level features were computed only from the creative body.

Line endings were normalized while internal blank lines, casing, punctuation, spelling, grammar, and markdown were otherwise preserved. Preamble detection was restricted to short leading framing material matching prespecified lexical patterns. Title detection was performed only after preamble removal and used prespecified rules for markdown headings, standalone emphasized headings, and short title-like lines separated from subsequent body text.

### Parser validation

Before harmonized outcome analysis, the parser was evaluated on a locked 180-response human-validation sample selected with seed `20260915`. The sample contained 90 responses from each study and 15 responses per model per study. Model and provider identity were hidden during review.

The prespecified acceptance threshold was 0.90 agreement for every applicable field. All fields passed: preamble presence, .989; title presence, .994; preamble-boundary correctness, .920; title-boundary correctness, .986; and creative-body starting point, .989.

### Harmonized features

The primary representation consisted of 22 numeric body features.

Six measured length and line structure: body word count, non-empty line count, stanza count, mean words per line, within-response words-per-line standard deviation, and mean word length.

Five represented part-of-speech composition: noun/proper noun, verb/auxiliary, adjective, adverb, and pronoun ratios.

Four represented person/pronoun composition: first-person singular, first-person plural, second-person, and third-person shares of recognized pronouns.

Seven represented punctuation events per 100 body words: em dash, semicolon, colon, comma, exclamation mark, question mark, and ellipsis.

The first lexical token and opening bigram were also extracted for frequency and entropy analyses but were not included in the primary 22-feature classifier.

A planned secondary full-surface representation added only four measurements: preamble presence, title presence, preamble token count, and title token count.

### Classification and transfer analyses

P1, P3, and P4 used six-way L2-regularized logistic regression. Missing numeric values were imputed from the training data only, and continuous features were standardized using training-set parameters only. No feature selection or hyperparameter tuning used held-out outcomes.

P1 trained on all 5,398 BA2 poems and tested without retraining on the 180 independently collected BA1 poems.

P3 used leave-one-genre-out classification within BA1: story + animal → poem; story + poem → animal; and animal + poem → story.

P4 used leave-one-group-out transfer within BA2 for prompt phrasing (`write`, `compose`, `gimme`) and requested line cap (5, 10, 20).

P2 repeated cross-study transfer using binary provider labels and was interpreted descriptively only.

P5 compared opening-token entropy across studies, rarefying BA2 10,000 times to 30 poems per model to match BA1 poetry.

### Planned secondary analyses

S1 estimated cross-study feature stability from the six per-model means in BA1 poetry and BA2 using Spearman rank correlation and 2,000 stratified bootstrap resamples.

S2 repeated P1–P4 with the four response-surface features added to the 22 body features.

S3 calculated harmonized BA2 model effect sizes for all body features.

S4 re-estimated previously salient May signatures, including em-dash behavior, title and preamble rates, opening concentration and entropy, line/block formatting, and pronoun tendencies.

S5 decomposed BA1 feature variation into model, genre, model × genre, and within-cell components.

### Outcome-informed exploratory analyses

IA1 addressed the unequal P1/P3 training sizes by repeating cross-study transfer over 1,000 deterministic BA2 samples containing exactly 360 training poems, 60 per model.

IA2 reran P1, P3, and P4 using five fixed feature representations: form/structure, grammar/person, punctuation, nonstructural style, and the full 22-feature body vector.

IA3 organized these results into a descriptive transfer map. Because the original experiments were not a fully crossed reciprocal design, this map was not interpreted as a complete invariance matrix.

### Reproducibility

The final harmonized table contained 5,938 responses: 540 from BA1 and 5,398 from BA2. September scripts, validation records, derived data, result files, software-version information, random seeds, and deviations were preserved separately from the frozen May source studies.

## Results

### Model-associated stylistic information transferred across independent studies

The primary cross-study classifier reached **48.9% six-way accuracy** on the independent BA1 poetry set, compared with 16.7% balanced-class chance (95% stratified-bootstrap interval, **42.8–55.0%**).

Transfer differed substantially by model. Recall was 73.3% for Claude Haiku 4.5, 63.3% for GPT-5.4 nano, 56.7% for GPT-5.4 mini, 46.7% for GPT-5.4, 43.3% for Claude Sonnet 4.6, and 10.0% for Claude Opus 4.7.

The descriptive provider-label classifier reached **70.6% accuracy** (95% interval, **65.0–76.1%**), but this result is restricted to the six tested snapshots.

Opening-token entropy also showed partial cross-study persistence. Four of six BA1 values fell inside their corresponding BA2 rarefaction intervals, and the broad cross-model ordering was similar across studies.

**[Table 2 about here]**

### Different environmental changes disrupted the signature to different degrees

Leave-one-phrasing-out transfer within BA2 remained comparatively strong. Accuracy was 64.1% for held-out `write`, 65.9% for `compose`, and 55.7% for `gimme`, giving **61.9% pooled accuracy**.

Length-cap transfer was weaker. Accuracy was 49.6% for the 5-line holdout, 57.4% for 10 lines, and 38.3% for 20 lines, for **48.4% pooled accuracy**.

Cross-genre transfer was much weaker. Accuracy was **24.4% for story**, **25.0% for animal**, and **17.8% for poem**, for **22.4% pooled accuracy**.

The large difference between P1 and P3 could potentially have reflected training size, because P1 trained on 5,398 examples and P3 on 360. IA1 therefore repeated P1 across 1,000 deterministic training samples of exactly 360 BA2 poems.

Median matched-size cross-study accuracy remained **46.1%**, with a 2.5th–97.5th percentile interval of **40.6–52.2%**. Even the lower tail of that distribution remained well above the observed P3 genre-transfer accuracies.

Within this design, therefore, genre change was considerably more disruptive to model recognizability than independent resampling within poetry, and the difference was not explained by the P1/P3 training-size imbalance.

**[Figure 1 about here]**

### The transferable signature was heterogeneous rather than unitary

Cross-study stability differed sharply among the 22 body features.

Semicolon rate showed **ρ = .986** across model means in the two poetry datasets. Em-dash rate, mean words per line, and overall pronoun ratio each showed **ρ = .829**. First-person-plural share showed **ρ = .714**.

By contrast, model rankings for body word count (**ρ = −.429**), non-empty line count (**ρ = −.543**), and stanza count (**ρ = −.314**) did not reproduce.

Previously salient May observations showed a similar pattern after harmonization. Opening-token entropy (**ρ = .943**), title rate (**ρ = .939**), modal opening concentration (**ρ = .928**), and em-dash prevalence (**ρ = .812**) were highly stable across the two poetry samples.

Within BA2, the largest descriptive model effects appeared for semicolon rate (η² = .315), em-dash rate (.301), overall pronoun ratio (.226), and first-person-singular share (.206).

**[Figure 3 about here]**

The exploratory feature-family decomposition showed that the cross-study classifier was not primarily exploiting coarse structural differences.

P1 accuracy was 34.4% using form/structure alone, 31.7% using grammar/person alone, 33.9% using punctuation alone, **43.3% using combined nonstructural style**, and 48.9% using the full body vector.

Under held-out phrasing, nonstructural style reached **55.8%**, compared with 61.9% for the full representation. Under held-out line constraints, nonstructural style reached **49.6%**, compared with 48.4% for the full representation.

No feature family, however, produced strong cross-genre transfer.

**[Table 3 about here]**

**[Figure 2 about here]**

### Strong model differences coexisted with strong genre dependence

The BA1 factorial design showed that substantial model separation did not imply context invariance.

Mean words per line produced a model effect of η² = .072 and a model × genre interaction of η² = .052.

Mean word length produced η² = .155 for model and .108 for the interaction.

Em-dash rate produced η² = .178 for model and .133 for model × genre.

Semicolon rate, despite being the most cross-study-stable body feature, produced η² = .082 for model and a larger η² = .146 for model × genre.

Thus a feature could strongly distinguish models, reproduce across independent poetry samples, and still change substantially in relative expression across genres.

### Response presentation carried additional model-associated information

Adding only title presence, preamble presence, title length, and preamble length substantially improved attribution.

Cross-study accuracy increased from **48.9% to 67.2%**. Descriptive provider-label accuracy increased from **70.6% to 90.6%**. Cross-genre pooled accuracy increased from **22.4% to 31.5%**, phrasing-transfer accuracy from **61.9% to 80.8%**, and length-cap transfer from **48.4% to 63.0%**.

Because these four variables were added jointly, their individual contributions cannot be separated. The result nevertheless shows that model-associated information extends beyond the requested creative body into response packaging and presentation.

**[Figure 4 about here]**

### Summary of the transfer pattern

Across analyses, substantial model-associated information survived independent poetry collection, prompt wording changes, and output constraints. That signal was not reducible to obvious structural features.

Different components of the signature had different domains of stability. Several punctuation, opening, grammatical, and presentation behaviors reproduced strongly, while raw structural measures did not. Genre shift was markedly more disruptive than the other tested transformations, and strong model effects could coexist with strong model-by-genre interactions.

The six tested snapshots therefore exhibited **partially transferable, context-dependent behavioral signatures** rather than either immutable stylistic fingerprints or purely local artifacts.

## Discussion

The present analyses began with a deliberately modest question. Prior work has already shown that outputs from different language models can contain stylistic information sufficient for generator attribution, including under some out-of-domain conditions. We therefore did not ask whether language models possess distinguishable “fingerprints” in the abstract. We asked instead how far a model-associated behavioral signature travels when the conditions of production change, and which observable components of that signature remain recognizable.

Across two independently collected studies of the same six model snapshots, the answer was mixed in a systematic way. Model identity remained substantially recoverable when a classifier trained on one poetry study was transferred to another. It also transferred under changes in prompt phrasing and explicit length constraints, although the strength and composition of the signal changed. In contrast, transfer across creative-writing genres was weak. Individual features showed the same heterogeneity: several punctuation, opening, grammatical, and presentation behaviors preserved model-relative differences across independently collected poetry samples, while coarse quantities such as word count, line count, and stanza count did not. These results support neither an immutable-fingerprint interpretation nor the view that model-associated style is merely an artifact of a particular prompt. Rather, the observed signatures had measurable **boundary conditions**.

### A model effect is not the same as a context-invariant property

The most important distinction in these results is between a behavior being associated with a model and that behavior remaining stable across environments.

Several features illustrate the point. Semicolon use was among the strongest model-separating behaviors in BA2 and showed nearly identical model ordering across the two poetry studies. Yet within BA1, semicolon use also exhibited a substantial model-by-genre interaction. Em-dash use showed a similar pattern. These behaviors were therefore neither arbitrary local noise nor fixed properties expressed independently of context.

This matters because statements about language models are often compressed into formulations such as “Model X is more verbose,” “Model Y uses more first-person language,” or “Model Z tends to use em dashes.” Such statements may accurately summarize a particular experiment while still obscuring the domain over which the comparison holds.

> **A model-associated tendency should be understood partly in terms of the environmental transformations under which it remains recognizable.**

This formulation does not require behavioral invariance to be absolute. A property may be highly stable under independent resampling and modest prompt perturbation, partially stable under production constraints, and substantially reorganized by genre.

### Attribution as an assay rather than an endpoint

Generator-attribution research typically evaluates success by how accurately the source model can be identified. Here, classification served a different role.

We treated model attribution as an **assay of preserved behavioral information**. When a classifier trained in one environment continued to recognize model identity in another, some observable model-associated structure had survived the change. When transfer deteriorated, the change identified a boundary on the original signature.

The feature-family results are important in this respect. The cross-study signal did not disappear when obvious structural quantities such as word count, line count, and stanza count were removed. Grammar/person and punctuation together retained most of the cross-study classification performance and transferred strongly under changes in prompt phrasing.

At the same time, no feature family produced robust cross-genre transfer. There was no hidden set of simple punctuation or grammatical features that behaved as a context-free model identity once macrostructure was removed.

### Relationship to prior model-fingerprint and stylometric work

These findings extend rather than overturn previous work on language-model fingerprints.

Recent studies have shown that model outputs contain lexical, morphosyntactic, structural, and semantic information sufficient for source attribution, sometimes across domains. The present findings are consistent with that literature.

The contribution here is narrower. Rather than optimizing attribution across a single in-domain/out-of-domain division, we compared several different transformations within the same set of six model snapshots and decomposed the resulting transfer into interpretable behavioral components.

This perspective also reconnects language-model attribution with a longstanding problem in human stylometry. Human authorship attribution has repeatedly confronted the distinction between an authorial signal and signals produced by topic, genre, register, or writing situation. Language models offer an unusually tractable version of this problem because the generator is known exactly and the production environment can be manipulated directly.

### Relationship to prompt robustness and distribution shift

The results also complement work showing that LLM evaluation can be sensitive to prompt formulation and test distributions.

Most robustness studies ask whether a capability score, benchmark ranking, or task prediction remains stable as prompts or evaluation distributions change. The present analyses concern a different dependent variable: the behavioral characteristics of the model's output itself.

A model could maintain task performance while changing substantially in how it expresses an answer. Conversely, a model-associated stylistic signature could remain recognizable while its task accuracy changes. Robustness of performance and robustness of behavioral expression therefore need not coincide.

Our results suggest that behavioral attribution can itself be treated as a distribution-shift problem.

### Different layers of model-associated behavior

The full-surface analyses suggest that model-associated behavior is layered.

**Macrostructural behavior** includes length, line structure, stanza structure, and related production choices. These were often highly responsive to prompt and genre conditions.

**Microstylistic behavior** includes punctuation, grammatical composition, and person usage. These features carried substantial signal across independent samples and modest prompt shifts but were not genre-invariant.

**Delivery behavior** includes whether and how the model introduces, titles, or otherwise packages its response. These surface conventions carried substantial additional identifying information.

These categories are descriptive rather than mechanistic. Their value is to prevent “style” from functioning as a single undifferentiated explanation.

### Implications for claims about language-model behavior

The broader implication is methodological rather than ontological.

Language-model research routinely reports behavioral differences under finite experimental conditions. Those differences may be real and reproducible within those conditions. The risk arises when the scope of the empirical observation silently expands into a more general statement about the model.

A finding that one model is more likely than another to exhibit behavior Y under prompt set A does not by itself establish that the ordering will survive prompt set B, genre C, another output constraint, or a later model snapshot.

This does not mean that researchers should avoid model-level descriptions. It means that the **scope of those descriptions is itself an empirical question**.

Where feasible, behavioral studies could therefore supplement estimates of model differences with targeted transfer tests:

> **Across what changes in context does the tendency remain recognizably true?**

### Limitations

The study concerns only six named model snapshots from two providers. Each provider-by-tier position is represented by one model, preventing population-level provider or tier inference.

The tasks were restricted to minimally specified creative writing, and poetry was the only direct cross-study bridge.

The two source studies were not prospectively constructed as a fully crossed invariance experiment. Several dimensions differ between them simultaneously.

The feature representation was intentionally sparse and interpretable and did not include embeddings, semantic representations, or learned attribution features.

Several feature-stability analyses compare only six model-level means and are therefore descriptive.

The full-surface analysis added four correlated response-presentation variables jointly.

Finally, the IA analyses were outcome-informed and exploratory, although they were documented before execution and subjected to reproducibility controls.

### Toward a prospective behavioral-transfer design

The obvious next experiment is a prospectively balanced, fully crossed design.

Model identity could be crossed with genre, prompt wording, output constraint, independent collection wave, and potentially decoding settings. Reciprocal train/test transfer among all environments would then produce a genuine **behavioral transfer matrix**.

For each observable behavior or feature family, such a design could ask which transformations preserve model ordering, which preserve attribution, which change only magnitude, which reverse relative differences, and which eliminate observable model information.

The same approach need not be restricted to style. Refusal behavior, calibration, sycophancy, confidence language, hedging, citation behavior, emotional framing, and other measurable behaviors could be studied in terms of the environmental boundaries across which model-level claims remain valid.

### Conclusion

Previous work has established that language-model outputs can contain recognizable model-specific stylistic information. The present study asks a narrower question:

**How far does that information travel?**

Across six model snapshots, substantial stylistic signal survived independent collection within poetry and changes in prompt wording and production constraints. The transferable signal included punctuation and grammatical/person behavior and was not reducible to coarse length or formatting. Other behaviors, particularly raw structural quantities, were much less stable. Genre change disrupted attribution far more strongly, even after equalizing training-set size, and strong model effects could coexist with strong model-by-genre interactions. Titles and preambles provided an additional layer of model-associated delivery behavior.

The resulting picture is therefore one of **partially transferable, context-dependent behavioral signatures**.

> **A behavioral property attributed to a language model is better characterized when the contexts across which that attribution continues to hold are also known.**

**The boundary of a model-level claim is not merely a limitation on the result. It is part of the result.**
