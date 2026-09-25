# Chunking and retrieval comparison: 30 IELTS Writing questions

## Corpus analysis and chunking choice

- Corpus: 5 standardized IELTS Writing Markdown pages. The pages use nested headings, paragraphs, and lists; the longest article contains long criterion explanations and examples.
- Legacy: recursive character splitting, 500 characters with 50-character overlap; 137 chunks.
- Updated: Markdown heading-path-aware recursive splitting, 1200 characters maximum including a repeated `Section:` breadcrumb, zero overlap, and paragraph/list grouping; 95 chunks.
- Chunk content length: legacy average 413 / median 431 characters; updated average 659 / median 547 characters.
- Reason: heading context prevents chunks from becoming detached from the IELTS criterion/task they describe. Paragraph/list grouping keeps self-contained guidance together. Zero overlap avoids indexing repeated content; document sections already carry context.
- Gold relevance is determined from exact evidence spans in the corpus, normalized for crawler replacement/zero-width characters and whitespace. This makes labels independent of chunk IDs and permits a fair comparison across boundaries.
- Query language: English; questions match the language of the source corpus.
- Dense: `sentence-transformers/all-mpnet-base-v2` Sentence Transformers embeddings with normalized cosine vectors. Sparse: the project's BM25 implementation. Hybrid: RRF (`k=60`) from each method's top 10, output top 5.
- Metrics are macro averages across the same 30 queries. Hit@k means a chunk containing a complete accepted evidence span appears in the first k. This evaluates chunk match, not generated answer correctness or citation quality.

## Aggregate chunk-match results

| Chunker | Method | Hit@1 | Hit@3 | Hit@5 | MRR@5 |
|---|---|---:|---:|---:|---:|
| Legacy recursive 500/50 | Sparse (BM25) | 0.600 | 0.767 | 0.767 | 0.678 |
| Legacy recursive 500/50 | Dense | 0.633 | 0.733 | 0.800 | 0.682 |
| Legacy recursive 500/50 | Hybrid (RRF) | 0.700 | 0.867 | 0.933 | 0.780 |
| Markdown section-aware 1200/0 | Sparse (BM25) | 0.567 | 0.867 | 0.900 | 0.712 |
| Markdown section-aware 1200/0 | Dense | 0.500 | 0.667 | 0.767 | 0.587 |
| Markdown section-aware 1200/0 | Hybrid (RRF) | 0.667 | 0.867 | 0.900 | 0.764 |

## Change by retrieval method

| Method | Δ Hit@1 | Δ Hit@3 | Δ Hit@5 | Δ MRR@5 |
|---|---:|---:|---:|---:|
| Sparse (BM25) | -0.033 | +0.100 | +0.133 | +0.034 |
| Dense | -0.133 | -0.067 | -0.033 | -0.095 |
| Hybrid (RRF) | -0.033 | +0.000 | -0.033 | -0.016 |

## Reading the result

Updated versus legacy Hit@5: BM25 +0.133, dense -0.033, hybrid -0.033. These measured results describe this dataset and embedder only; they do not guarantee that hybrid ranks first for every query. For Vietnamese questions against English source chunks, evaluate a bilingual embedder and query translation as separate configurations before selecting production behavior.

## Scores by question challenge

| Challenge | Chunker | Method | Hit@1 | Hit@5 | MRR@5 |
|---|---|---|---:|---:|---:|
| BM25-targeted terms | Legacy recursive 500/50 | Sparse (BM25) | 0.700 | 0.900 | 0.783 |
| BM25-targeted terms | Legacy recursive 500/50 | Dense | 0.700 | 0.900 | 0.758 |
| BM25-targeted terms | Legacy recursive 500/50 | Hybrid (RRF) | 0.900 | 0.900 | 0.900 |
| BM25-targeted terms | Markdown section-aware 1200/0 | Sparse (BM25) | 0.600 | 0.900 | 0.750 |
| BM25-targeted terms | Markdown section-aware 1200/0 | Dense | 0.500 | 0.900 | 0.607 |
| BM25-targeted terms | Markdown section-aware 1200/0 | Hybrid (RRF) | 0.800 | 0.900 | 0.850 |
| Semantic paraphrases | Legacy recursive 500/50 | Sparse (BM25) | 0.600 | 0.600 | 0.600 |
| Semantic paraphrases | Legacy recursive 500/50 | Dense | 0.600 | 0.700 | 0.620 |
| Semantic paraphrases | Legacy recursive 500/50 | Hybrid (RRF) | 0.600 | 1.000 | 0.707 |
| Semantic paraphrases | Markdown section-aware 1200/0 | Sparse (BM25) | 0.500 | 0.900 | 0.670 |
| Semantic paraphrases | Markdown section-aware 1200/0 | Dense | 0.500 | 0.800 | 0.603 |
| Semantic paraphrases | Markdown section-aware 1200/0 | Hybrid (RRF) | 0.600 | 1.000 | 0.767 |
| Multi-constraint questions | Legacy recursive 500/50 | Sparse (BM25) | 0.500 | 0.800 | 0.650 |
| Multi-constraint questions | Legacy recursive 500/50 | Dense | 0.600 | 0.800 | 0.667 |
| Multi-constraint questions | Legacy recursive 500/50 | Hybrid (RRF) | 0.600 | 0.900 | 0.733 |
| Multi-constraint questions | Markdown section-aware 1200/0 | Sparse (BM25) | 0.600 | 0.900 | 0.717 |
| Multi-constraint questions | Markdown section-aware 1200/0 | Dense | 0.500 | 0.600 | 0.550 |
| Multi-constraint questions | Markdown section-aware 1200/0 | Hybrid (RRF) | 0.600 | 0.800 | 0.675 |

## Per-question chunk match

‘✓’ marks a chunk that contains a complete gold evidence span.

### Q01 — BM25-targeted terms

> Which Writing task contributes the larger share of the overall mark, and what fraction does it contribute?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_04_ielts-academic-format-writing::chunk-6` (11.5341), 2. `article_02_writing-test-resources::chunk-62` (11.3140), 3. `article_02_writing-test-resources::chunk-6` (10.9573) ✓, 4. `article_02_writing-test-resources::chunk-27` (10.3449), 5. `article_02_writing-test-resources::chunk-3` (10.2265) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-6` (0.6214) ✓, 2. `article_02_writing-test-resources::chunk-11` (0.5953), 3. `article_02_writing-test-resources::chunk-15` (0.5844), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-3` (0.5807), 5. `article_04_ielts-academic-format-writing::chunk-3` (0.5555) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-6` (0.0323) ✓, 2. `article_04_ielts-academic-format-writing::chunk-6` (0.0164), 3. `article_02_writing-test-resources::chunk-11` (0.0161), 4. `article_02_writing-test-resources::chunk-62` (0.0161), 5. `article_02_writing-test-resources::chunk-15` (0.0159) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_04_ielts-academic-format-writing::chunk-4` (13.7932), 2. `article_02_writing-test-resources::chunk-2` (13.4001) ✓, 3. `article_02_writing-test-resources::chunk-8` (13.1730), 4. `article_02_writing-test-resources::chunk-26` (11.7554), 5. `article_02_writing-test-resources::chunk-1` (11.5537) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-9` (0.6396), 2. `article_02_writing-test-resources::chunk-6` (0.5861), 3. `article_02_writing-test-resources::chunk-4` (0.5773), 4. `article_02_writing-test-resources::chunk-14` (0.5744), 5. `article_02_writing-test-resources::chunk-2` (0.5698) ✓ |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-2` (0.0315) ✓, 2. `article_04_ielts-academic-format-writing::chunk-2` (0.0301), 3. `article_04_ielts-academic-format-writing::chunk-5` (0.0292), 4. `article_02_writing-test-resources::chunk-9` (0.0164), 5. `article_04_ielts-academic-format-writing::chunk-4` (0.0164) |

Evidence: Task 2 contributes two thirds of the overall Writing mark, while Task 1 contributes one third.

### Q02 — Multi-constraint questions

> What minimum response lengths and approximate time budgets apply to the two Academic Writing tasks?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_02_writing-test-resources::chunk-5` (12.0816), 2. `article_04_ielts-academic-format-writing::chunk-6` (11.9427), 3. `article_04_ielts-academic-format-writing::chunk-15` (11.8695), 4. `article_04_ielts-academic-format-writing::chunk-0` (11.1456), 5. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-3` (10.5256) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-6` (0.7080) ✓, 2. `article_03_academic-test::chunk-19` (0.6357), 3. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-3` (0.6255), 4. `article_04_ielts-academic-format-writing::chunk-8` (0.6220), 5. `article_03_academic-test::chunk-11` (0.6096) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-6` (0.0315) ✓, 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-3` (0.0313), 3. `article_04_ielts-academic-format-writing::chunk-15` (0.0308), 4. `article_02_writing-test-resources::chunk-5` (0.0164), 5. `article_03_academic-test::chunk-19` (0.0161) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_04_ielts-academic-format-writing::chunk-8` (12.0261), 2. `article_04_ielts-academic-format-writing::chunk-2` (10.9778), 3. `article_02_writing-test-resources::chunk-2` (10.8645) ✓, 4. `article_04_ielts-academic-format-writing::chunk-10` (10.6907), 5. `article_04_ielts-academic-format-writing::chunk-4` (10.4091) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-2` (0.6009) ✓, 2. `article_04_ielts-academic-format-writing::chunk-9` (0.5994), 3. `article_04_ielts-academic-format-writing::chunk-4` (0.5992), 4. `article_02_writing-test-resources::chunk-17` (0.5971), 5. `article_02_writing-test-resources::chunk-6` (0.5905) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-2` (0.0323) ✓, 2. `article_04_ielts-academic-format-writing::chunk-4` (0.0313), 3. `article_04_ielts-academic-format-writing::chunk-10` (0.0308), 4. `article_02_writing-test-resources::chunk-6` (0.0297), 5. `article_04_ielts-academic-format-writing::chunk-8` (0.0164) |

