# Chunking and retrieval comparison: 30 IELTS Writing questions

## Corpus analysis and chunking choice

- Corpus: 5 standardized IELTS Writing Markdown pages. The pages use nested headings, paragraphs, and lists; the longest article contains long criterion explanations and examples.
- Legacy: recursive character splitting, 500 characters with 50-character overlap; 137 chunks.
- Updated: Markdown heading-path-aware recursive splitting, 1200 characters maximum including a repeated `Section:` breadcrumb, zero overlap, and paragraph/list grouping; 95 chunks.
- Chunk content length: legacy average 413 / median 431 characters; updated average 659 / median 547 characters.
- Reason: heading context prevents chunks from becoming detached from the IELTS criterion/task they describe. Paragraph/list grouping keeps self-contained guidance together. Zero overlap avoids indexing repeated content; document sections already carry context.
- Gold relevance is determined from exact evidence spans in the corpus, normalized for crawler replacement/zero-width characters and whitespace. This makes labels independent of chunk IDs and permits a fair comparison across boundaries.
- Query language: Vietnamese; corpus evidence remains in the source language (English). Vietnamese query results therefore measure cross-language retrieval.
- Dense: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` Sentence Transformers embeddings with normalized cosine vectors. Sparse: the project's BM25 implementation. Hybrid: RRF (`k=60`) from each method's top 10, output top 5.
- Metrics are macro averages across the same 30 queries. Hit@k means a chunk containing a complete accepted evidence span appears in the first k. This evaluates chunk match, not generated answer correctness or citation quality.

## Aggregate chunk-match results

| Chunker | Method | Hit@1 | Hit@3 | Hit@5 | MRR@5 |
|---|---|---:|---:|---:|---:|
| Legacy recursive 500/50 | Sparse (BM25) | 0.133 | 0.200 | 0.333 | 0.184 |
| Legacy recursive 500/50 | Dense | 0.367 | 0.633 | 0.667 | 0.492 |
| Legacy recursive 500/50 | Hybrid (RRF) | 0.367 | 0.567 | 0.600 | 0.464 |
| Markdown section-aware 1200/0 | Sparse (BM25) | 0.100 | 0.333 | 0.333 | 0.211 |
| Markdown section-aware 1200/0 | Dense | 0.233 | 0.433 | 0.533 | 0.334 |
| Markdown section-aware 1200/0 | Hybrid (RRF) | 0.233 | 0.433 | 0.600 | 0.366 |

## Change by retrieval method

| Method | Δ Hit@1 | Δ Hit@3 | Δ Hit@5 | Δ MRR@5 |
|---|---:|---:|---:|---:|
| Sparse (BM25) | -0.033 | +0.133 | +0.000 | +0.027 |
| Dense | -0.133 | -0.200 | -0.133 | -0.157 |
| Hybrid (RRF) | -0.133 | -0.133 | +0.000 | -0.098 |

## Reading the result

Updated versus legacy Hit@5: BM25 +0.000, dense -0.133, hybrid +0.000. These measured results describe this dataset and embedder only; they do not guarantee that hybrid ranks first for every query. For Vietnamese questions against English source chunks, evaluate a bilingual embedder and query translation as separate configurations before selecting production behavior.

## Scores by question challenge

| Challenge | Chunker | Method | Hit@1 | Hit@5 | MRR@5 |
|---|---|---|---:|---:|---:|
| BM25-targeted terms | Legacy recursive 500/50 | Sparse (BM25) | 0.000 | 0.100 | 0.033 |
| BM25-targeted terms | Legacy recursive 500/50 | Dense | 0.400 | 0.700 | 0.533 |
| BM25-targeted terms | Legacy recursive 500/50 | Hybrid (RRF) | 0.400 | 0.700 | 0.517 |
| BM25-targeted terms | Markdown section-aware 1200/0 | Sparse (BM25) | 0.000 | 0.200 | 0.100 |
| BM25-targeted terms | Markdown section-aware 1200/0 | Dense | 0.000 | 0.400 | 0.137 |
| BM25-targeted terms | Markdown section-aware 1200/0 | Hybrid (RRF) | 0.000 | 0.500 | 0.183 |
| Semantic paraphrases | Legacy recursive 500/50 | Sparse (BM25) | 0.200 | 0.300 | 0.220 |
| Semantic paraphrases | Legacy recursive 500/50 | Dense | 0.400 | 0.700 | 0.508 |
| Semantic paraphrases | Legacy recursive 500/50 | Hybrid (RRF) | 0.300 | 0.500 | 0.375 |
| Semantic paraphrases | Markdown section-aware 1200/0 | Sparse (BM25) | 0.200 | 0.400 | 0.283 |
| Semantic paraphrases | Markdown section-aware 1200/0 | Dense | 0.300 | 0.700 | 0.433 |
| Semantic paraphrases | Markdown section-aware 1200/0 | Hybrid (RRF) | 0.400 | 0.700 | 0.525 |
| Multi-constraint questions | Legacy recursive 500/50 | Sparse (BM25) | 0.200 | 0.600 | 0.298 |
| Multi-constraint questions | Legacy recursive 500/50 | Dense | 0.300 | 0.600 | 0.433 |
| Multi-constraint questions | Legacy recursive 500/50 | Hybrid (RRF) | 0.400 | 0.600 | 0.500 |
| Multi-constraint questions | Markdown section-aware 1200/0 | Sparse (BM25) | 0.100 | 0.400 | 0.250 |
| Multi-constraint questions | Markdown section-aware 1200/0 | Dense | 0.400 | 0.500 | 0.433 |
| Multi-constraint questions | Markdown section-aware 1200/0 | Hybrid (RRF) | 0.300 | 0.600 | 0.390 |

## Per-question chunk match

‘✓’ marks a chunk that contains a complete gold evidence span.

### Q01 — BM25-targeted terms

> Trong điểm Writing tổng thể, Task nào có trọng số lớn hơn và chiếm bao nhiêu?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_03_academic-test::chunk-20` (0.9234), 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-3` (0.8583), 3. `article_02_writing-test-resources::chunk-3` (0.8357), 4. `article_04_ielts-academic-format-writing::chunk-0` (0.8212), 5. `article_04_ielts-academic-format-writing::chunk-6` (0.8004) |
| Dense | No | 1. `article_04_ielts-academic-format-writing::chunk-6` (0.6983), 2. `article_04_ielts-academic-format-writing::chunk-11` (0.6884), 3. `article_02_writing-test-resources::chunk-48` (0.6655), 4. `article_02_writing-test-resources::chunk-35` (0.6604), 5. `article_02_writing-test-resources::chunk-44` (0.6509) |
| Hybrid (RRF) | No | 1. `article_04_ielts-academic-format-writing::chunk-6` (0.0318), 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-3` (0.0306), 3. `article_03_academic-test::chunk-20` (0.0164), 4. `article_04_ielts-academic-format-writing::chunk-11` (0.0161), 5. `article_02_writing-test-resources::chunk-3` (0.0159) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_03_academic-test::chunk-23` (3.3130), 2. `article_04_ielts-academic-format-writing::chunk-4` (3.1626), 3. `article_02_writing-test-resources::chunk-14` (3.1286), 4. `article_04_ielts-academic-format-writing::chunk-2` (3.0770), 5. `article_02_writing-test-resources::chunk-0` (3.0396) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-9` (0.6623), 2. `article_02_writing-test-resources::chunk-14` (0.6450), 3. `article_02_writing-test-resources::chunk-11` (0.6172), 4. `article_02_writing-test-resources::chunk-13` (0.6135), 5. `article_02_writing-test-resources::chunk-8` (0.6038) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-14` (0.0320), 2. `article_02_writing-test-resources::chunk-9` (0.0307), 3. `article_02_writing-test-resources::chunk-18` (0.0296), 4. `article_03_academic-test::chunk-23` (0.0164), 5. `article_04_ielts-academic-format-writing::chunk-4` (0.0161) |

Evidence: Task 2 contributes two thirds of the overall Writing mark, while Task 1 contributes one third.

### Q02 — Multi-constraint questions

> Hai bài Academic Writing yêu cầu tối thiểu bao nhiêu từ và thời gian làm bài khoảng bao lâu?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_03_academic-test::chunk-20` (2.7523), 2. `article_04_ielts-academic-format-writing::chunk-0` (2.6496), 3. `article_03_academic-test::chunk-24` (2.4597), 4. `article_03_academic-test::chunk-18` (2.4349), 5. `article_03_academic-test::chunk-19` (2.2791) |
| Dense | Yes | 1. `article_04_ielts-academic-format-writing::chunk-11` (0.7487), 2. `article_02_writing-test-resources::chunk-6` (0.7058) ✓, 3. `article_04_ielts-academic-format-writing::chunk-6` (0.6719), 4. `article_04_ielts-academic-format-writing::chunk-8` (0.6621), 5. `article_04_ielts-academic-format-writing::chunk-13` (0.6564) |
| Hybrid (RRF) | No | 1. `article_03_academic-test::chunk-20` (0.0309), 2. `article_04_ielts-academic-format-writing::chunk-6` (0.0306), 3. `article_03_academic-test::chunk-19` (0.0301), 4. `article_03_academic-test::chunk-21` (0.0292), 5. `article_04_ielts-academic-format-writing::chunk-11` (0.0164) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_03_academic-test::chunk-23` (3.6098), 2. `article_03_academic-test::chunk-2` (3.3240), 3. `article_04_ielts-academic-format-writing::chunk-0` (3.2694), 4. `article_04_ielts-academic-format-writing::chunk-4` (3.1626), 5. `article_04_ielts-academic-format-writing::chunk-8` (3.1408) |
| Dense | Yes | 1. `article_04_ielts-academic-format-writing::chunk-1` (0.6131) ✓, 2. `article_02_writing-test-resources::chunk-2` (0.6062) ✓, 3. `article_04_ielts-academic-format-writing::chunk-4` (0.5898), 4. `article_03_academic-test::chunk-23` (0.5827), 5. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-2` (0.5578) |
| Hybrid (RRF) | Yes | 1. `article_03_academic-test::chunk-23` (0.0320), 2. `article_04_ielts-academic-format-writing::chunk-4` (0.0315), 3. `article_04_ielts-academic-format-writing::chunk-8` (0.0299), 4. `article_04_ielts-academic-format-writing::chunk-13` (0.0296), 5. `article_04_ielts-academic-format-writing::chunk-1` (0.0164) ✓ |

