# JARVIS AI Operating System

Version: 1.0

---

# Vision

JARVIS is a modular AI Operating System.

The user only interacts with **JARVIS**.

Internally, JARVIS delegates work to specialized subsystems.

The architecture is designed so every subsystem can evolve independently without changing the others.

---

# Core Principles

* Single Responsibility
* Modular Design
* Feature-Based Architecture
* Local First
* Provider Agnostic
* Testable Components
* Long-Term Maintainability

---

# High-Level Architecture

```
User
 │
 ▼
FastAPI / Voice / Dashboard
 │
 ▼
Hermes Orchestrator
 │
 ├──────────────┬──────────────┬──────────────┐
 │              │              │              │
Context      Planner        Tools         Memory
 │                             │              │
 │                             │              │
 └──────────────┬──────────────┘              │
                │                             │
                ▼                             ▼
             GLM 5.1                 Obsidian Vault
```

---

# Subsystems

## Hermes

Responsibilities:

* Orchestrate requests
* Coordinate memory
* Coordinate tools
* Build execution flow
* Return final response

Hermes never directly owns memory or tools.

---

## LLM

Responsibilities:

* Connect to model providers
* Manage prompts
* Send messages
* Return responses

The LLM layer never decides what information to send.

---

## Context

Responsibilities:

* Build the final prompt
* Combine:

  * System Prompt
  * Conversation History
  * Vault Memory
  * Tool Results
  * User Message

---

## Memory

Split into multiple layers.

Conversation Memory

* Current chat session

Vault Memory

* Obsidian notes

Search

* Retrieval

Embeddings

* Semantic search

---

## Tools

Every external capability becomes a tool.

Examples

* Browser
* Gmail
* Calendar
* GitHub
* Buffer
* RevenueCat
* Meta Ads
* Local Python
* Shell

---

## Voice

Speech-to-Text

Text-to-Speech

Wake Word

Streaming

---

## Dashboard

Displays:

* Chats
* Tasks
* Memory
* Logs
* System Health
* Running Agents

---

# Folder Structure

```
app/

agents/
    hermes/

api/

config/

context/

llm/
    prompts/
    providers/

memory/
    conversation/
    vault/
    search/
    embeddings/

planner/

tools/

voice/

core/

business/

utils/
```

---

# Request Flow

```
User

↓

Hermes

↓

Context Builder

↓

Memory

↓

Tools

↓

LLM

↓

Response

↓

Save Memory

↓

Return Response
```

---

# Development Roadmap

Phase 1

* Foundation
* API
* GLM
* Prompt Loader
* Conversation Memory

Phase 2

* Vault Reader
* Markdown Search
* Context Builder

Phase 3

* Tool Registry
* Planner
* Browser Automation

Phase 4

* Voice Interface
* Dashboard
* Automation Engine

Phase 5

* Multi-Agent System
* Long-Term Memory
* Mobile Companion

---

# Guiding Principle

The LLM is not the brain.

Hermes is the brain.

The LLM is one reasoning component used by Hermes.

JARVIS is the complete AI Operating System.