Evidence: Task 1: at least 150 words and about 20 minutes. Task 2: at least 250 words and about 40 minutes.

### Q03 — Semantic paraphrases

> When describing Academic Task 1 visual data, what should the writer select and report, and when should comparisons be made?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-8` (15.8947) ✓, 2. `article_02_writing-test-resources::chunk-27` (12.9894), 3. `article_02_writing-test-resources::chunk-17` (12.4434) ✓, 4. `article_04_ielts-academic-format-writing::chunk-10` (12.3774), 5. `article_02_writing-test-resources::chunk-39` (11.8063) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-7` (0.7111), 2. `article_04_ielts-academic-format-writing::chunk-1` (0.6656), 3. `article_04_ielts-academic-format-writing::chunk-10` (0.6568), 4. `article_04_ielts-academic-format-writing::chunk-4` (0.6098), 5. `article_02_writing-test-resources::chunk-8` (0.6089) ✓ |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-8` (0.0318) ✓, 2. `article_04_ielts-academic-format-writing::chunk-10` (0.0315), 3. `article_02_writing-test-resources::chunk-7` (0.0309), 4. `article_02_writing-test-resources::chunk-27` (0.0161), 5. `article_04_ielts-academic-format-writing::chunk-1` (0.0161) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_04_ielts-academic-format-writing::chunk-7` (15.6690), 2. `article_02_writing-test-resources::chunk-6` (15.5206) ✓, 3. `article_02_writing-test-resources::chunk-3` (14.4309) ✓, 4. `article_02_writing-test-resources::chunk-7` (14.2074), 5. `article_02_writing-test-resources::chunk-10` (13.1958) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-9` (0.6684), 2. `article_02_writing-test-resources::chunk-7` (0.5675), 3. `article_02_writing-test-resources::chunk-2` (0.5449), 4. `article_04_ielts-academic-format-writing::chunk-7` (0.5417), 5. `article_04_ielts-academic-format-writing::chunk-5` (0.5318) |
| Hybrid (RRF) | Yes | 1. `article_04_ielts-academic-format-writing::chunk-7` (0.0320), 2. `article_02_writing-test-resources::chunk-7` (0.0318), 3. `article_02_writing-test-resources::chunk-6` (0.0308) ✓, 4. `article_02_writing-test-resources::chunk-9` (0.0164), 5. `article_02_writing-test-resources::chunk-2` (0.0159) |

Evidence: Summarise the information by selecting and reporting its main features; make comparisons where relevant.

### Q04 — BM25-targeted terms

> In a General Training Task 1 letter, how do the personal, semi-formal and formal categories change with the recipient and situation?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-26` (29.7329) ✓, 2. `article_02_writing-test-resources::chunk-10` (25.0715) ✓, 3. `article_02_writing-test-resources::chunk-35` (20.3153), 4. `article_02_writing-test-resources::chunk-30` (18.0013), 5. `article_02_writing-test-resources::chunk-25` (17.7511) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-26` (0.6430) ✓, 2. `article_02_writing-test-resources::chunk-10` (0.6343) ✓, 3. `article_02_writing-test-resources::chunk-30` (0.6266), 4. `article_02_writing-test-resources::chunk-35` (0.5817), 5. `article_02_writing-test-resources::chunk-9` (0.5241) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-26` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-10` (0.0323) ✓, 3. `article_02_writing-test-resources::chunk-30` (0.0315), 4. `article_02_writing-test-resources::chunk-35` (0.0315), 5. `article_02_writing-test-resources::chunk-25` (0.0305) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-10` (32.5173) ✓, 2. `article_02_writing-test-resources::chunk-3` (30.6373) ✓, 3. `article_02_writing-test-resources::chunk-12` (22.6783), 4. `article_02_writing-test-resources::chunk-14` (22.6701), 5. `article_02_writing-test-resources::chunk-11` (18.8005) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-10` (0.5736) ✓, 2. `article_02_writing-test-resources::chunk-12` (0.5492), 3. `article_02_writing-test-resources::chunk-11` (0.5310), 4. `article_02_writing-test-resources::chunk-14` (0.5271), 5. `article_02_writing-test-resources::chunk-13` (0.4649) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-10` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-12` (0.0320), 3. `article_02_writing-test-resources::chunk-3` (0.0313) ✓, 4. `article_02_writing-test-resources::chunk-11` (0.0313), 5. `article_02_writing-test-resources::chunk-14` (0.0312) |

Evidence: The situation determines whether the letter is personal (for example, to a friend), semi-formal (to a manager), or formal (to someone not personally known).

### Q05 — BM25-targeted terms

> For Task 2, what does the Task Response criterion assess about answering the question and developing main ideas?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-13` (16.3257), 2. `article_02_writing-test-resources::chunk-12` (15.8479) ✓, 3. `article_04_ielts-academic-format-writing::chunk-3` (14.4335), 4. `article_02_writing-test-resources::chunk-39` (13.7799), 5. `article_02_writing-test-resources::chunk-42` (12.4137) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-12` (0.7584) ✓, 2. `article_02_writing-test-resources::chunk-44` (0.7107), 3. `article_04_ielts-academic-format-writing::chunk-4` (0.6988), 4. `article_02_writing-test-resources::chunk-36` (0.6972), 5. `article_02_writing-test-resources::chunk-43` (0.6775) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-12` (0.0325) ✓, 2. `article_02_writing-test-resources::chunk-44` (0.0306), 3. `article_04_ielts-academic-format-writing::chunk-3` (0.0304), 4. `article_02_writing-test-resources::chunk-36` (0.0303), 5. `article_02_writing-test-resources::chunk-13` (0.0164) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_04_ielts-academic-format-writing::chunk-2` (19.0139), 2. `article_02_writing-test-resources::chunk-4` (18.2351) ✓, 3. `article_02_writing-test-resources::chunk-16` (16.7916), 4. `article_02_writing-test-resources::chunk-17` (15.7647), 5. `article_02_writing-test-resources::chunk-0` (15.7369) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-17` (0.7374), 2. `article_02_writing-test-resources::chunk-18` (0.7191), 3. `article_02_writing-test-resources::chunk-4` (0.6489) ✓, 4. `article_02_writing-test-resources::chunk-15` (0.6022), 5. `article_02_writing-test-resources::chunk-9` (0.5980) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-17` (0.0320), 2. `article_02_writing-test-resources::chunk-4` (0.0320) ✓, 3. `article_04_ielts-academic-format-writing::chunk-2` (0.0311), 4. `article_02_writing-test-resources::chunk-18` (0.0308), 5. `article_02_writing-test-resources::chunk-15` (0.0306) |

Evidence: Task Response is used for Task 2; it assesses completeness of the response and how main ideas are extended and supported. Task Achievement is used for Task 1.

### Q06 — Multi-constraint questions

> How do the official explanations distinguish organisation/linking from vocabulary assessment, including what is judged about word choice?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_02_writing-test-resources::chunk-63` (14.4081), 2. `article_02_writing-test-resources::chunk-54` (12.6095), 3. `article_02_writing-test-resources::chunk-45` (11.5832), 4. `article_02_writing-test-resources::chunk-62` (10.3401), 5. `article_04_ielts-academic-format-writing::chunk-5` (9.5641) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-54` (0.5466), 2. `article_02_writing-test-resources::chunk-55` (0.5379), 3. `article_02_writing-test-resources::chunk-13` (0.5213) ✓, 4. `article_02_writing-test-resources::chunk-59` (0.5070), 5. `article_02_writing-test-resources::chunk-1` (0.5064) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-54` (0.0325), 2. `article_02_writing-test-resources::chunk-63` (0.0313), 3. `article_02_writing-test-resources::chunk-56` (0.0303), 4. `article_04_ielts-academic-format-writing::chunk-5` (0.0297), 5. `article_02_writing-test-resources::chunk-55` (0.0161) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_02_writing-test-resources::chunk-26` (15.5475), 2. `article_02_writing-test-resources::chunk-23` (12.2956), 3. `article_02_writing-test-resources::chunk-19` (12.2141), 4. `article_02_writing-test-resources::chunk-0` (10.8634), 5. `article_04_ielts-academic-format-writing::chunk-2` (10.7700) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-24` (0.5867), 2. `article_02_writing-test-resources::chunk-23` (0.5700), 3. `article_02_writing-test-resources::chunk-26` (0.5282), 4. `article_02_writing-test-resources::chunk-25` (0.4863), 5. `article_02_writing-test-resources::chunk-5` (0.4742) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-26` (0.0323), 2. `article_02_writing-test-resources::chunk-23` (0.0323), 3. `article_02_writing-test-resources::chunk-0` (0.0308), 4. `article_02_writing-test-resources::chunk-25` (0.0303), 5. `article_04_ielts-academic-format-writing::chunk-2` (0.0303) |

Evidence: Coherence and Cohesion concerns organisation, logical development and links; Lexical Resource concerns vocabulary range, accuracy and appropriacy.

### Q07 — Semantic paraphrases

> Which published reference can a learner consult to compare the full IELTS Writing descriptors and detailed assessment criteria across score levels?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (32.7480) ✓, 2. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-1` (17.2811), 3. `article_02_writing-test-resources::chunk-1` (16.7170), 4. `article_02_writing-test-resources::chunk-15` (12.5536), 5. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-8` (12.0446) |
| Dense | Yes | 1. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.7658) ✓, 2. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-1` (0.7275), 3. `article_04_ielts-academic-format-writing::chunk-3` (0.7135), 4. `article_02_writing-test-resources::chunk-0` (0.6991), 5. `article_02_writing-test-resources::chunk-5` (0.6917) |
| Hybrid (RRF) | Yes | 1. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.0328) ✓, 2. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-1` (0.0323), 3. `article_02_writing-test-resources::chunk-3` (0.0290), 4. `article_02_writing-test-resources::chunk-1` (0.0159), 5. `article_04_ielts-academic-format-writing::chunk-3` (0.0159) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (35.2624) ✓, 2. `article_02_writing-test-resources::chunk-0` (19.4078), 3. `article_02_writing-test-resources::chunk-5` (16.9130), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-1` (13.7076), 5. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-0` (12.9468) |
| Dense | Yes | 1. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.7598) ✓, 2. `article_02_writing-test-resources::chunk-5` (0.7548), 3. `article_04_ielts-academic-format-writing::chunk-2` (0.7510), 4. `article_02_writing-test-resources::chunk-3` (0.7476), 5. `article_02_writing-test-resources::chunk-0` (0.7390) |
| Hybrid (RRF) | Yes | 1. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-5` (0.0320), 3. `article_02_writing-test-resources::chunk-0` (0.0315), 4. `article_04_ielts-academic-format-writing::chunk-2` (0.0308), 5. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-1` (0.0306) |

Evidence: The full assessment scales used by Writing examiners, including the band descriptors and detailed key assessment criteria, were made available.

### Q08 — Multi-constraint questions

> When planning a Task 2 essay, how does the recommended schedule divide time among planning, drafting, and the final revision stage?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-4` (22.3738) ✓, 2. `article_02_writing-test-resources::chunk-14` (14.5302), 3. `article_02_writing-test-resources::chunk-42` (13.6651), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-3` (12.3190), 5. `article_02_writing-test-resources::chunk-61` (11.6438) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-6` (0.5835), 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-3` (0.5511), 3. `article_02_writing-test-resources::chunk-44` (0.5075), 4. `article_02_writing-test-resources::chunk-43` (0.4923), 5. `article_02_writing-test-resources::chunk-36` (0.4902) |
| Hybrid (RRF) | Yes | 1. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-3` (0.0318), 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-4` (0.0307) ✓, 3. `article_02_writing-test-resources::chunk-6` (0.0164), 4. `article_02_writing-test-resources::chunk-14` (0.0161), 5. `article_02_writing-test-resources::chunk-42` (0.0159) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-2` (21.3671) ✓, 2. `article_02_writing-test-resources::chunk-5` (13.9510), 3. `article_02_writing-test-resources::chunk-17` (13.1621), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-3` (11.9067), 5. `article_02_writing-test-resources::chunk-25` (11.3480) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-18` (0.5391), 2. `article_02_writing-test-resources::chunk-17` (0.5320), 3. `article_02_writing-test-resources::chunk-9` (0.5118), 4. `article_02_writing-test-resources::chunk-2` (0.5032), 5. `article_02_writing-test-resources::chunk-4` (0.4894) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-17` (0.0320), 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-2` (0.0311) ✓, 3. `article_02_writing-test-resources::chunk-18` (0.0309), 4. `article_02_writing-test-resources::chunk-4` (0.0303), 5. `article_02_writing-test-resources::chunk-5` (0.0161) |