Evidence: Task 1: at least 150 words and about 20 minutes. Task 2: at least 250 words and about 40 minutes.

### Q03 — Semantic paraphrases

> Khi mô tả biểu đồ ở Academic Task 1, cần chọn và trình bày điều gì, và khi nào nên so sánh?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_02_writing-test-resources::chunk-6` (4.8284), 2. `article_02_writing-test-resources::chunk-55` (4.0030), 3. `article_03_academic-test::chunk-14` (3.8953), 4. `article_02_writing-test-resources::chunk-5` (3.8377), 5. `article_03_academic-test::chunk-13` (3.6380) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-7` (0.7206), 2. `article_04_ielts-academic-format-writing::chunk-4` (0.6766), 3. `article_03_academic-test::chunk-19` (0.6643), 4. `article_02_writing-test-resources::chunk-12` (0.6345), 5. `article_02_writing-test-resources::chunk-37` (0.6259) |
| Hybrid (RRF) | No | 1. `article_04_ielts-academic-format-writing::chunk-6` (0.0296), 2. `article_02_writing-test-resources::chunk-6` (0.0164), 3. `article_02_writing-test-resources::chunk-7` (0.0164), 4. `article_02_writing-test-resources::chunk-55` (0.0161), 5. `article_04_ielts-academic-format-writing::chunk-4` (0.0161) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_02_writing-test-resources::chunk-2` (5.5371), 2. `article_03_academic-test::chunk-16` (4.3074), 3. `article_03_academic-test::chunk-17` (4.2871), 4. `article_03_academic-test::chunk-15` (4.2347), 5. `article_03_academic-test::chunk-12` (4.1696) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-9` (0.6991), 2. `article_02_writing-test-resources::chunk-8` (0.6445), 3. `article_02_writing-test-resources::chunk-17` (0.6089), 4. `article_03_academic-test::chunk-22` (0.6051), 5. `article_02_writing-test-resources::chunk-13` (0.5908) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-2` (0.0164), 2. `article_02_writing-test-resources::chunk-9` (0.0164), 3. `article_02_writing-test-resources::chunk-8` (0.0161), 4. `article_03_academic-test::chunk-16` (0.0161), 5. `article_02_writing-test-resources::chunk-17` (0.0159) |

Evidence: Summarise the information by selecting and reporting its main features; make comparisons where relevant.

### Q04 — BM25-targeted terms

> Trong thư General Training Task 1, tình huống và người nhận quyết định thế nào giữa giọng thân mật, bán trang trọng và trang trọng?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-9` (7.9477), 2. `article_02_writing-test-resources::chunk-25` (6.1499), 3. `article_02_writing-test-resources::chunk-26` (5.4615) ✓, 4. `article_03_academic-test::chunk-22` (5.3291), 5. `article_02_writing-test-resources::chunk-35` (5.1603) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-35` (0.6337), 2. `article_02_writing-test-resources::chunk-25` (0.5566), 3. `article_02_writing-test-resources::chunk-26` (0.5496) ✓, 4. `article_02_writing-test-resources::chunk-37` (0.5429), 5. `article_02_writing-test-resources::chunk-44` (0.5384) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-25` (0.0323), 2. `article_02_writing-test-resources::chunk-35` (0.0318), 3. `article_02_writing-test-resources::chunk-26` (0.0317) ✓, 4. `article_02_writing-test-resources::chunk-55` (0.0294), 5. `article_02_writing-test-resources::chunk-9` (0.0164) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-14` (7.0141), 2. `article_02_writing-test-resources::chunk-10` (6.0447) ✓, 3. `article_02_writing-test-resources::chunk-3` (5.2024) ✓, 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-0` (4.7336), 5. `article_03_academic-test::chunk-24` (4.1474) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-12` (0.6226), 2. `article_02_writing-test-resources::chunk-14` (0.6218), 3. `article_02_writing-test-resources::chunk-10` (0.5613) ✓, 4. `article_02_writing-test-resources::chunk-11` (0.5440), 5. `article_02_writing-test-resources::chunk-17` (0.5351) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-14` (0.0325), 2. `article_02_writing-test-resources::chunk-10` (0.0320) ✓, 3. `article_02_writing-test-resources::chunk-12` (0.0309), 4. `article_02_writing-test-resources::chunk-11` (0.0306), 5. `article_02_writing-test-resources::chunk-15` (0.0288) |

Evidence: The situation determines whether the letter is personal (for example, to a friend), semi-formal (to a manager), or formal (to someone not personally known).

### Q05 — BM25-targeted terms

