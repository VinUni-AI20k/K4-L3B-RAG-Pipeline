# Track D Generation and UI Design

**Date:** 2026-09-25

## Goal

Deliver the Track D layer for the household-business tax RAG chatbot: grounded answer generation, a resilient Streamlit chat interface, and a visual style inspired by Ant Design and the supplied government-service portal reference.

## Scope

This design covers D0 through D3 only:

- `src/task10_generation.py`: context ordering, context formatting, provider dispatch, and citation-aware generation.
- `tests/test_edge_cases.py`: generation tests that use mocked retrieval and provider calls.
- `app.py`: the Streamlit user interface and source presentation.

Golden data, Ragas evaluation, and the evaluation report remain later Track D work. Track C retains ownership of retrieval.

## Integration Contract

`generate_with_citation(query, top_k)` imports and consumes Track C's public `retrieve` function. It does not inspect dense, BM25, RRF, or PageIndex internals.

Each retrieval item must follow `SearchResult`: an ID, content, numeric score, source metadata, and a `hybrid` or `pageindex` retrieval method. The generator returns `GenerationResult` with the answer, original retrieved chunks as sources, and the retrieval source.

If retrieval produces no chunks, retrieval raises, the provider raises, or the provider returns empty text, generation returns exactly:

```text
Tôi không thể xác minh thông tin này từ nguồn hiện có.
```

with an empty source list and `retrieval_source="none"`.

## Generation Design

`reorder_for_llm` returns a new list. It keeps all IDs but orders alternating chunks first and the remaining chunks in reverse order, reducing lost-in-the-middle effects.

`format_context` assigns each chunk a stable, visible label:

```text
[Document N | Title: ... | Source: ...]
```

The prompt instructs the selected provider to use only this context and cite the visible document labels. Provider selection remains environment-driven: OpenAI, Gemini, or Anthropic, with a 30-second timeout and temperature 0.3.

## UI Design

The app stays a Streamlit application; Ant Design is a visual reference rather than a React dependency. CSS provides the component language:

- charcoal application bar (`#202124`) with a compact product mark and product title;
- terracotta accent (`#D55A43`) for calls to action, active states, and assistant emphasis;
- pale apricot (`#FFF0E8`) hero surface and ivory (`#FCFBF8`) page background;
- white, 12-pixel-radius cards with subtle borders and shadows;
- deep teal (`#146B62`) for trusted-source accents.

The page contains a service hero, clickable suggested questions, the Streamlit chat transcript, and an expandable source display. Every cited source exposes `title | source | retrieval_method | score` plus its source excerpt. The page stores the full conversation in `st.session_state.messages`.

The supplied generated mock is a visual reference only. No generated image asset is required at runtime, keeping the app lightweight and reproducible.

## Error Handling and Accessibility

The app lets generation return its safe refusal without exposing provider traces to the user. It retains the question and the refusal in session history. Source expanders use plain text labels, and color is not the only representation of retrieval method or score.

## Verification

- Unit and contract tests verify ordering, context labels, safe refusal, and the public generation signature.
- The Streamlit app is manually checked with one in-scope tax question and one out-of-scope question after Track C is ready.
- Browser verification checks desktop layout, visible source metadata, responsive behavior, console errors, and the accessibility tree.