Evidence: The breakdown is 5–10 minutes for reading/planning, 15–20 minutes for the first draft, and 10 minutes for proofreading/editing.

### Q09 — Multi-constraint questions

> What paragraph structure does the essay outline recommend, including the suggested number and role of body paragraphs?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-6` (20.6815) ✓, 2. `article_02_writing-test-resources::chunk-46` (14.2894), 3. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-13` (13.4391), 4. `article_02_writing-test-resources::chunk-50` (13.1802), 5. `article_02_writing-test-resources::chunk-42` (12.8503) |
| Dense | Yes | 1. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-6` (0.6093) ✓, 2. `article_02_writing-test-resources::chunk-42` (0.5973), 3. `article_02_writing-test-resources::chunk-48` (0.5494), 4. `article_03_academic-test::chunk-19` (0.5324), 5. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-7` (0.5137) |
| Hybrid (RRF) | Yes | 1. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-6` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-42` (0.0315), 3. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-13` (0.0310), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-4` (0.0292), 5. `article_02_writing-test-resources::chunk-41` (0.0288) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-5` (21.5574) ✓, 2. `article_02_writing-test-resources::chunk-19` (14.6937), 3. `article_02_writing-test-resources::chunk-17` (12.6055), 4. `article_02_writing-test-resources::chunk-21` (11.5209), 5. `article_02_writing-test-resources::chunk-20` (11.4106) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-11` (0.5042), 2. `article_02_writing-test-resources::chunk-21` (0.4901), 3. `article_02_writing-test-resources::chunk-17` (0.4893), 4. `article_02_writing-test-resources::chunk-20` (0.4864), 5. `article_02_writing-test-resources::chunk-13` (0.4756) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-21` (0.0318), 2. `article_02_writing-test-resources::chunk-17` (0.0317), 3. `article_02_writing-test-resources::chunk-20` (0.0310), 4. `article_02_writing-test-resources::chunk-15` (0.0299), 5. `article_02_writing-test-resources::chunk-11` (0.0164) |

Evidence: Use an introduction, two or three body paragraphs each addressing one issue or idea, and a conclusion that sums up the discussion.

### Q10 — BM25-targeted terms

> During editing, what kind of idea placement makes a paragraph unfocused, and how should the writer fix it?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-13` (13.3137) ✓, 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-6` (12.0925), 3. `article_02_writing-test-resources::chunk-27` (11.6577), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-16` (11.4841), 5. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-11` (11.0167) |
| Dense | Yes | 1. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-7` (0.5253), 2. `article_02_writing-test-resources::chunk-49` (0.5056), 3. `article_02_writing-test-resources::chunk-50` (0.4835), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-13` (0.4725) ✓, 5. `article_02_writing-test-resources::chunk-53` (0.4626) |
| Hybrid (RRF) | Yes | 1. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-13` (0.0320) ✓, 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-7` (0.0164), 3. `article_02_writing-test-resources::chunk-49` (0.0161), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-6` (0.0161), 5. `article_02_writing-test-resources::chunk-27` (0.0159) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-13` (14.5618) ✓, 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-5` (13.9964), 3. `article_02_writing-test-resources::chunk-11` (11.4616), 4. `article_02_writing-test-resources::chunk-12` (10.6352), 5. `article_02_writing-test-resources::chunk-17` (10.4706) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-19` (0.4421), 2. `article_02_writing-test-resources::chunk-21` (0.4394), 3. `article_02_writing-test-resources::chunk-20` (0.4309), 4. `article_02_writing-test-resources::chunk-22` (0.3874), 5. `article_02_writing-test-resources::chunk-13` (0.3497) |
| Hybrid (RRF) | Yes | 1. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-13` (0.0315) ✓, 2. `article_02_writing-test-resources::chunk-21` (0.0311), 3. `article_02_writing-test-resources::chunk-19` (0.0164), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-5` (0.0161), 5. `article_02_writing-test-resources::chunk-11` (0.0159) |

Evidence: A paragraph should address one issue only; move unrelated sentences to the paragraph where they belong.

### Q11 — Semantic paraphrases

> In a visual-summary response, what part condenses the dominant pattern rather than supplying the supporting particulars?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_03_academic-test::chunk-21` (12.6616), 2. `article_03_academic-test::chunk-20` (12.2839), 3. `article_02_writing-test-resources::chunk-20` (10.4613), 4. `article_03_academic-test::chunk-12` (9.9021), 5. `article_02_writing-test-resources::chunk-19` (9.7125) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-21` (0.4667) ✓, 2. `article_02_writing-test-resources::chunk-53` (0.4429), 3. `article_02_writing-test-resources::chunk-24` (0.4427), 4. `article_02_writing-test-resources::chunk-50` (0.4258), 5. `article_02_writing-test-resources::chunk-47` (0.4240) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-21` (0.0164) ✓, 2. `article_03_academic-test::chunk-21` (0.0164), 3. `article_02_writing-test-resources::chunk-53` (0.0161), 4. `article_03_academic-test::chunk-20` (0.0161), 5. `article_02_writing-test-resources::chunk-20` (0.0159) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_03_academic-test::chunk-24` (12.4486), 2. `article_03_academic-test::chunk-23` (11.6163), 3. `article_02_writing-test-resources::chunk-7` (11.4954), 4. `article_02_writing-test-resources::chunk-9` (10.1087), 5. `article_03_academic-test::chunk-4` (9.3317) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-8` (0.4468) ✓, 2. `article_02_writing-test-resources::chunk-22` (0.3878), 3. `article_02_writing-test-resources::chunk-21` (0.3851), 4. `article_02_writing-test-resources::chunk-19` (0.3687), 5. `article_02_writing-test-resources::chunk-20` (0.3605) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-8` (0.0309) ✓, 2. `article_02_writing-test-resources::chunk-7` (0.0308), 3. `article_02_writing-test-resources::chunk-9` (0.0308), 4. `article_03_academic-test::chunk-24` (0.0164), 5. `article_02_writing-test-resources::chunk-22` (0.0161) |

Evidence: The overview summarises the main points, such as the main trends, changes, or number of steps.

### Q12 — Multi-constraint questions

> When a map question asks about major changes over time, what two kinds of supporting detail should accompany the description?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-19` (26.8487), 2. `article_02_writing-test-resources::chunk-20` (22.3934) ✓, 3. `article_02_writing-test-resources::chunk-23` (14.1213), 4. `article_02_writing-test-resources::chunk-24` (13.4439), 5. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-6` (12.3127) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-20` (0.6813) ✓, 2. `article_02_writing-test-resources::chunk-23` (0.5948), 3. `article_02_writing-test-resources::chunk-19` (0.4694), 4. `article_02_writing-test-resources::chunk-21` (0.4643), 5. `article_02_writing-test-resources::chunk-17` (0.3967) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-20` (0.0325) ✓, 2. `article_02_writing-test-resources::chunk-19` (0.0323), 3. `article_02_writing-test-resources::chunk-23` (0.0320), 4. `article_02_writing-test-resources::chunk-8` (0.0299), 5. `article_03_academic-test::chunk-5` (0.0296) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-7` (30.4358) ✓, 2. `article_02_writing-test-resources::chunk-13` (16.4637), 3. `article_02_writing-test-resources::chunk-9` (15.6980), 4. `article_02_writing-test-resources::chunk-8` (13.3330), 5. `article_03_academic-test::chunk-5` (12.0068) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-7` (0.5945) ✓, 2. `article_02_writing-test-resources::chunk-8` (0.4665), 3. `article_03_academic-test::chunk-5` (0.3491), 4. `article_02_writing-test-resources::chunk-9` (0.3389), 5. `article_03_academic-test::chunk-22` (0.2618) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-7` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-8` (0.0318), 3. `article_02_writing-test-resources::chunk-9` (0.0315), 4. `article_03_academic-test::chunk-5` (0.0313), 5. `article_02_writing-test-resources::chunk-6` (0.0292) |

Evidence: Support the major changes with the supplied figures and the positions of items on the map; compass directions can help describe locations.

### Q13 — BM25-targeted terms

> For the Academic visual task, which formatting elements are ruled out even when the response meets the minimum length?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_02_writing-test-resources::chunk-5` (11.8371), 2. `article_04_ielts-academic-format-writing::chunk-10` (10.6204), 3. `article_04_ielts-academic-format-writing::chunk-11` (10.4303), 4. `article_02_writing-test-resources::chunk-25` (10.2977), 5. `article_02_writing-test-resources::chunk-55` (10.1365) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-7` (0.5938), 2. `article_03_academic-test::chunk-19` (0.5830), 3. `article_04_ielts-academic-format-writing::chunk-10` (0.5588), 4. `article_03_academic-test::chunk-11` (0.5472), 5. `article_03_academic-test::chunk-21` (0.5439) |
| Hybrid (RRF) | No | 1. `article_04_ielts-academic-format-writing::chunk-10` (0.0320), 2. `article_02_writing-test-resources::chunk-5` (0.0164), 3. `article_02_writing-test-resources::chunk-7` (0.0164), 4. `article_03_academic-test::chunk-19` (0.0161), 5. `article_04_ielts-academic-format-writing::chunk-11` (0.0159) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_04_ielts-academic-format-writing::chunk-2` (13.4292), 2. `article_02_writing-test-resources::chunk-1` (12.4272), 3. `article_02_writing-test-resources::chunk-8` (11.5964), 4. `article_02_writing-test-resources::chunk-2` (11.5383), 5. `article_04_ielts-academic-format-writing::chunk-7` (11.0496) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-9` (0.5685), 2. `article_04_ielts-academic-format-writing::chunk-5` (0.5646), 3. `article_02_writing-test-resources::chunk-6` (0.5635) ✓, 4. `article_02_writing-test-resources::chunk-17` (0.5285), 5. `article_02_writing-test-resources::chunk-2` (0.5280) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-2` (0.0310), 2. `article_04_ielts-academic-format-writing::chunk-7` (0.0305), 3. `article_02_writing-test-resources::chunk-8` (0.0302), 4. `article_02_writing-test-resources::chunk-9` (0.0164), 5. `article_04_ielts-academic-format-writing::chunk-2` (0.0164) |

