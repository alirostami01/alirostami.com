#!/usr/bin/env python3
"""Canonical reader routes for Fundamentals of Software Architecture.

The upstream translation repository keeps generic ``chapter-NN`` source names.
This site's deployment artifacts use descriptive English slugs instead; this
reviewed table is the single source of truth for generators and redirects.
"""

from __future__ import annotations

# (historical site filename stem, canonical descriptive filename stem)
SOFTWARE_ARCHITECTURE_ROUTE_MAP: tuple[tuple[str, str], ...] = (
    ("chapter-01", "01-introduction"),
    ("chapter-02", "02-architectural-thinking"),
    ("chapter-03", "03-modularity"),
    ("chapter-04", "04-architectural-characteristics-defined"),
    ("chapter-05", "05-identifying-architectural-characteristics"),
    ("chapter-06", "06-measuring-and-governing-architectural-characteristics"),
    ("chapter-07", "07-the-scope-of-architectural-characteristics"),
    ("chapter-08", "08-component-based-thinking"),
    ("chapter-09", "09-foundations"),
    ("chapter-10", "10-layered-architecture-style"),
    ("chapter-11", "11-the-modular-monolith-architecture-style"),
    ("chapter-12", "12-pipeline-architecture-style"),
    ("chapter-13", "13-microkernel-architecture-style"),
    ("chapter-14", "14-service-based-architecture-style"),
    ("chapter-15", "15-event-driven-architecture-style"),
    ("chapter-16", "16-space-based-architecture-style"),
    ("chapter-17", "17-orchestration-driven-service-oriented-architecture"),
    ("chapter-18", "18-microservices-architecture"),
    ("chapter-19", "19-choosing-the-appropriate-architecture-style"),
    ("chapter-20", "20-architectural-patterns"),
    ("chapter-21", "21-architectural-decisions"),
    ("chapter-22", "22-analyzing-architecture-risk"),
    ("chapter-23", "23-diagramming-architecture"),
    ("chapter-24", "24-making-teams-effective"),
    ("chapter-25", "25-negotiation-and-leadership-skills"),
    ("chapter-26", "26-architectural-intersections"),
    ("chapter-27", "27-the-laws-of-software-architecture-revisited"),
    ("appendix", "appendix-discussion-questions"),
)

SOFTWARE_ARCHITECTURE_LEGACY_TO_CANONICAL = dict(SOFTWARE_ARCHITECTURE_ROUTE_MAP)
SOFTWARE_ARCHITECTURE_CANONICAL_STEMS = tuple(
    canonical for _, canonical in SOFTWARE_ARCHITECTURE_ROUTE_MAP
)
SOFTWARE_ARCHITECTURE_POSITIONS = {
    canonical: position
    for position, (_legacy, canonical) in enumerate(SOFTWARE_ARCHITECTURE_ROUTE_MAP, start=1)
}
SOFTWARE_ARCHITECTURE_READER_ALIASES = {
    **SOFTWARE_ARCHITECTURE_LEGACY_TO_CANONICAL,
    **{
        f"ch-item-{index}": canonical
        for index, canonical in enumerate(SOFTWARE_ARCHITECTURE_CANONICAL_STEMS)
    },
}