> Ở Task 2, tiêu chí Task Response đánh giá những khía cạnh nào trong việc trả lời đề và phát triển ý chính?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_02_writing-test-resources::chunk-48` (3.8084), 2. `article_04_ielts-academic-format-writing::chunk-3` (3.7201), 3. `article_04_ielts-academic-format-writing::chunk-4` (3.2829), 4. `article_02_writing-test-resources::chunk-1` (3.1085), 5. `article_02_writing-test-resources::chunk-43` (2.7223) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-44` (0.8406), 2. `article_02_writing-test-resources::chunk-12` (0.8144) ✓, 3. `article_04_ielts-academic-format-writing::chunk-4` (0.8079), 4. `article_02_writing-test-resources::chunk-37` (0.7565), 5. `article_02_writing-test-resources::chunk-36` (0.7359) |
| Hybrid (RRF) | Yes | 1. `article_04_ielts-academic-format-writing::chunk-4` (0.0317), 2. `article_02_writing-test-resources::chunk-12` (0.0313) ✓, 3. `article_02_writing-test-resources::chunk-48` (0.0311), 4. `article_02_writing-test-resources::chunk-44` (0.0164), 5. `article_04_ielts-academic-format-writing::chunk-3` (0.0161) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_04_ielts-academic-format-writing::chunk-2` (6.6805), 2. `article_02_writing-test-resources::chunk-4` (5.5142) ✓, 3. `article_02_writing-test-resources::chunk-20` (5.3816), 4. `article_02_writing-test-resources::chunk-17` (5.2965), 5. `article_02_writing-test-resources::chunk-0` (5.2105) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-18` (0.7473), 2. `article_02_writing-test-resources::chunk-17` (0.7420), 3. `article_02_writing-test-resources::chunk-9` (0.6781), 4. `article_02_writing-test-resources::chunk-15` (0.6755), 5. `article_02_writing-test-resources::chunk-13` (0.6714) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-17` (0.0318), 2. `article_02_writing-test-resources::chunk-18` (0.0309), 3. `article_04_ielts-academic-format-writing::chunk-2` (0.0164), 4. `article_02_writing-test-resources::chunk-4` (0.0161) ✓, 5. `article_02_writing-test-resources::chunk-20` (0.0159) |

Evidence: Task Response is used for Task 2; it assesses completeness of the response and how main ideas are extended and supported. Task Achievement is used for Task 1.

### Q06 — Multi-constraint questions

> Tài liệu phân biệt Coherence and Cohesion với Lexical Resource ra sao, nhất là về cách tổ chức ý và lựa chọn từ?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-2` (12.5841), 2. `article_04_ielts-academic-format-writing::chunk-5` (11.7973), 3. `article_04_ielts-academic-format-writing::chunk-3` (11.2196), 4. `article_02_writing-test-resources::chunk-1` (11.1238), 5. `article_02_writing-test-resources::chunk-13` (11.0566) ✓ |
| Dense | Yes | 1. `article_04_ielts-academic-format-writing::chunk-5` (0.7969), 2. `article_02_writing-test-resources::chunk-46` (0.7166), 3. `article_02_writing-test-resources::chunk-13` (0.7162) ✓, 4. `article_02_writing-test-resources::chunk-45` (0.6798), 5. `article_02_writing-test-resources::chunk-51` (0.6658) |
| Hybrid (RRF) | Yes | 1. `article_04_ielts-academic-format-writing::chunk-5` (0.0325), 2. `article_02_writing-test-resources::chunk-13` (0.0313) ✓, 3. `article_02_writing-test-resources::chunk-46` (0.0311), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-2` (0.0309), 5. `article_02_writing-test-resources::chunk-45` (0.0308) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_04_ielts-academic-format-writing::chunk-2` (12.1581), 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-1` (10.1071), 3. `article_02_writing-test-resources::chunk-19` (9.8227), 4. `article_02_writing-test-resources::chunk-22` (8.3504), 5. `article_02_writing-test-resources::chunk-0` (8.3173) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-21` (0.7498), 2. `article_02_writing-test-resources::chunk-22` (0.6942), 3. `article_02_writing-test-resources::chunk-19` (0.6419), 4. `article_02_writing-test-resources::chunk-26` (0.6321), 5. `article_02_writing-test-resources::chunk-20` (0.5229) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-22` (0.0318), 2. `article_02_writing-test-resources::chunk-19` (0.0317), 3. `article_02_writing-test-resources::chunk-21` (0.0315), 4. `article_02_writing-test-resources::chunk-20` (0.0301), 5. `article_02_writing-test-resources::chunk-23` (0.0301) |

Evidence: Coherence and Cohesion concerns organisation, logical development and links; Lexical Resource concerns vocabulary range, accuracy and appropriacy.

### Q07 — Semantic paraphrases

> Người học có thể tra cứu tài liệu công bố nào để đối chiếu đầy đủ band descriptor và tiêu chí đánh giá IELTS Writing?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (4.3768) ✓, 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-14` (3.2933), 3. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-1` (3.2258), 4. `article_03_academic-test::chunk-20` (3.1345), 5. `article_04_ielts-academic-format-writing::chunk-0` (2.4455) |
| Dense | Yes | 1. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.7608) ✓, 2. `article_02_writing-test-resources::chunk-14` (0.7197), 3. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-1` (0.6960), 4. `article_02_writing-test-resources::chunk-2` (0.6628), 5. `article_04_ielts-academic-format-writing::chunk-0` (0.6461) |
| Hybrid (RRF) | Yes | 1. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.0328) ✓, 2. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-1` (0.0317), 3. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-14` (0.0313), 4. `article_04_ielts-academic-format-writing::chunk-0` (0.0308), 5. `article_02_writing-test-resources::chunk-14` (0.0161) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (5.6149) ✓, 2. `article_03_academic-test::chunk-23` (4.6745), 3. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-1` (4.3269), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-14` (4.1697), 5. `article_02_writing-test-resources::chunk-5` (4.0339) |
| Dense | Yes | 1. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.7501) ✓, 2. `article_04_ielts-academic-format-writing::chunk-0` (0.7033), 3. `article_04_ielts-academic-format-writing::chunk-6` (0.6936), 4. `article_04_ielts-academic-format-writing::chunk-2` (0.6811), 5. `article_04_ielts-academic-format-writing::chunk-3` (0.6746) |
| Hybrid (RRF) | Yes | 1. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.0328) ✓, 2. `article_04_ielts-academic-format-writing::chunk-0` (0.0308), 3. `article_02_writing-test-resources::chunk-5` (0.0303), 4. `article_04_ielts-academic-format-writing::chunk-5` (0.0294), 5. `article_03_academic-test::chunk-23` (0.0161) |

Evidence: The full assessment scales used by Writing examiners, including the band descriptors and detailed key assessment criteria, were made available.

### Q08 — Multi-constraint questions

> Khi lập kế hoạch cho bài Task 2, thời gian được khuyến nghị chia thế nào giữa đọc và lập dàn ý, viết nháp, rồi soát bài?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_04_ielts-academic-format-writing::chunk-6` (2.4285), 2. `article_02_writing-test-resources::chunk-48` (2.1553), 3. `article_02_writing-test-resources::chunk-6` (2.1473), 4. `article_04_ielts-academic-format-writing::chunk-3` (2.0950), 5. `article_02_writing-test-resources::chunk-1` (2.0934) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-6` (0.6571), 2. `article_04_ielts-academic-format-writing::chunk-6` (0.6364), 3. `article_02_writing-test-resources::chunk-48` (0.6245), 4. `article_03_academic-test::chunk-11` (0.6204), 5. `article_02_writing-test-resources::chunk-44` (0.5946) |
| Hybrid (RRF) | No | 1. `article_04_ielts-academic-format-writing::chunk-6` (0.0325), 2. `article_02_writing-test-resources::chunk-6` (0.0323), 3. `article_02_writing-test-resources::chunk-48` (0.0320), 4. `article_04_ielts-academic-format-writing::chunk-11` (0.0294), 5. `article_03_academic-test::chunk-20` (0.0294) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_04_ielts-academic-format-writing::chunk-4` (3.4453), 2. `article_02_writing-test-resources::chunk-2` (3.2901), 3. `article_03_academic-test::chunk-23` (3.2893), 4. `article_04_ielts-academic-format-writing::chunk-2` (3.2719), 5. `article_03_academic-test::chunk-20` (2.9767) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-18` (0.6011), 2. `article_02_writing-test-resources::chunk-17` (0.5664), 3. `article_04_ielts-academic-format-writing::chunk-4` (0.5556), 4. `article_02_writing-test-resources::chunk-4` (0.5459), 5. `article_02_writing-test-resources::chunk-2` (0.5453) |
| Hybrid (RRF) | No | 1. `article_04_ielts-academic-format-writing::chunk-4` (0.0323), 2. `article_02_writing-test-resources::chunk-2` (0.0315), 3. `article_03_academic-test::chunk-23` (0.0304), 4. `article_02_writing-test-resources::chunk-18` (0.0164), 5. `article_02_writing-test-resources::chunk-17` (0.0161) |

Evidence: The breakdown is 5–10 minutes for reading/planning, 15–20 minutes for the first draft, and 10 minutes for proofreading/editing.

### Q09 — Multi-constraint questions