Evidence: The response must be written in full without subheadings, bullet points, a greeting, a name/sign-off, or diagrams, charts and tables.

### Q14 — Multi-constraint questions

> In Task 1, what does Task Achievement expect the writer to do with the visual's key features besides selecting them?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-16` (18.0452), 2. `article_02_writing-test-resources::chunk-24` (16.8153) ✓, 3. `article_02_writing-test-resources::chunk-4` (15.8565), 4. `article_02_writing-test-resources::chunk-27` (14.7196), 5. `article_02_writing-test-resources::chunk-17` (13.8600) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-24` (0.6504) ✓, 2. `article_02_writing-test-resources::chunk-7` (0.6217), 3. `article_04_ielts-academic-format-writing::chunk-10` (0.5722), 4. `article_02_writing-test-resources::chunk-35` (0.5532), 5. `article_04_ielts-academic-format-writing::chunk-1` (0.5463) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-24` (0.0325) ✓, 2. `article_02_writing-test-resources::chunk-7` (0.0308), 3. `article_02_writing-test-resources::chunk-25` (0.0292), 4. `article_02_writing-test-resources::chunk-16` (0.0164), 5. `article_02_writing-test-resources::chunk-4` (0.0159) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-6` (20.3638), 2. `article_02_writing-test-resources::chunk-9` (19.9257) ✓, 3. `article_02_writing-test-resources::chunk-10` (17.1430), 4. `article_02_writing-test-resources::chunk-7` (16.2298), 5. `article_02_writing-test-resources::chunk-12` (15.1921) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-9` (0.6117) ✓, 2. `article_02_writing-test-resources::chunk-14` (0.5356), 3. `article_02_writing-test-resources::chunk-7` (0.5081), 4. `article_02_writing-test-resources::chunk-17` (0.4583), 5. `article_02_writing-test-resources::chunk-6` (0.4583) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-9` (0.0325) ✓, 2. `article_02_writing-test-resources::chunk-6` (0.0318), 3. `article_02_writing-test-resources::chunk-7` (0.0315), 4. `article_02_writing-test-resources::chunk-12` (0.0301), 5. `article_02_writing-test-resources::chunk-8` (0.0296) |

