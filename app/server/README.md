# Transcript Analysis API — Solution

A FastAPI service that accepts plain-text transcripts, analyzes them with an LLM, stores results in memory, and returns structured summaries with action items. Built following the hexagonal architecture already established in `app/`.

---

## Architecture

```
HTTP Layer      solution/server/main.py        — routes, exception handlers
Service Layer   solution/server/service.py     — business logic, error mapping
Storage         solution/server/storage.py     — in-memory dict store
Models          solution/server/models.py      — Pydantic DTOs
DI Wiring       solution/server/dependencies.py — composition root

LLM Port        app/ports/llm.py               — interface boundary
Adapters        app/adapters/openai.py         — real OpenAI calls
                app/adapters/mock.py           — offline fake adapter
```

The service depends only on the `LLm` port interface — the concrete adapter is wired at startup in `dependencies.py` and is never imported by the service or routes.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/analyses?transcript=...` | Analyze a single transcript |
| `GET` | `/analyses/{id}` | Retrieve a stored analysis by UUID |
| `POST` | `/analyses/batch` | Analyze multiple transcripts concurrently |

---

## Swagger / Interactive docs

With the server running, open **http://localhost:8000/docs** in your browser.

FastAPI generates the OpenAPI schema automatically from the route definitions and Pydantic models. Each endpoint has:

- A description explaining what it does
- Request parameter/body schema with a pre-filled example you can send directly from the browser
- Response schema showing the shape of a successful reply

The raw OpenAPI JSON is also available at **http://localhost:8000/openapi.json** if you want to import it into Postman or another client.

### Example payloads

**`GET /analyses`** — pass the transcript as a query parameter:
```
GET /analyses?transcript=Coach: What's been your biggest challenge this week? Client: Staying focused.
```

**`GET /analyses/{id}`** — use the UUID returned by the above call:
```
GET /analyses/3fa85f64-5717-4562-b3fc-2c963f66afa6
```

**`POST /analyses/batch`** — JSON body:
```json
{
  "transcripts": [
    "Coach: What's been your biggest challenge this week? Client: Staying focused — too many interruptions.",
    "Coach: How are you tracking toward your Q2 goals? Client: Behind on two of them, mainly due to scope creep."
  ]
}
```

These same examples are embedded in the models and will appear pre-filled in the Swagger UI "Try it out" panel.

---

## Setup

### Prerequisites

- Python 3.12+
- Dependencies installed and `.env` configured — see root README

### Run the server

From the repo root:

```bash
uvicorn solution.server.main:app --reload
```

---

## Mock mode

Set `MOCK_LLM=true` in `.env` to use the `MockLLmAdapter` instead of calling OpenAI. The mock returns hardcoded data instantly — useful for local development and testing without an API key or network access.

---

## Error responses

| Scenario | Status |
|----------|--------|
| Blank transcript / malformed UUID / invalid request body | 422 |
| Analysis ID not found | 404 |
| OpenAI rate limit reached | 429 |
| OpenAI network or timeout error | 503 |

---

## Running tests

```bash
pytest
```