> Dàn ý bài luận khuyến nghị cấu trúc các đoạn thế nào, gồm bao nhiêu đoạn thân bài và mỗi đoạn đảm nhiệm việc gì?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-43` (0.6066), 2. `article_02_writing-test-resources::chunk-17` (0.5852), 3. `article_02_writing-test-resources::chunk-48` (0.5814), 4. `article_02_writing-test-resources::chunk-18` (0.5812), 5. `article_02_writing-test-resources::chunk-50` (0.5811) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-43` (0.0164), 2. `article_02_writing-test-resources::chunk-17` (0.0161), 3. `article_02_writing-test-resources::chunk-48` (0.0159), 4. `article_02_writing-test-resources::chunk-18` (0.0156), 5. `article_02_writing-test-resources::chunk-50` (0.0154) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-17` (0.6088), 2. `article_02_writing-test-resources::chunk-8` (0.5935), 3. `article_02_writing-test-resources::chunk-9` (0.5913), 4. `article_02_writing-test-resources::chunk-22` (0.5890), 5. `article_02_writing-test-resources::chunk-18` (0.5764) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-17` (0.0164), 2. `article_02_writing-test-resources::chunk-8` (0.0161), 3. `article_02_writing-test-resources::chunk-9` (0.0159), 4. `article_02_writing-test-resources::chunk-22` (0.0156), 5. `article_02_writing-test-resources::chunk-18` (0.0154) |

Evidence: Use an introduction, two or three body paragraphs each addressing one issue or idea, and a conclusion that sums up the discussion.

### Q10 — BM25-targeted terms

> Khi chỉnh sửa, điều gì khiến một đoạn văn mất trọng tâm và người viết nên xử lý ra sao?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | No | 1. `article_04_ielts-academic-format-writing::chunk-14` (0.6324), 2. `article_04_ielts-academic-format-writing::chunk-9` (0.6255), 3. `article_02_writing-test-resources::chunk-49` (0.5982), 4. `article_02_writing-test-resources::chunk-62` (0.5785), 5. `article_02_writing-test-resources::chunk-72` (0.5490) |
| Hybrid (RRF) | No | 1. `article_04_ielts-academic-format-writing::chunk-14` (0.0164), 2. `article_04_ielts-academic-format-writing::chunk-9` (0.0161), 3. `article_02_writing-test-resources::chunk-49` (0.0159), 4. `article_02_writing-test-resources::chunk-62` (0.0156), 5. `article_02_writing-test-resources::chunk-72` (0.0154) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-26` (0.5982), 2. `article_02_writing-test-resources::chunk-25` (0.5112), 3. `article_02_writing-test-resources::chunk-29` (0.5108), 4. `article_04_ielts-academic-format-writing::chunk-6` (0.4869), 5. `article_02_writing-test-resources::chunk-31` (0.4601) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-26` (0.0164), 2. `article_02_writing-test-resources::chunk-25` (0.0161), 3. `article_02_writing-test-resources::chunk-29` (0.0159), 4. `article_04_ielts-academic-format-writing::chunk-6` (0.0156), 5. `article_02_writing-test-resources::chunk-31` (0.0154) |

Evidence: A paragraph should address one issue only; move unrelated sentences to the paragraph where they belong.

### Q11 — Semantic paraphrases

> Trong bài tóm tắt dữ liệu trực quan, phần nào khái quát xu hướng chính thay vì liệt kê chi tiết hỗ trợ?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-23` (0.6252), 2. `article_02_writing-test-resources::chunk-20` (0.6007), 3. `article_02_writing-test-resources::chunk-17` (0.5749), 4. `article_02_writing-test-resources::chunk-50` (0.5606), 5. `article_02_writing-test-resources::chunk-24` (0.5346) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-23` (0.0164), 2. `article_02_writing-test-resources::chunk-20` (0.0161), 3. `article_02_writing-test-resources::chunk-17` (0.0159), 4. `article_02_writing-test-resources::chunk-50` (0.0156), 5. `article_02_writing-test-resources::chunk-24` (0.0154) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-22` (0.4904), 2. `article_02_writing-test-resources::chunk-7` (0.4727), 3. `article_02_writing-test-resources::chunk-19` (0.4664), 4. `article_02_writing-test-resources::chunk-8` (0.4590) ✓, 5. `article_02_writing-test-resources::chunk-21` (0.4523) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-22` (0.0164), 2. `article_02_writing-test-resources::chunk-7` (0.0161), 3. `article_02_writing-test-resources::chunk-19` (0.0159), 4. `article_02_writing-test-resources::chunk-8` (0.0156) ✓, 5. `article_02_writing-test-resources::chunk-21` (0.0154) |

Evidence: The overview summarises the main points, such as the main trends, changes, or number of steps.

### Q12 — Multi-constraint questions

> Khi mô tả các thay đổi chính trên bản đồ theo thời gian, cần kèm những loại chi tiết hỗ trợ nào?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-20` (0.7500) ✓, 2. `article_02_writing-test-resources::chunk-23` (0.7359), 3. `article_02_writing-test-resources::chunk-19` (0.5981), 4. `article_02_writing-test-resources::chunk-21` (0.5109), 5. `article_04_ielts-academic-format-writing::chunk-7` (0.4163) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-20` (0.0164) ✓, 2. `article_02_writing-test-resources::chunk-23` (0.0161), 3. `article_02_writing-test-resources::chunk-19` (0.0159), 4. `article_02_writing-test-resources::chunk-21` (0.0156), 5. `article_04_ielts-academic-format-writing::chunk-7` (0.0154) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-7` (0.4128) ✓, 2. `article_02_writing-test-resources::chunk-8` (0.3894), 3. `article_02_writing-test-resources::chunk-9` (0.3268), 4. `article_02_writing-test-resources::chunk-13` (0.3102), 5. `article_02_writing-test-resources::chunk-27` (0.3000) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-7` (0.0164) ✓, 2. `article_02_writing-test-resources::chunk-8` (0.0161), 3. `article_02_writing-test-resources::chunk-9` (0.0159), 4. `article_02_writing-test-resources::chunk-13` (0.0156), 5. `article_02_writing-test-resources::chunk-27` (0.0154) |

Evidence: Support the major changes with the supplied figures and the positions of items on the map; compass directions can help describe locations.

### Q13 — BM25-targeted terms