Evidence: Compare or contrast the key features, provide enough supporting detail, report accurately, and present an overview.

### Q15 — Semantic paraphrases

> If one instruction in a letter prompt asks for both difficulties and their cause, how should a candidate treat that instruction to cover it fully?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_02_writing-test-resources::chunk-40` (22.6230), 2. `article_02_writing-test-resources::chunk-32` (20.0186), 3. `article_02_writing-test-resources::chunk-41` (19.9557), 4. `article_02_writing-test-resources::chunk-39` (19.0594), 5. `article_02_writing-test-resources::chunk-68` (17.2088) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-35` (0.4927), 2. `article_02_writing-test-resources::chunk-9` (0.4845), 3. `article_02_writing-test-resources::chunk-26` (0.4575), 4. `article_02_writing-test-resources::chunk-25` (0.4491), 5. `article_02_writing-test-resources::chunk-36` (0.4164) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-35` (0.0311), 2. `article_02_writing-test-resources::chunk-32` (0.0311), 3. `article_02_writing-test-resources::chunk-33` (0.0294) ✓, 4. `article_02_writing-test-resources::chunk-40` (0.0164), 5. `article_02_writing-test-resources::chunk-9` (0.0161) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-16` (25.0732), 2. `article_02_writing-test-resources::chunk-13` (24.5722) ✓, 3. `article_02_writing-test-resources::chunk-10` (20.1207), 4. `article_02_writing-test-resources::chunk-12` (19.7411), 5. `article_02_writing-test-resources::chunk-11` (18.2250) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-10` (0.4868), 2. `article_02_writing-test-resources::chunk-14` (0.4844), 3. `article_02_writing-test-resources::chunk-12` (0.4703), 4. `article_02_writing-test-resources::chunk-11` (0.4631), 5. `article_02_writing-test-resources::chunk-13` (0.4396) ✓ |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-10` (0.0323), 2. `article_02_writing-test-resources::chunk-13` (0.0315) ✓, 3. `article_02_writing-test-resources::chunk-12` (0.0315), 4. `article_02_writing-test-resources::chunk-11` (0.0310), 5. `article_02_writing-test-resources::chunk-16` (0.0309) |

Evidence: The example bullet contains two parts: explain more than one problem and explain why working is difficult. Both parts need to be addressed.

### Q16 — BM25-targeted terms

> What does the preparation advice recommend placing in the opening paragraph to make a Band 7 letter's purpose clear?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-29` (25.3730) ✓, 2. `article_02_writing-test-resources::chunk-41` (21.9117), 3. `article_02_writing-test-resources::chunk-28` (17.9038), 4. `article_02_writing-test-resources::chunk-47` (14.5019), 5. `article_02_writing-test-resources::chunk-22` (13.5491) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-29` (0.6893) ✓, 2. `article_02_writing-test-resources::chunk-28` (0.6135), 3. `article_02_writing-test-resources::chunk-41` (0.5849), 4. `article_02_writing-test-resources::chunk-32` (0.5778), 5. `article_02_writing-test-resources::chunk-15` (0.5449) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-29` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-28` (0.0320), 3. `article_02_writing-test-resources::chunk-41` (0.0320), 4. `article_02_writing-test-resources::chunk-32` (0.0306), 5. `article_02_writing-test-resources::chunk-31` (0.0294) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-11` (25.5352) ✓, 2. `article_02_writing-test-resources::chunk-17` (17.3045), 3. `article_02_writing-test-resources::chunk-20` (14.8623), 4. `article_02_writing-test-resources::chunk-8` (14.3361), 5. `article_02_writing-test-resources::chunk-30` (14.0228) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-11` (0.6196) ✓, 2. `article_02_writing-test-resources::chunk-12` (0.5618), 3. `article_02_writing-test-resources::chunk-13` (0.5382), 4. `article_02_writing-test-resources::chunk-10` (0.4931), 5. `article_02_writing-test-resources::chunk-20` (0.4896) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-11` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-12` (0.0313), 3. `article_02_writing-test-resources::chunk-20` (0.0313), 4. `article_02_writing-test-resources::chunk-16` (0.0288), 5. `article_02_writing-test-resources::chunk-17` (0.0161) |

Evidence: State the main purpose in the opening paragraph so the reason for writing is clear.

### Q17 — Semantic paraphrases

> A candidate is writing to a company manager they have never met. What tone and greeting does the IELTS example recommend?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-30` (21.4208) ✓, 2. `article_02_writing-test-resources::chunk-27` (16.9073), 3. `article_02_writing-test-resources::chunk-28` (16.6303), 4. `article_02_writing-test-resources::chunk-10` (14.3634), 5. `article_02_writing-test-resources::chunk-18` (13.3802) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-30` (0.6304) ✓, 2. `article_02_writing-test-resources::chunk-26` (0.5959), 3. `article_02_writing-test-resources::chunk-9` (0.4949), 4. `article_02_writing-test-resources::chunk-10` (0.4884), 5. `article_02_writing-test-resources::chunk-28` (0.4711) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-30` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-28` (0.0313), 3. `article_02_writing-test-resources::chunk-10` (0.0312), 4. `article_02_writing-test-resources::chunk-27` (0.0311), 5. `article_02_writing-test-resources::chunk-26` (0.0161) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-10` (20.4880), 2. `article_02_writing-test-resources::chunk-12` (18.4214) ✓, 3. `article_02_writing-test-resources::chunk-11` (17.2265), 4. `article_02_writing-test-resources::chunk-3` (15.4178), 5. `article_02_writing-test-resources::chunk-25` (15.1487) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-10` (0.5674), 2. `article_02_writing-test-resources::chunk-3` (0.4934), 3. `article_02_writing-test-resources::chunk-12` (0.4465) ✓, 4. `article_03_academic-test::chunk-24` (0.4353), 5. `article_03_academic-test::chunk-18` (0.4321) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-10` (0.0328), 2. `article_02_writing-test-resources::chunk-12` (0.0320) ✓, 3. `article_02_writing-test-resources::chunk-3` (0.0318), 4. `article_02_writing-test-resources::chunk-11` (0.0159), 5. `article_03_academic-test::chunk-24` (0.0156) |

Evidence: Use a formal, not overly chatty or friendly, tone and begin with 'Dear Sir or Madam'.

### Q18 — Multi-constraint questions

> If an essay prompt asks whether advertising harms children and their families, which parts must the response discuss to avoid being capped at Band 5 for Task Response?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-39` (31.6075) ✓, 2. `article_02_writing-test-resources::chunk-40` (24.4400), 3. `article_02_writing-test-resources::chunk-37` (18.6972), 4. `article_02_writing-test-resources::chunk-44` (17.7496), 5. `article_02_writing-test-resources::chunk-41` (17.4619) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-39` (0.7596) ✓, 2. `article_02_writing-test-resources::chunk-40` (0.6636), 3. `article_02_writing-test-resources::chunk-38` (0.6034), 4. `article_02_writing-test-resources::chunk-57` (0.5215), 5. `article_02_writing-test-resources::chunk-36` (0.4977) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-39` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-40` (0.0323), 3. `article_02_writing-test-resources::chunk-38` (0.0310), 4. `article_02_writing-test-resources::chunk-44` (0.0308), 5. `article_02_writing-test-resources::chunk-41` (0.0301) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-16` (35.8099) ✓, 2. `article_02_writing-test-resources::chunk-15` (29.4661), 3. `article_02_writing-test-resources::chunk-17` (21.5559), 4. `article_02_writing-test-resources::chunk-24` (21.3171), 5. `article_02_writing-test-resources::chunk-18` (20.3789) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-16` (0.7326) ✓, 2. `article_02_writing-test-resources::chunk-15` (0.6327), 3. `article_02_writing-test-resources::chunk-17` (0.5186), 4. `article_02_writing-test-resources::chunk-24` (0.4963), 5. `article_02_writing-test-resources::chunk-18` (0.4735) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-16` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-15` (0.0323), 3. `article_02_writing-test-resources::chunk-17` (0.0317), 4. `article_02_writing-test-resources::chunk-24` (0.0312), 5. `article_02_writing-test-resources::chunk-18` (0.0308) |

Evidence: Address both children and their families; omitting either main part limits the response to Band 5. Give reasons and relevant examples.

### Q19 — Semantic paraphrases

> For the next level above Band 6, what qualities should a writer's stance show, and how should the argument finish?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_02_writing-test-resources::chunk-28` (16.8307), 2. `article_02_writing-test-resources::chunk-8` (14.9416), 3. `article_02_writing-test-resources::chunk-48` (14.5339), 4. `article_02_writing-test-resources::chunk-47` (14.3529), 5. `article_02_writing-test-resources::chunk-32` (13.8564) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-41` (0.6672) ✓, 2. `article_02_writing-test-resources::chunk-15` (0.6057), 3. `article_02_writing-test-resources::chunk-42` (0.5490), 4. `article_02_writing-test-resources::chunk-53` (0.5454), 5. `article_02_writing-test-resources::chunk-40` (0.5370) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-47` (0.0308), 2. `article_02_writing-test-resources::chunk-42` (0.0304), 3. `article_02_writing-test-resources::chunk-40` (0.0301), 4. `article_02_writing-test-resources::chunk-28` (0.0164), 5. `article_02_writing-test-resources::chunk-41` (0.0164) ✓ |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-16` (16.3493) ✓, 2. `article_02_writing-test-resources::chunk-11` (15.9521), 3. `article_02_writing-test-resources::chunk-12` (15.6001), 4. `article_02_writing-test-resources::chunk-20` (14.7945), 5. `article_02_writing-test-resources::chunk-30` (14.1857) |
| Dense | No | 1. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-0` (0.4924), 2. `article_02_writing-test-resources::chunk-20` (0.4878), 3. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.4794), 4. `article_04_ielts-academic-format-writing::chunk-10` (0.4543), 5. `article_02_writing-test-resources::chunk-5` (0.4470) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-20` (0.0318), 2. `article_02_writing-test-resources::chunk-11` (0.0306), 3. `article_02_writing-test-resources::chunk-16` (0.0164) ✓, 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-0` (0.0164), 5. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.0159) |

