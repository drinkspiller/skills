# Evaluation Rubrics & Calibration

Rigorous evaluation separates transformative concepts from clever decoration.
This document establishes the multi-axis evaluation rubric, competitor swap
verification checks, and the "Kill Your Darlings" stress-testing protocol for
Phase 4 (`EVALUATE`).

--------------------------------------------------------------------------------

## 1. Axis 1: Brief Compliance (Pass/Fail Gate)

Before evaluating conceptual strength, verify candidate directions against eight
foundational compliance gates. If a concept fails any single gate, it is
disqualified from final presentation:

1.  **Single-Sentence Articulation**: Can the concept be articulated completely
    in one unambiguous sentence?
2.  **Message Clarity**: Does the intended message or technical capability read
    immediately without secondary explanation?
3.  **Insight Alignment**: Does the concept directly resolve the mined tension
    or Jobs-to-be-Done insight?
4.  **Audience Resonance**: Does the target audience (consumer, developer, or
    operator) immediately recognize their own operational reality?
5.  **Mandatory Fulfillment**: Are all explicit user requirements and technical
    constraints incorporated?
6.  **Security & Ethics**: Does the approach comply strictly with security
    policies, privacy mandates, and ethical standards?
7.  **Voice & Style Preservation**: Does the execution preserve established
    system architecture conventions or brand tone?
8.  **Attribute Support**: Is the concept supported by genuine technological
    capabilities or real product attributes?

--------------------------------------------------------------------------------

## 2. Axis 2: Multi-Axis Idea Strength (Scored Rubric)

Evaluate compliant concepts across six weighted criteria. Each criterion is
scored from 1.0 to 10.0:

| Criterion                   | Weight | Evaluation Focus                      |
| :-------------------------- | :----- | :------------------------------------ |
| **Originality**             | 0.25   | Unexpectedness. Does this break out   |
:                             :        : of standard domain design patterns?   :
| **Strategic Fit**           | 0.20   | Precision. Does this directly achieve |
:                             :        : the core objective and satisfy the    :
:                             :        : JTBD?                                 :
| **Developer / User Impact** | 0.20   | Resonance. Does this meaningfully     |
:                             :        : eliminate friction or inspire         :
:                             :        : engagement?                           :
| **Feasibility**             | 0.15   | Viability. Can this be implemented    |
:                             :        : cleanly within timeline and technical :
:                             :        : boundaries?                           :
| **Scalability**             | 0.10   | Extensibility. Does this adapt        |
:                             :        : cleanly across multi-node topologies  :
:                             :        : or future growth?                     :
| **Simplicity**              | 0.10   | Elegance. Does this apply "Simplicity |
:                             :        : as Violence" (stripping out all       :
:                             :        : incidental complexity)?               :

**Weighted Score Calculation**: \[ \text{Total Score} = \sum (\text{Criterion
Score} \times \text{Weight}) \]

**Threshold Rule**: Directions scoring below **7.0** are considered conventional
or incomplete and must not be presented as primary recommendations.

--------------------------------------------------------------------------------

## 3. Stress-Testing Protocols

### 3.1 The Competitor Swap Test (Anti-Cliché Verification)

Replace the primary product, brand, or architecture component in the concept
proposal with a direct competitor or generic industry alternative. If the
concept still functions identically without modification, it lacks
differentiating specificity (`Originality <= 5.0`). Re-anchor the design in
unique internal capabilities.

### 3.2 Kill Your Darlings Protocol

After scoring and ranking candidate approaches, identify the top-recommended
concept. Actively construct a rigorous, unsparing technical or strategic
argument *against* this chosen favorite. Expose hidden operational fragility,
unstated assumptions, or scaling bottlenecks. If the favorite cannot survive
this adversarial challenge, promote an alternative or initiate targeted Phase 4
refinement.