> Ở bài Academic Task 1, những hình thức trình bày nào không được dùng dù bài đã đạt số từ tối thiểu?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_03_academic-test::chunk-14` (3.8953), 2. `article_03_academic-test::chunk-13` (3.6380), 3. `article_03_academic-test::chunk-17` (3.5305), 4. `article_04_ielts-academic-format-writing::chunk-6` (3.4454), 5. `article_03_academic-test::chunk-12` (3.3942) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-7` (0.6454), 2. `article_02_writing-test-resources::chunk-58` (0.6390), 3. `article_04_ielts-academic-format-writing::chunk-6` (0.6030), 4. `article_02_writing-test-resources::chunk-59` (0.5931), 5. `article_02_writing-test-resources::chunk-48` (0.5869) |
| Hybrid (RRF) | No | 1. `article_04_ielts-academic-format-writing::chunk-6` (0.0315), 2. `article_03_academic-test::chunk-19` (0.0290), 3. `article_02_writing-test-resources::chunk-7` (0.0164), 4. `article_03_academic-test::chunk-14` (0.0164), 5. `article_02_writing-test-resources::chunk-58` (0.0161) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_03_academic-test::chunk-16` (4.3074), 2. `article_03_academic-test::chunk-17` (4.2871), 3. `article_03_academic-test::chunk-15` (4.2347), 4. `article_03_academic-test::chunk-12` (4.1696), 5. `article_03_academic-test::chunk-14` (4.1696) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-8` (0.5911), 2. `article_02_writing-test-resources::chunk-9` (0.5800), 3. `article_02_writing-test-resources::chunk-13` (0.5479), 4. `article_02_writing-test-resources::chunk-17` (0.5425), 5. `article_02_writing-test-resources::chunk-31` (0.5343) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-8` (0.0164), 2. `article_03_academic-test::chunk-16` (0.0164), 3. `article_02_writing-test-resources::chunk-9` (0.0161), 4. `article_03_academic-test::chunk-17` (0.0161), 5. `article_02_writing-test-resources::chunk-13` (0.0159) |

Evidence: The response must be written in full without subheadings, bullet points, a greeting, a name/sign-off, or diagrams, charts and tables.

### Q14 — Multi-constraint questions

> Ngoài việc chọn các đặc điểm chính của hình, Task Achievement yêu cầu thí sinh xử lý chúng thế nào?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_04_ielts-academic-format-writing::chunk-3` (3.8419), 2. `article_02_writing-test-resources::chunk-25` (3.7508), 3. `article_02_writing-test-resources::chunk-31` (3.6334), 4. `article_02_writing-test-resources::chunk-15` (3.0568), 5. `article_02_writing-test-resources::chunk-24` (2.7674) ✓ |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-24` (0.7783) ✓, 2. `article_02_writing-test-resources::chunk-12` (0.7309), 3. `article_02_writing-test-resources::chunk-44` (0.6908), 4. `article_02_writing-test-resources::chunk-35` (0.6743), 5. `article_02_writing-test-resources::chunk-1` (0.6674) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-24` (0.0318) ✓, 2. `article_02_writing-test-resources::chunk-25` (0.0313), 3. `article_04_ielts-academic-format-writing::chunk-3` (0.0307), 4. `article_02_writing-test-resources::chunk-12` (0.0306), 5. `article_02_writing-test-resources::chunk-35` (0.0306) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-14` (4.5841), 2. `article_02_writing-test-resources::chunk-9` (4.1076) ✓, 3. `article_02_writing-test-resources::chunk-12` (3.9780), 4. `article_04_ielts-academic-format-writing::chunk-2` (3.9596), 5. `article_02_writing-test-resources::chunk-6` (3.5652) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-7` (0.6679), 2. `article_02_writing-test-resources::chunk-13` (0.6592), 3. `article_02_writing-test-resources::chunk-9` (0.6586) ✓, 4. `article_02_writing-test-resources::chunk-14` (0.6207), 5. `article_02_writing-test-resources::chunk-6` (0.6096) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-14` (0.0320), 2. `article_02_writing-test-resources::chunk-9` (0.0320) ✓, 3. `article_02_writing-test-resources::chunk-6` (0.0308), 4. `article_02_writing-test-resources::chunk-7` (0.0307), 5. `article_02_writing-test-resources::chunk-10` (0.0299) |

Evidence: Compare or contrast the key features, provide enough supporting detail, report accurately, and present an overview.

### Q15 — Semantic paraphrases

> Nếu một gạch đầu dòng trong đề thư yêu cầu nêu cả vấn đề lẫn nguyên nhân khiến công việc khó khăn, cần trả lời thế nào cho đủ?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-33` (0.5647) ✓, 2. `article_02_writing-test-resources::chunk-35` (0.5646), 3. `article_04_ielts-academic-format-writing::chunk-4` (0.5357), 4. `article_02_writing-test-resources::chunk-44` (0.5325), 5. `article_02_writing-test-resources::chunk-48` (0.5255) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-33` (0.0164) ✓, 2. `article_02_writing-test-resources::chunk-35` (0.0161), 3. `article_04_ielts-academic-format-writing::chunk-4` (0.0159), 4. `article_02_writing-test-resources::chunk-44` (0.0156), 5. `article_02_writing-test-resources::chunk-48` (0.0154) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-13` (0.5802) ✓, 2. `article_02_writing-test-resources::chunk-12` (0.5701), 3. `article_02_writing-test-resources::chunk-11` (0.5612), 4. `article_02_writing-test-resources::chunk-17` (0.5607), 5. `article_02_writing-test-resources::chunk-14` (0.5438) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-13` (0.0164) ✓, 2. `article_02_writing-test-resources::chunk-12` (0.0161), 3. `article_02_writing-test-resources::chunk-11` (0.0159), 4. `article_02_writing-test-resources::chunk-17` (0.0156), 5. `article_02_writing-test-resources::chunk-14` (0.0154) |

Evidence: The example bullet contains two parts: explain more than one problem and explain why working is difficult. Both parts need to be addressed.

### Q16 — BM25-targeted terms

> Theo hướng dẫn, nên đưa thông tin gì vào đoạn mở đầu thư để mục đích rõ ràng ở Band 7 trở lên?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_02_writing-test-resources::chunk-70` (4.5154), 2. `article_02_writing-test-resources::chunk-47` (4.3357), 3. `article_02_writing-test-resources::chunk-31` (4.0747), 4. `article_02_writing-test-resources::chunk-68` (3.8638), 5. `article_02_writing-test-resources::chunk-41` (3.6975) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-41` (0.6793), 2. `article_02_writing-test-resources::chunk-29` (0.6503) ✓, 3. `article_02_writing-test-resources::chunk-22` (0.6004), 4. `article_02_writing-test-resources::chunk-39` (0.5626), 5. `article_02_writing-test-resources::chunk-42` (0.5494) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-41` (0.0318), 2. `article_02_writing-test-resources::chunk-47` (0.0313), 3. `article_02_writing-test-resources::chunk-29` (0.0308) ✓, 4. `article_02_writing-test-resources::chunk-31` (0.0308), 5. `article_02_writing-test-resources::chunk-42` (0.0305) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_02_writing-test-resources::chunk-30` (3.5848), 2. `article_02_writing-test-resources::chunk-16` (3.5783), 3. `article_02_writing-test-resources::chunk-20` (3.4958), 4. `article_02_writing-test-resources::chunk-29` (3.4700), 5. `article_02_writing-test-resources::chunk-12` (3.2696) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-20` (0.6442), 2. `article_02_writing-test-resources::chunk-16` (0.4961), 3. `article_02_writing-test-resources::chunk-17` (0.4382), 4. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.4334), 5. `article_02_writing-test-resources::chunk-11` (0.4243) ✓ |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-20` (0.0323), 2. `article_02_writing-test-resources::chunk-16` (0.0323), 3. `article_02_writing-test-resources::chunk-30` (0.0311), 4. `article_02_writing-test-resources::chunk-11` (0.0305) ✓, 5. `article_02_writing-test-resources::chunk-17` (0.0302) |

Evidence: State the main purpose in the opening paragraph so the reason for writing is clear.

### Q17 — Semantic paraphrases

> Nếu viết cho quản lý công ty mà mình chưa từng gặp, ví dụ IELTS khuyến nghị giọng điệu và lời chào nào?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_04_ielts-academic-format-writing::chunk-0` (1.6242), 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-0` (1.5828), 3. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (1.5745), 4. `article_02_writing-test-resources::chunk-5` (1.5582), 5. `article_03_academic-test::chunk-0` (1.5232) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-26` (0.6171), 2. `article_02_writing-test-resources::chunk-30` (0.5622) ✓, 3. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-14` (0.5063), 4. `article_02_writing-test-resources::chunk-10` (0.5042), 5. `article_02_writing-test-resources::chunk-9` (0.5003) |
| Hybrid (RRF) | No | 1. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.0308), 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-14` (0.0306), 3. `article_03_academic-test::chunk-1` (0.0288), 4. `article_02_writing-test-resources::chunk-26` (0.0164), 5. `article_04_ielts-academic-format-writing::chunk-0` (0.0164) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_03_academic-test::chunk-28` (1.8048), 2. `article_03_academic-test::chunk-27` (1.7927), 3. `article_03_academic-test::chunk-29` (1.7342), 4. `article_03_academic-test::chunk-2` (1.6620), 5. `article_04_ielts-academic-format-writing::chunk-0` (1.6347) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-3` (0.4808), 2. `article_04_ielts-academic-format-writing::chunk-2` (0.4766), 3. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-15` (0.4670), 4. `article_02_writing-test-resources::chunk-12` (0.4646) ✓, 5. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.4571) |
| Hybrid (RRF) | No | 1. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-15` (0.0306), 2. `article_04_ielts-academic-format-writing::chunk-0` (0.0305), 3. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.0303), 4. `article_04_ielts-academic-format-writing::chunk-8` (0.0288), 5. `article_02_writing-test-resources::chunk-3` (0.0164) |

Evidence: Use a formal, not overly chatty or friendly, tone and begin with 'Dear Sir or Madam'.

### Q18 — Multi-constraint questions