Evidence: At Band 7 or higher, the position should be clear and developed, with ideas leading to a logical conclusion.

### Q20 — Semantic paraphrases

> Which criterion concerns the large-scale organisation and logical flow of ideas, as opposed to the devices linking sentences?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-46` (24.3654) ✓, 2. `article_02_writing-test-resources::chunk-45` (19.3093), 3. `article_02_writing-test-resources::chunk-51` (17.4727), 4. `article_02_writing-test-resources::chunk-52` (17.2948), 5. `article_02_writing-test-resources::chunk-47` (17.2373) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-53` (0.7056), 2. `article_02_writing-test-resources::chunk-50` (0.6559), 3. `article_02_writing-test-resources::chunk-13` (0.6285), 4. `article_02_writing-test-resources::chunk-47` (0.6228), 5. `article_02_writing-test-resources::chunk-52` (0.5767) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-53` (0.0315), 2. `article_02_writing-test-resources::chunk-45` (0.0313), 3. `article_02_writing-test-resources::chunk-47` (0.0310), 4. `article_02_writing-test-resources::chunk-52` (0.0310), 5. `article_02_writing-test-resources::chunk-46` (0.0309) ✓ |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-19` (28.2693) ✓, 2. `article_02_writing-test-resources::chunk-22` (23.8818), 3. `article_02_writing-test-resources::chunk-21` (22.4911), 4. `article_02_writing-test-resources::chunk-4` (15.0567), 5. `article_04_ielts-academic-format-writing::chunk-2` (14.5511) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-22` (0.6322), 2. `article_02_writing-test-resources::chunk-19` (0.6320) ✓, 3. `article_02_writing-test-resources::chunk-21` (0.5905), 4. `article_02_writing-test-resources::chunk-20` (0.5502), 5. `article_02_writing-test-resources::chunk-28` (0.4612) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-19` (0.0325) ✓, 2. `article_02_writing-test-resources::chunk-22` (0.0325), 3. `article_02_writing-test-resources::chunk-21` (0.0317), 4. `article_02_writing-test-resources::chunk-5` (0.0303), 5. `article_04_ielts-academic-format-writing::chunk-2` (0.0301) |

Evidence: Coherence is structural linking and logical organisation; cohesion uses devices that clarify relationships within and between sentences.

### Q21 — Multi-constraint questions

> At which bands is paragraphing described as important for short Task 1 responses, and from which band is it expected in Task 2?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-48` (30.8731) ✓, 2. `article_02_writing-test-resources::chunk-57` (19.2712), 3. `article_04_ielts-academic-format-writing::chunk-8` (16.8525), 4. `article_02_writing-test-resources::chunk-56` (15.6207), 5. `article_03_academic-test::chunk-10` (14.8650) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-48` (0.8348) ✓, 2. `article_02_writing-test-resources::chunk-6` (0.6007), 3. `article_04_ielts-academic-format-writing::chunk-8` (0.5563), 4. `article_02_writing-test-resources::chunk-49` (0.5549), 5. `article_02_writing-test-resources::chunk-50` (0.5516) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-48` (0.0328) ✓, 2. `article_04_ielts-academic-format-writing::chunk-8` (0.0317), 3. `article_02_writing-test-resources::chunk-57` (0.0161), 4. `article_02_writing-test-resources::chunk-6` (0.0161), 5. `article_02_writing-test-resources::chunk-49` (0.0156) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-20` (28.1236) ✓, 2. `article_02_writing-test-resources::chunk-24` (20.0062), 3. `article_04_ielts-academic-format-writing::chunk-5` (18.1334), 4. `article_02_writing-test-resources::chunk-23` (17.6560), 5. `article_02_writing-test-resources::chunk-4` (16.6449) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-20` (0.6614) ✓, 2. `article_02_writing-test-resources::chunk-2` (0.5333), 3. `article_02_writing-test-resources::chunk-17` (0.5309), 4. `article_02_writing-test-resources::chunk-6` (0.5238), 5. `article_02_writing-test-resources::chunk-9` (0.5159) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-20` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-2` (0.0313), 3. `article_04_ielts-academic-format-writing::chunk-5` (0.0308), 4. `article_02_writing-test-resources::chunk-4` (0.0301), 5. `article_02_writing-test-resources::chunk-24` (0.0161) |

Evidence: For short Task 1 responses paragraphing matters only at Bands 8 and 9; Task 2 expects paragraphs from Band 6 and above.

### Q22 — BM25-targeted terms

> Which linking expressions can mark sequence, and which examples can signal a relationship such as result or contrast?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-54` (20.1364) ✓, 2. `article_02_writing-test-resources::chunk-52` (16.2574), 3. `article_02_writing-test-resources::chunk-51` (13.2678), 4. `article_02_writing-test-resources::chunk-7` (12.2657), 5. `article_02_writing-test-resources::chunk-49` (11.4629) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-54` (0.5519) ✓, 2. `article_02_writing-test-resources::chunk-51` (0.4633), 3. `article_02_writing-test-resources::chunk-53` (0.4614), 4. `article_02_writing-test-resources::chunk-52` (0.4382), 5. `article_02_writing-test-resources::chunk-47` (0.4301) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-54` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-51` (0.0320), 3. `article_02_writing-test-resources::chunk-52` (0.0318), 4. `article_02_writing-test-resources::chunk-53` (0.0159), 5. `article_02_writing-test-resources::chunk-7` (0.0156) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-22` (24.1261) ✓, 2. `article_02_writing-test-resources::chunk-2` (11.7267), 3. `article_02_writing-test-resources::chunk-21` (11.3852), 4. `article_04_ielts-academic-format-writing::chunk-10` (10.7435), 5. `article_02_writing-test-resources::chunk-20` (10.0016) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-22` (0.5593) ✓, 2. `article_02_writing-test-resources::chunk-21` (0.5072), 3. `article_02_writing-test-resources::chunk-19` (0.4462), 4. `article_02_writing-test-resources::chunk-20` (0.4107), 5. `article_02_writing-test-resources::chunk-26` (0.3438) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-22` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-21` (0.0320), 3. `article_02_writing-test-resources::chunk-20` (0.0310), 4. `article_02_writing-test-resources::chunk-19` (0.0308), 5. `article_02_writing-test-resources::chunk-2` (0.0161) |

Evidence: 'Firstly' and 'in conclusion' mark sequences; 'hence', 'as a result', 'although' and 'because' signal relationships.

### Q23 — BM25-targeted terms

> What kinds of reference forms can help an essay avoid repeating the same noun?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-52` (15.5676) ✓, 2. `article_02_writing-test-resources::chunk-67` (11.5948), 3. `article_02_writing-test-resources::chunk-11` (9.4474), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-10` (9.0957), 5. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-6` (8.5852) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-52` (0.5223) ✓, 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-9` (0.5140), 3. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-7` (0.4240), 4. `article_03_academic-test::chunk-19` (0.4159), 5. `article_02_writing-test-resources::chunk-63` (0.4152) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-52` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-63` (0.0301), 3. `article_02_writing-test-resources::chunk-8` (0.0294), 4. `article_02_writing-test-resources::chunk-67` (0.0161), 5. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-9` (0.0161) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-28` (12.2553), 2. `article_02_writing-test-resources::chunk-21` (11.6155) ✓, 3. `article_02_writing-test-resources::chunk-22` (8.8155), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-11` (8.6452), 5. `article_03_academic-test::chunk-1` (8.5946) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-26` (0.4723), 2. `article_02_writing-test-resources::chunk-23` (0.4285), 3. `article_02_writing-test-resources::chunk-25` (0.4158), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-13` (0.4127), 5. `article_02_writing-test-resources::chunk-21` (0.4025) ✓ |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-21` (0.0315) ✓, 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-11` (0.0303), 3. `article_02_writing-test-resources::chunk-26` (0.0164), 4. `article_02_writing-test-resources::chunk-28` (0.0164), 5. `article_02_writing-test-resources::chunk-23` (0.0161) |

