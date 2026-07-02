---
name: agent-system-navigation
description: "Быстрая навигация по агентам, паттернам делегирования, маршрутизация задач."
requires: none
---

> **Reference doc** — loaded on-demand from `references/skills/`. Not a separate ZCode skill; use when the master `multi-agent-ecosystem` skill or an agent brief points here.


## ЦЕЛЬ

Направить задачу к нужному агенту без избыточного делегирования.

## КОГДА ИСПОЛЬЗОВАТЬ

- При выборе агента для задачи
- При сборке мульти-voice pipeline
- При неясном владельце домена

## ТАБЛИЦА АГЕНТОВ

| Категория | Агент | Когда |
|-----------|-------|-------|
| **Координатор** | `orchestrator` | Многошаговые задачи с 2+ доменами |
| **Планирование** | `start` | Старт сессии; долгосрочные PBI |
| **Архитектура** | `architect` | Системные решения, ADR |
|  | `agent-architect` | Дизайн агентов и правил |
| **Реализация** | `code` | Написание / рефакторинг кода |
|  | `api-designer` | REST/gRPC контракты |
|  | `database-specialist` | Схемы БД, миграции |
|  | `devops-specialist` | CI/CD, инфраструктура |
|  | `frontend-specialist` | UI/UX, компоненты |
|  | `mobile-specialist` | iOS/Android |
| **Анализ** | `data-analyst` | Данные, метрики, EDA |
|  | `repo-explorer` | Исследование кодовой базы |
| **Качество** | `code-reviewer` | Ревью PR/кода |
|  | `bug-triage` | Диагностика и воспроизведение багов |
|  | `test-specialist` | Тест-стратегии, написание тестов |
|  | `security-auditor` | OWASP, CVE, threat model |
|  | `code-skeptic` | Devil's advocate, уязвимые места |
| **Оптимизация** | `performance-optimizer` | Latency, CPU, память |
|  | `code-simplifier` | Снижение сложности |
| **Документация** | `docs-specialist` | README, ADR, CHANGELOG |
|  | `release-manager` | Changelog, versioning, release notes |
| **Мета-агенты** | `meta-agent-architect` | Создание новых агентов |
|  | `subagent-factory` | Сборка агентных пакетов |
|  | `rules-specialist` | Обновление *.mdc правил |
|  | `skills-specialist` | Создание / обновление SKILL.md |
|  | `benchmark-specialist` | Контракты поведения |
| **Персональные** | `profile-manager` | Управление профилями пользователей |
|  | `provider-integrator` | API / сторонние провайдеры |
|  | `monitoring-specialist` | Observability, алерты |

## ПАТТЕРНЫ ДЕЛЕГИРОВАНИЯ

| Паттерн | Описание |
|---------|----------|
| **Sequential** | A  B  C (зависимости) |
| **Parallel** | A \|\| B \|\| C (независимые) |
| **BuilderSkepticVerifier** | Стандартные 3 голоса |
| **Council** | 4+ голоса при высоком риске |
| **Debate** | Skeptic оспаривает Builder; Verifier выносит вердикт |
| **Recursive** | Orchestrator  sub-orchestrator (макс глубина 3) |
| **Relay** | Результат A = вход B без полного переосмысления |
| **Peer refinement** | B1 рефайнит выход B2, оба говорят об одном |
| **Self-critique loop** | Агент оценивает собственный выход (micro/full) |

## ROUTING CHECKLIST

```
1. Один домен + одна задача     прямой агент
2. 2+ домена / ступени          orchestrator
3. Architectural decision       architect
4. Новый агент/правило          agent-architect / meta-agent-architect
5. "Не знаю какой агент"        ask / repo-explorer
6. Регрессия / баг              bug-triage  code
7. Security concern             security-auditor параллельно
```

## COST-AWARE ROUTING

- L1  6 веток  стандарт
- L2  12  только при явном открытом вопросе
- Council (+5 pts рубрика)  при критических решениях

## ПРОТОКОЛ ЧТЕНИЯ БОЛЬШИХ ФАЙЛОВ

```
read_file(lines 180)     # структура + секции
read_file(lines NN+80)   # целевой блок
```
Никогда не читать файл целиком, если >200 строк.