> Nếu đề luận hỏi quảng cáo có ảnh hưởng xấu đến trẻ em và gia đình hay không, cần bàn những phần nào để tránh bị giới hạn ở Band 5 Task Response?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-68` (5.1269), 2. `article_02_writing-test-resources::chunk-60` (5.0089), 3. `article_02_writing-test-resources::chunk-39` (4.4089) ✓, 4. `article_02_writing-test-resources::chunk-56` (4.2428), 5. `article_03_academic-test::chunk-20` (3.9667) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-40` (0.8009), 2. `article_02_writing-test-resources::chunk-39` (0.7883) ✓, 3. `article_02_writing-test-resources::chunk-38` (0.6490), 4. `article_02_writing-test-resources::chunk-58` (0.5394), 5. `article_02_writing-test-resources::chunk-48` (0.5335) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-39` (0.0320) ✓, 2. `article_02_writing-test-resources::chunk-48` (0.0303), 3. `article_02_writing-test-resources::chunk-58` (0.0301), 4. `article_02_writing-test-resources::chunk-47` (0.0294), 5. `article_02_writing-test-resources::chunk-40` (0.0164) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-16` (5.9316) ✓, 2. `article_03_academic-test::chunk-23` (5.4818), 3. `article_02_writing-test-resources::chunk-23` (4.9698), 4. `article_02_writing-test-resources::chunk-20` (4.8993), 5. `article_02_writing-test-resources::chunk-29` (4.5771) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-16` (0.7384) ✓, 2. `article_02_writing-test-resources::chunk-20` (0.5376), 3. `article_02_writing-test-resources::chunk-17` (0.4980), 4. `article_02_writing-test-resources::chunk-26` (0.4359), 5. `article_02_writing-test-resources::chunk-24` (0.4325) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-16` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-20` (0.0318), 3. `article_02_writing-test-resources::chunk-17` (0.0304), 4. `article_02_writing-test-resources::chunk-25` (0.0303), 5. `article_02_writing-test-resources::chunk-24` (0.0297) |

Evidence: Address both children and their families; omitting either main part limits the response to Band 5. Give reasons and relevant examples.

### Q19 — Semantic paraphrases

> So với Band 6, lập trường ở Band 7 trở lên cần thể hiện đặc điểm gì và lập luận nên kết thúc thế nào?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_02_writing-test-resources::chunk-47` (8.6714), 2. `article_02_writing-test-resources::chunk-31` (8.1494), 3. `article_02_writing-test-resources::chunk-22` (7.7465), 4. `article_02_writing-test-resources::chunk-48` (7.6380), 5. `article_02_writing-test-resources::chunk-21` (6.6184) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-41` (0.6363) ✓, 2. `article_02_writing-test-resources::chunk-47` (0.6351), 3. `article_02_writing-test-resources::chunk-22` (0.6254), 4. `article_02_writing-test-resources::chunk-39` (0.6040), 5. `article_02_writing-test-resources::chunk-31` (0.5690) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-47` (0.0325), 2. `article_02_writing-test-resources::chunk-22` (0.0317), 3. `article_02_writing-test-resources::chunk-31` (0.0315), 4. `article_02_writing-test-resources::chunk-39` (0.0303), 5. `article_02_writing-test-resources::chunk-48` (0.0303) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-20` (9.6915), 2. `article_02_writing-test-resources::chunk-8` (8.5202), 3. `article_02_writing-test-resources::chunk-16` (8.3955) ✓, 4. `article_02_writing-test-resources::chunk-11` (8.1909), 5. `article_02_writing-test-resources::chunk-12` (7.7613) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-20` (0.6980), 2. `article_02_writing-test-resources::chunk-16` (0.4986) ✓, 3. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.4075), 4. `article_02_writing-test-resources::chunk-22` (0.3597), 5. `article_02_writing-test-resources::chunk-26` (0.3445) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-20` (0.0328), 2. `article_02_writing-test-resources::chunk-16` (0.0320) ✓, 3. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.0304), 4. `article_02_writing-test-resources::chunk-11` (0.0301), 5. `article_02_writing-test-resources::chunk-30` (0.0299) |

Evidence: At Band 7 or higher, the position should be clear and developed, with ideas leading to a logical conclusion.

### Q20 — Semantic paraphrases

> Tiêu chí nào đánh giá bố cục tổng thể và mạch logic của ý tưởng, khác với các phương tiện liên kết giữa câu?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-50` (0.7418), 2. `article_02_writing-test-resources::chunk-53` (0.7320), 3. `article_02_writing-test-resources::chunk-47` (0.6537), 4. `article_02_writing-test-resources::chunk-42` (0.6387), 5. `article_02_writing-test-resources::chunk-49` (0.6253) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-50` (0.0164), 2. `article_02_writing-test-resources::chunk-53` (0.0161), 3. `article_02_writing-test-resources::chunk-47` (0.0159), 4. `article_02_writing-test-resources::chunk-42` (0.0156), 5. `article_02_writing-test-resources::chunk-49` (0.0154) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-22` (0.5680), 2. `article_02_writing-test-resources::chunk-17` (0.5591), 3. `article_02_writing-test-resources::chunk-26` (0.5195), 4. `article_02_writing-test-resources::chunk-21` (0.5145), 5. `article_02_writing-test-resources::chunk-13` (0.4844) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-22` (0.0164), 2. `article_02_writing-test-resources::chunk-17` (0.0161), 3. `article_02_writing-test-resources::chunk-26` (0.0159), 4. `article_02_writing-test-resources::chunk-21` (0.0156), 5. `article_02_writing-test-resources::chunk-13` (0.0154) |

Evidence: Coherence is structural linking and logical organisation; cohesion uses devices that clarify relationships within and between sentences.

### Q21 — Multi-constraint questions

> Với câu trả lời Task 1 ngắn, việc chia đoạn quan trọng ở band nào; còn Task 2 yêu cầu chia đoạn từ band nào?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-48` (6.0100) ✓, 2. `article_03_academic-test::chunk-20` (5.6688), 3. `article_04_ielts-academic-format-writing::chunk-8` (4.6167), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-3` (4.6167), 5. `article_04_ielts-academic-format-writing::chunk-6` (4.3880) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-48` (0.6711) ✓, 2. `article_02_writing-test-resources::chunk-15` (0.6328), 3. `article_02_writing-test-resources::chunk-31` (0.6155), 4. `article_02_writing-test-resources::chunk-58` (0.5866), 5. `article_04_ielts-academic-format-writing::chunk-8` (0.5534) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-48` (0.0328) ✓, 2. `article_04_ielts-academic-format-writing::chunk-8` (0.0313), 3. `article_02_writing-test-resources::chunk-15` (0.0161), 4. `article_03_academic-test::chunk-20` (0.0161), 5. `article_02_writing-test-resources::chunk-31` (0.0159) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_03_academic-test::chunk-23` (8.2798), 2. `article_02_writing-test-resources::chunk-20` (7.8185) ✓, 3. `article_04_ielts-academic-format-writing::chunk-5` (6.5907), 4. `article_02_writing-test-resources::chunk-12` (6.5364), 5. `article_02_writing-test-resources::chunk-24` (6.0837) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-20` (0.5998) ✓, 2. `article_02_writing-test-resources::chunk-16` (0.5894), 3. `article_02_writing-test-resources::chunk-17` (0.5376), 4. `article_02_writing-test-resources::chunk-8` (0.4591), 5. `article_02_writing-test-resources::chunk-13` (0.4498) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-20` (0.0325) ✓, 2. `article_03_academic-test::chunk-23` (0.0313), 3. `article_02_writing-test-resources::chunk-16` (0.0313), 4. `article_02_writing-test-resources::chunk-17` (0.0304), 5. `article_04_ielts-academic-format-writing::chunk-5` (0.0159) |

Evidence: For short Task 1 responses paragraphing matters only at Bands 8 and 9; Task 2 expects paragraphs from Band 6 and above.

### Q22 — BM25-targeted terms

> Những cụm từ nối nào báo hiệu trình tự, và ví dụ nào thể hiện quan hệ như kết quả hoặc tương phản?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-54` (0.5616) ✓, 2. `article_02_writing-test-resources::chunk-51` (0.5562), 3. `article_02_writing-test-resources::chunk-52` (0.5206), 4. `article_02_writing-test-resources::chunk-53` (0.4846), 5. `article_02_writing-test-resources::chunk-62` (0.4805) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-54` (0.0164) ✓, 2. `article_02_writing-test-resources::chunk-51` (0.0161), 3. `article_02_writing-test-resources::chunk-52` (0.0159), 4. `article_02_writing-test-resources::chunk-53` (0.0156), 5. `article_02_writing-test-resources::chunk-62` (0.0154) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-26` (0.4842), 2. `article_02_writing-test-resources::chunk-22` (0.4813) ✓, 3. `article_02_writing-test-resources::chunk-21` (0.4434), 4. `article_02_writing-test-resources::chunk-19` (0.4078), 5. `article_02_writing-test-resources::chunk-25` (0.3901) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-26` (0.0164), 2. `article_02_writing-test-resources::chunk-22` (0.0161) ✓, 3. `article_02_writing-test-resources::chunk-21` (0.0159), 4. `article_02_writing-test-resources::chunk-19` (0.0156), 5. `article_02_writing-test-resources::chunk-25` (0.0154) |