Evidence: Reference and substitution include pronouns, relative pronouns and the definite article 'the'.

### Q24 — Multi-constraint questions

> What vocabulary capability separates a merely adequate Band 5 range from the level sought at higher bands?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-56` (20.9249) ✓, 2. `article_02_writing-test-resources::chunk-58` (13.7729), 3. `article_02_writing-test-resources::chunk-68` (11.8269), 4. `article_02_writing-test-resources::chunk-60` (10.9944), 5. `article_02_writing-test-resources::chunk-55` (10.3633) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-58` (0.7136), 2. `article_02_writing-test-resources::chunk-59` (0.5718), 3. `article_02_writing-test-resources::chunk-56` (0.5355) ✓, 4. `article_02_writing-test-resources::chunk-60` (0.5121), 5. `article_04_ielts-academic-format-writing::chunk-13` (0.4863) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-58` (0.0325), 2. `article_02_writing-test-resources::chunk-56` (0.0323) ✓, 3. `article_02_writing-test-resources::chunk-60` (0.0312), 4. `article_02_writing-test-resources::chunk-68` (0.0308), 5. `article_02_writing-test-resources::chunk-22` (0.0301) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-23` (19.3913) ✓, 2. `article_02_writing-test-resources::chunk-24` (13.5248), 3. `article_02_writing-test-resources::chunk-29` (11.8063), 4. `article_02_writing-test-resources::chunk-5` (10.4801), 5. `article_02_writing-test-resources::chunk-28` (9.9476) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-24` (0.5955), 2. `article_02_writing-test-resources::chunk-23` (0.4838) ✓, 3. `article_02_writing-test-resources::chunk-25` (0.4629), 4. `article_02_writing-test-resources::chunk-26` (0.4407), 5. `article_02_writing-test-resources::chunk-29` (0.4185) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-23` (0.0325) ✓, 2. `article_02_writing-test-resources::chunk-24` (0.0325), 3. `article_02_writing-test-resources::chunk-29` (0.0313), 4. `article_02_writing-test-resources::chunk-5` (0.0308), 5. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.0301) |

Evidence: Band 5 may have a minimally adequate range; higher bands require flexible use of wider vocabulary, including synonyms and collocations.

### Q25 — Semantic paraphrases

> What is wrong when a word sounds unnatural in its context or is too informal for the situation, and what related vocabulary issue may occur?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-61` (28.9769) ✓, 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-12` (23.6790), 3. `article_02_writing-test-resources::chunk-63` (17.5072), 4. `article_02_writing-test-resources::chunk-62` (16.8317), 5. `article_02_writing-test-resources::chunk-60` (16.1926) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-61` (0.7548) ✓, 2. `article_02_writing-test-resources::chunk-63` (0.4428), 3. `article_02_writing-test-resources::chunk-57` (0.4141), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-12` (0.4119), 5. `article_02_writing-test-resources::chunk-62` (0.4067) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-61` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-63` (0.0320), 3. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-12` (0.0318), 4. `article_02_writing-test-resources::chunk-62` (0.0310), 5. `article_02_writing-test-resources::chunk-60` (0.0303) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-25` (28.7710) ✓, 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-13` (24.7142), 3. `article_02_writing-test-resources::chunk-26` (22.0992), 4. `article_02_writing-test-resources::chunk-24` (18.1046), 5. `article_02_writing-test-resources::chunk-23` (17.6417) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-25` (0.5691) ✓, 2. `article_02_writing-test-resources::chunk-26` (0.4196), 3. `article_02_writing-test-resources::chunk-24` (0.3474), 4. `article_02_writing-test-resources::chunk-23` (0.2926), 5. `article_02_writing-test-resources::chunk-30` (0.2454) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-25` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-26` (0.0320), 3. `article_02_writing-test-resources::chunk-24` (0.0315), 4. `article_02_writing-test-resources::chunk-23` (0.0310), 5. `article_02_writing-test-resources::chunk-29` (0.0290) |

Evidence: These are lexical inappropriacies; inaccurate collocations, where words are not normally used together, may also occur.

### Q26 — Semantic paraphrases

> How severe must a spelling or word-formation problem become before it limits the Lexical Resource score to Band 5?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-60` (20.7833) ✓, 2. `article_02_writing-test-resources::chunk-54` (11.9885), 3. `article_02_writing-test-resources::chunk-56` (11.7774), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-10` (11.7435), 5. `article_02_writing-test-resources::chunk-1` (11.5397) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-60` (0.8007) ✓, 2. `article_02_writing-test-resources::chunk-59` (0.5424), 3. `article_02_writing-test-resources::chunk-58` (0.5112), 4. `article_04_ielts-academic-format-writing::chunk-8` (0.5109), 5. `article_02_writing-test-resources::chunk-55` (0.5105) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-60` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-56` (0.0310), 3. `article_02_writing-test-resources::chunk-68` (0.0299), 4. `article_02_writing-test-resources::chunk-62` (0.0292), 5. `article_02_writing-test-resources::chunk-54` (0.0161) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-25` (18.1672) ✓, 2. `article_02_writing-test-resources::chunk-23` (16.2678), 3. `article_02_writing-test-resources::chunk-26` (13.5248), 4. `article_02_writing-test-resources::chunk-24` (12.4534), 5. `article_02_writing-test-resources::chunk-29` (12.0051) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-25` (0.6380) ✓, 2. `article_02_writing-test-resources::chunk-24` (0.6305), 3. `article_02_writing-test-resources::chunk-26` (0.5949), 4. `article_02_writing-test-resources::chunk-23` (0.5731), 5. `article_02_writing-test-resources::chunk-29` (0.5522) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-25` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-23` (0.0318), 3. `article_02_writing-test-resources::chunk-24` (0.0318), 4. `article_02_writing-test-resources::chunk-26` (0.0317), 5. `article_02_writing-test-resources::chunk-29` (0.0308) |

Evidence: A serious error prevents communication; noticeable spelling or word-formation errors that cause reader difficulty limit Lexical Resource to Band 5.

### Q27 — BM25-targeted terms

> Under the grammar criterion, what clause structure distinguishes a complex sentence from a simple sentence?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-66` (24.4777) ✓, 2. `article_02_writing-test-resources::chunk-65` (19.6736), 3. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-10` (16.5950), 4. `article_03_academic-test::chunk-17` (12.7738), 5. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-12` (12.7314) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-66` (0.6082) ✓, 2. `article_02_writing-test-resources::chunk-67` (0.5149), 3. `article_02_writing-test-resources::chunk-50` (0.3644), 4. `article_02_writing-test-resources::chunk-53` (0.3611), 5. `article_02_writing-test-resources::chunk-73` (0.3599) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-66` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-65` (0.0304), 3. `article_02_writing-test-resources::chunk-67` (0.0161), 4. `article_02_writing-test-resources::chunk-50` (0.0159), 5. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-10` (0.0159) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-28` (28.4490) ✓, 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-11` (15.0435), 3. `article_03_academic-test::chunk-9` (12.1037), 4. `article_03_academic-test::chunk-21` (12.0479), 5. `article_03_academic-test::chunk-20` (11.0970) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-28` (0.5799) ✓, 2. `article_02_writing-test-resources::chunk-21` (0.3970), 3. `article_02_writing-test-resources::chunk-20` (0.3528), 4. `article_02_writing-test-resources::chunk-22` (0.3493), 5. `article_02_writing-test-resources::chunk-19` (0.3218) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-28` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-29` (0.0301), 3. `article_02_writing-test-resources::chunk-30` (0.0290), 4. `article_02_writing-test-resources::chunk-5` (0.0290), 5. `article_02_writing-test-resources::chunk-21` (0.0161) |

Evidence: A simple sentence has one independent clause; a complex sentence has a main clause and one or more subordinate clauses.

### Q28 — BM25-targeted terms

> Name examples of more complex phrasing within sentences that count toward grammatical range.

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-67` (18.6210) ✓, 2. `article_02_writing-test-resources::chunk-65` (15.5812), 3. `article_02_writing-test-resources::chunk-66` (12.0961), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-10` (11.5701), 5. `article_02_writing-test-resources::chunk-73` (10.3853) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-73` (0.6221), 2. `article_04_ielts-academic-format-writing::chunk-6` (0.5909), 3. `article_02_writing-test-resources::chunk-67` (0.5670) ✓, 4. `article_02_writing-test-resources::chunk-65` (0.5373), 5. `article_02_writing-test-resources::chunk-66` (0.5154) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-67` (0.0323) ✓, 2. `article_02_writing-test-resources::chunk-73` (0.0318), 3. `article_02_writing-test-resources::chunk-65` (0.0318), 4. `article_02_writing-test-resources::chunk-66` (0.0313), 5. `article_02_writing-test-resources::chunk-63` (0.0296) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-28` (23.3110) ✓, 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-11` (10.9494), 3. `article_02_writing-test-resources::chunk-5` (10.6439), 4. `article_02_writing-test-resources::chunk-31` (8.9551), 5. `article_02_writing-test-resources::chunk-21` (8.1128) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-28` (0.6050) ✓, 2. `article_02_writing-test-resources::chunk-31` (0.4505), 3. `article_02_writing-test-resources::chunk-21` (0.4356), 4. `article_04_ielts-academic-format-writing::chunk-3` (0.4294), 5. `article_02_writing-test-resources::chunk-29` (0.3940) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-28` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-31` (0.0318), 3. `article_02_writing-test-resources::chunk-21` (0.0313), 4. `article_04_ielts-academic-format-writing::chunk-3` (0.0303), 5. `article_02_writing-test-resources::chunk-30` (0.0294) |

Evidence: Examples include passive forms, modal verbs, comparative structures and complex noun phrases.

### Q29 — Multi-constraint questions

> At Band 8, how does IELTS distinguish an occasional grammar slip from a repeated pattern, and why is that distinction different at Band 7?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-69` (21.9112), 2. `article_02_writing-test-resources::chunk-70` (20.3548) ✓, 3. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-14` (17.4617), 4. `article_02_writing-test-resources::chunk-15` (16.5127), 5. `article_02_writing-test-resources::chunk-22` (13.8308) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-64` (0.5469), 2. `article_02_writing-test-resources::chunk-65` (0.5437), 3. `article_02_writing-test-resources::chunk-14` (0.5102), 4. `article_02_writing-test-resources::chunk-69` (0.4946), 5. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-14` (0.4944) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-69` (0.0320), 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-14` (0.0313), 3. `article_02_writing-test-resources::chunk-70` (0.0308) ✓, 4. `article_02_writing-test-resources::chunk-65` (0.0306), 5. `article_02_writing-test-resources::chunk-64` (0.0164) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-29` (18.7090), 2. `article_02_writing-test-resources::chunk-5` (18.4359), 3. `article_02_writing-test-resources::chunk-30` (17.0809) ✓, 4. `article_02_writing-test-resources::chunk-20` (14.1722), 5. `article_02_writing-test-resources::chunk-8` (13.6108) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-28` (0.5248), 2. `article_02_writing-test-resources::chunk-29` (0.5223), 3. `article_02_writing-test-resources::chunk-31` (0.5214), 4. `article_02_writing-test-resources::chunk-5` (0.5068), 5. `article_04_ielts-academic-format-writing::chunk-3` (0.4921) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-29` (0.0325), 2. `article_02_writing-test-resources::chunk-5` (0.0318), 3. `article_02_writing-test-resources::chunk-28` (0.0307), 4. `article_02_writing-test-resources::chunk-30` (0.0304) ✓, 5. `article_02_writing-test-resources::chunk-25` (0.0292) |

Evidence: Non-systematic errors are occasional; this distinction is not important for Band 7 but is important for Band 8, where most sentences should be error-free.

### Q30 — Semantic paraphrases

> For Academic Writing, is typing the only available way to take the test, or may a paper response be an option in some locations?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_03_academic-test::chunk-24` (17.0653), 2. `article_02_writing-test-resources::chunk-74` (16.9718), 3. `article_02_writing-test-resources::chunk-68` (16.3477), 4. `article_02_writing-test-resources::chunk-4` (15.9316), 5. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-15` (15.7204) |
| Dense | No | 1. `article_04_ielts-academic-format-writing::chunk-2` (0.5492), 2. `article_03_academic-test::chunk-20` (0.5353), 3. `article_04_ielts-academic-format-writing::chunk-0` (0.5238), 4. `article_02_writing-test-resources::chunk-5` (0.5146), 5. `article_02_writing-test-resources::chunk-11` (0.4993) |
| Hybrid (RRF) | Yes | 1. `article_03_academic-test::chunk-24` (0.0311), 2. `article_02_writing-test-resources::chunk-75` (0.0294), 3. `article_03_academic-test::chunk-2` (0.0290) ✓, 4. `article_04_ielts-academic-format-writing::chunk-2` (0.0164), 5. `article_02_writing-test-resources::chunk-74` (0.0161) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_04_ielts-academic-format-writing::chunk-9` (20.1259), 2. `article_04_ielts-academic-format-writing::chunk-5` (18.9967), 3. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-15` (18.6246), 4. `article_02_writing-test-resources::chunk-29` (18.1319), 5. `article_03_academic-test::chunk-2` (17.1721) ✓ |
| Dense | Yes | 1. `article_03_academic-test::chunk-2` (0.5788) ✓, 2. `article_02_writing-test-resources::chunk-1` (0.5470), 3. `article_03_academic-test::chunk-23` (0.5431), 4. `article_04_ielts-academic-format-writing::chunk-1` (0.5187), 5. `article_03_academic-test::chunk-26` (0.5030) |
| Hybrid (RRF) | Yes | 1. `article_03_academic-test::chunk-2` (0.0318) ✓, 2. `article_02_writing-test-resources::chunk-1` (0.0313), 3. `article_04_ielts-academic-format-writing::chunk-1` (0.0299), 4. `article_04_ielts-academic-format-writing::chunk-9` (0.0164), 5. `article_04_ielts-academic-format-writing::chunk-5` (0.0161) |

Evidence: IELTS Academic is delivered on computer; for Writing, candidates may also choose Writing on Paper where available.

## Limits

The corpus currently has five IELTS pages and does not include all eight planned sources. The benchmark's dense model is `all-mpnet-base-v2`, while production Task 4 defaults to `BAAI/bge-m3`; use the same benchmark with BGE-M3 before treating dense/hybrid numbers as production estimates. Retrieval scores are not comparable across methods; only ranked evidence matches are compared.