Evidence: 'Firstly' and 'in conclusion' mark sequences; 'hence', 'as a result', 'although' and 'because' signal relationships.

### Q23 — BM25-targeted terms

> Những dạng quy chiếu nào giúp tránh lặp lại cùng một danh từ trong bài luận?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-52` (0.5965) ✓, 2. `article_02_writing-test-resources::chunk-62` (0.5476), 3. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-9` (0.5389), 4. `article_02_writing-test-resources::chunk-63` (0.5242), 5. `article_02_writing-test-resources::chunk-56` (0.5143) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-52` (0.0164) ✓, 2. `article_02_writing-test-resources::chunk-62` (0.0161), 3. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-9` (0.0159), 4. `article_02_writing-test-resources::chunk-63` (0.0156), 5. `article_02_writing-test-resources::chunk-56` (0.0154) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-26` (0.5072), 2. `article_02_writing-test-resources::chunk-22` (0.3963), 3. `article_02_writing-test-resources::chunk-21` (0.3927) ✓, 4. `article_02_writing-test-resources::chunk-24` (0.3484), 5. `article_02_writing-test-resources::chunk-25` (0.3407) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-26` (0.0164), 2. `article_02_writing-test-resources::chunk-22` (0.0161), 3. `article_02_writing-test-resources::chunk-21` (0.0159) ✓, 4. `article_02_writing-test-resources::chunk-24` (0.0156), 5. `article_02_writing-test-resources::chunk-25` (0.0154) |

Evidence: Reference and substitution include pronouns, relative pronouns and the definite article 'the'.

### Q24 — Multi-constraint questions

> Năng lực từ vựng nào phân biệt phạm vi vừa đủ ở Band 5 với mức được kỳ vọng ở band cao hơn?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-60` (6.4877), 2. `article_02_writing-test-resources::chunk-39` (6.0872), 3. `article_02_writing-test-resources::chunk-68` (5.9660), 4. `article_02_writing-test-resources::chunk-56` (5.4400) ✓, 5. `article_03_academic-test::chunk-20` (5.0486) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-39` (0.6616), 2. `article_02_writing-test-resources::chunk-22` (0.6517), 3. `article_02_writing-test-resources::chunk-58` (0.6245), 4. `article_02_writing-test-resources::chunk-47` (0.5817), 5. `article_02_writing-test-resources::chunk-62` (0.5480) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-39` (0.0325), 2. `article_02_writing-test-resources::chunk-47` (0.0303), 3. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.0301), 4. `article_02_writing-test-resources::chunk-15` (0.0286), 5. `article_02_writing-test-resources::chunk-60` (0.0164) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | 1. `article_02_writing-test-resources::chunk-16` (6.0435), 2. `article_02_writing-test-resources::chunk-25` (5.9734), 3. `article_02_writing-test-resources::chunk-29` (5.7718), 4. `article_03_academic-test::chunk-23` (5.3351), 5. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (4.9898) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-20` (0.7071), 2. `article_02_writing-test-resources::chunk-16` (0.5371), 3. `article_02_writing-test-resources::chunk-26` (0.4920), 4. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.4852), 5. `article_02_writing-test-resources::chunk-30` (0.4164) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-16` (0.0325), 2. `article_02_writing-test-resources::chunk-20` (0.0311), 3. `article_02_writing-test-resources::chunk-25` (0.0311), 4. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.0310), 5. `article_02_writing-test-resources::chunk-30` (0.0303) |

Evidence: Band 5 may have a minimally adequate range; higher bands require flexible use of wider vocabulary, including synonyms and collocations.

### Q25 — Semantic paraphrases

> Lỗi gì xảy ra khi một từ nghe không tự nhiên trong ngữ cảnh hoặc quá suồng sã; ngoài ra còn có vấn đề từ vựng liên quan nào?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-60` (0.6100), 2. `article_02_writing-test-resources::chunk-62` (0.6049), 3. `article_02_writing-test-resources::chunk-67` (0.5537), 4. `article_02_writing-test-resources::chunk-61` (0.5403) ✓, 5. `article_02_writing-test-resources::chunk-72` (0.5327) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-60` (0.0164), 2. `article_02_writing-test-resources::chunk-62` (0.0161), 3. `article_02_writing-test-resources::chunk-67` (0.0159), 4. `article_02_writing-test-resources::chunk-61` (0.0156) ✓, 5. `article_02_writing-test-resources::chunk-72` (0.0154) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-25` (0.5821) ✓, 2. `article_02_writing-test-resources::chunk-26` (0.5561), 3. `article_02_writing-test-resources::chunk-30` (0.4282), 4. `article_02_writing-test-resources::chunk-24` (0.4133), 5. `article_02_writing-test-resources::chunk-29` (0.4119) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-25` (0.0164) ✓, 2. `article_02_writing-test-resources::chunk-26` (0.0161), 3. `article_02_writing-test-resources::chunk-30` (0.0159), 4. `article_02_writing-test-resources::chunk-24` (0.0156), 5. `article_02_writing-test-resources::chunk-29` (0.0154) |

Evidence: These are lexical inappropriacies; inaccurate collocations, where words are not normally used together, may also occur.

### Q26 — Semantic paraphrases

> Lỗi chính tả hoặc cấu tạo từ phải nghiêm trọng đến mức nào mới khiến Lexical Resource bị giới hạn ở Band 5?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-60` (10.6473) ✓, 2. `article_02_writing-test-resources::chunk-56` (8.9279), 3. `article_02_writing-test-resources::chunk-62` (5.7452), 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-2` (5.5111), 5. `article_04_ielts-academic-format-writing::chunk-5` (5.0544) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-60` (0.7648) ✓, 2. `article_02_writing-test-resources::chunk-58` (0.6994), 3. `article_02_writing-test-resources::chunk-62` (0.6614), 4. `article_02_writing-test-resources::chunk-70` (0.6536), 5. `article_02_writing-test-resources::chunk-68` (0.6178) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-60` (0.0328) ✓, 2. `article_02_writing-test-resources::chunk-62` (0.0317), 3. `article_02_writing-test-resources::chunk-56` (0.0313), 4. `article_02_writing-test-resources::chunk-58` (0.0161), 5. `article_02_writing-test-resources::chunk-70` (0.0156) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-25` (9.8605) ✓, 2. `article_02_writing-test-resources::chunk-23` (9.1782), 3. `article_02_writing-test-resources::chunk-26` (6.3823), 4. `article_02_writing-test-resources::chunk-24` (5.4417), 5. `article_02_writing-test-resources::chunk-27` (5.3833) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-26` (0.6680), 2. `article_02_writing-test-resources::chunk-20` (0.6440), 3. `article_02_writing-test-resources::chunk-25` (0.6380) ✓, 4. `article_02_writing-test-resources::chunk-30` (0.5962), 5. `article_02_writing-test-resources::chunk-16` (0.5339) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-25` (0.0323) ✓, 2. `article_02_writing-test-resources::chunk-26` (0.0323), 3. `article_02_writing-test-resources::chunk-23` (0.0306), 4. `article_02_writing-test-resources::chunk-16` (0.0297), 5. `article_02_writing-test-resources::chunk-20` (0.0161) |

Evidence: A serious error prevents communication; noticeable spelling or word-formation errors that cause reader difficulty limit Lexical Resource to Band 5.

### Q27 — BM25-targeted terms

> Theo tiêu chí ngữ pháp, cấu trúc mệnh đề nào phân biệt câu phức với câu đơn?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-66` (0.7460) ✓, 2. `article_02_writing-test-resources::chunk-67` (0.6877), 3. `article_02_writing-test-resources::chunk-56` (0.6119), 4. `article_02_writing-test-resources::chunk-50` (0.5572), 5. `article_02_writing-test-resources::chunk-58` (0.5528) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-66` (0.0164) ✓, 2. `article_02_writing-test-resources::chunk-67` (0.0161), 3. `article_02_writing-test-resources::chunk-56` (0.0159), 4. `article_02_writing-test-resources::chunk-50` (0.0156), 5. `article_02_writing-test-resources::chunk-58` (0.0154) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-24` (0.5151), 2. `article_02_writing-test-resources::chunk-26` (0.5075), 3. `article_02_writing-test-resources::chunk-21` (0.4908), 4. `article_02_writing-test-resources::chunk-22` (0.4639), 5. `article_02_writing-test-resources::chunk-17` (0.4288) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-24` (0.0164), 2. `article_02_writing-test-resources::chunk-26` (0.0161), 3. `article_02_writing-test-resources::chunk-21` (0.0159), 4. `article_02_writing-test-resources::chunk-22` (0.0156), 5. `article_02_writing-test-resources::chunk-17` (0.0154) |

Evidence: A simple sentence has one independent clause; a complex sentence has a main clause and one or more subordinate clauses.

### Q28 — BM25-targeted terms

> Hãy nêu một số cấu trúc diễn đạt phức tạp hơn trong câu được tính vào phạm vi ngữ pháp.

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | Yes | 1. `article_02_writing-test-resources::chunk-67` (0.7314) ✓, 2. `article_02_writing-test-resources::chunk-66` (0.6654), 3. `article_02_writing-test-resources::chunk-56` (0.6540), 4. `article_02_writing-test-resources::chunk-58` (0.5911), 5. `article_02_writing-test-resources::chunk-57` (0.5527) |
| Hybrid (RRF) | Yes | 1. `article_02_writing-test-resources::chunk-67` (0.0164) ✓, 2. `article_02_writing-test-resources::chunk-66` (0.0161), 3. `article_02_writing-test-resources::chunk-56` (0.0159), 4. `article_02_writing-test-resources::chunk-58` (0.0156), 5. `article_02_writing-test-resources::chunk-57` (0.0154) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | No | (no lexical matches) |
| Dense | No | 1. `article_02_writing-test-resources::chunk-26` (0.5669), 2. `article_02_writing-test-resources::chunk-24` (0.5593), 3. `article_02_writing-test-resources::chunk-21` (0.5093), 4. `article_02_writing-test-resources::chunk-22` (0.4871), 5. `article_02_writing-test-resources::chunk-25` (0.4665) |
| Hybrid (RRF) | No | 1. `article_02_writing-test-resources::chunk-26` (0.0164), 2. `article_02_writing-test-resources::chunk-24` (0.0161), 3. `article_02_writing-test-resources::chunk-21` (0.0159), 4. `article_02_writing-test-resources::chunk-22` (0.0156), 5. `article_02_writing-test-resources::chunk-25` (0.0154) |

Evidence: Examples include passive forms, modal verbs, comparative structures and complex noun phrases.

### Q29 — Multi-constraint questions

> Ở Band 8, IELTS phân biệt lỗi ngữ pháp thỉnh thoảng với lỗi lặp thành quy luật ra sao, và vì sao điều này khác Band 7?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_02_writing-test-resources::chunk-70` (9.9045) ✓, 2. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-14` (9.3155), 3. `article_02_writing-test-resources::chunk-69` (6.3951), 4. `article_02_writing-test-resources::chunk-48` (6.3055), 5. `article_02_writing-test-resources::chunk-47` (6.1487) |
| Dense | No | 1. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-14` (0.7301), 2. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.6397), 3. `article_02_writing-test-resources::chunk-64` (0.6115), 4. `article_02_writing-test-resources::chunk-14` (0.5433), 5. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-1` (0.5331) |
| Hybrid (RRF) | Yes | 1. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-14` (0.0325), 2. `article_02_writing-test-resources::chunk-70` (0.0315) ✓, 3. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.0313), 4. `article_02_writing-test-resources::chunk-64` (0.0159), 5. `article_02_writing-test-resources::chunk-69` (0.0159) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-14` (9.1542), 2. `article_02_writing-test-resources::chunk-30` (7.8784) ✓, 3. `article_02_writing-test-resources::chunk-20` (7.6782), 4. `article_02_writing-test-resources::chunk-29` (7.6202), 5. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (6.5931) |
| Dense | No | 1. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.6248), 2. `article_02_writing-test-resources::chunk-27` (0.5310), 3. `article_04_ielts-academic-format-writing::chunk-6` (0.4993), 4. `article_02_writing-test-resources::chunk-20` (0.4988), 5. `article_04_ielts-academic-format-writing::chunk-0` (0.4987) |
| Hybrid (RRF) | Yes | 1. `article_01_ielts-writing-band-descriptors-and-key-assessment-criteria::chunk-0` (0.0318), 2. `article_02_writing-test-resources::chunk-20` (0.0315), 3. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-14` (0.0164), 4. `article_02_writing-test-resources::chunk-27` (0.0161), 5. `article_02_writing-test-resources::chunk-30` (0.0161) ✓ |

Evidence: Non-systematic errors are occasional; this distinction is not important for Band 7 but is important for Band 8, where most sentences should be error-free.

### Q30 — Semantic paraphrases

> Trong IELTS Academic Writing, thí sinh bắt buộc phải gõ bài hay một số địa điểm có thể chọn viết trên giấy?

**Legacy recursive 500/50**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_04_ielts-academic-format-writing::chunk-0` (4.2738), 2. `article_03_academic-test::chunk-20` (3.8814), 3. `article_03_academic-test::chunk-24` (3.6517), 4. `article_04_ielts-academic-format-writing::chunk-16` (3.5011), 5. `article_03_academic-test::chunk-2` (3.4959) ✓ |
| Dense | Yes | 1. `article_04_ielts-academic-format-writing::chunk-0` (0.7569), 2. `article_04_ielts-academic-format-writing::chunk-2` (0.7189), 3. `article_03_academic-test::chunk-2` (0.7132) ✓, 4. `article_05_10-steps-to-writing-high-scoring-ielts-essays::chunk-0` (0.6996), 5. `article_02_writing-test-resources::chunk-74` (0.6803) |
| Hybrid (RRF) | Yes | 1. `article_04_ielts-academic-format-writing::chunk-0` (0.0328), 2. `article_03_academic-test::chunk-2` (0.0313) ✓, 3. `article_03_academic-test::chunk-0` (0.0294), 4. `article_03_academic-test::chunk-20` (0.0161), 5. `article_04_ielts-academic-format-writing::chunk-2` (0.0161) |

**Markdown section-aware 1200/0**

| Method | Hit@5 | Top-5 chunks |
|---|---:|---|
| Sparse (BM25) | Yes | 1. `article_03_academic-test::chunk-23` (5.1179), 2. `article_03_academic-test::chunk-2` (4.9860) ✓, 3. `article_04_ielts-academic-format-writing::chunk-0` (4.9042), 4. `article_04_ielts-academic-format-writing::chunk-8` (4.7112), 5. `article_04_ielts-academic-format-writing::chunk-11` (4.6744) |
| Dense | No | 1. `article_04_ielts-academic-format-writing::chunk-6` (0.7961), 2. `article_04_ielts-academic-format-writing::chunk-0` (0.7928), 3. `article_04_ielts-academic-format-writing::chunk-10` (0.7687), 4. `article_04_ielts-academic-format-writing::chunk-3` (0.7484), 5. `article_04_ielts-academic-format-writing::chunk-5` (0.7462) |
| Hybrid (RRF) | Yes | 1. `article_04_ielts-academic-format-writing::chunk-0` (0.0320), 2. `article_03_academic-test::chunk-2` (0.0313) ✓, 3. `article_04_ielts-academic-format-writing::chunk-3` (0.0301), 4. `article_04_ielts-academic-format-writing::chunk-8` (0.0299), 5. `article_04_ielts-academic-format-writing::chunk-13` (0.0296) |

Evidence: IELTS Academic is delivered on computer; for Writing, candidates may also choose Writing on Paper where available.

## Limits

The corpus currently has five IELTS pages and does not include all eight planned sources. The benchmark's dense model is `all-mpnet-base-v2`, while production Task 4 defaults to `BAAI/bge-m3`; use the same benchmark with BGE-M3 before treating dense/hybrid numbers as production estimates. Retrieval scores are not comparable across methods; only ranked evidence matches are compared.
