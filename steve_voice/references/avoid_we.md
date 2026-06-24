# Name the actor

"We" is a referential index deletion. It hides who is doing the work. A reader
hits "we check the input" and has to guess — the caller? The function? The
class? The runtime? The team that wrote it three years ago? Every guess is a
micro-interruption, and enough of them add up to a reader who stops trusting the
text.

The fix is not mechanical word-substitution. Swapping "we" for passive voice
just moves the ambiguity: "the input has already been checked for safety" still
hides who checked it, and now the sentence is longer. The fix is naming the
actual component.

`AcceptUserInput()` already validated this input above. The ingress layer
rejects malformed payloads before this function runs. `parseConfig()` normalizes
the flags on startup.

Those sentences have zero ambiguity about responsibility. A reader knows exactly
where to look when something breaks.

## When "we" adds nothing, cut it

Sometimes the subject is meaningless — the sentence works as a bare imperative.
"Check for failure" says everything "we check for failure" says, minus one
useless pronoun. If the actor contributes no information, drop it entirely.

## The passive trap

Passive voice is not the answer. "The input has already been checked for safety"
is grammatically valid and semantically empty — it tells the reader nothing
about which layer owns that responsibility. The point of avoiding "we" is not to
avoid a word. The point is to force every sentence to name its actor, so the
reader never has to guess who does what.

## Applying this in comments and documentation

Comments explain ownership. "Handles retry logic" is incomplete —
`RetryInterceptor` handles retry logic. "Ensures consistency" is a ghost claim —
`TwoPhaseCommit.prepare()` ensures consistency by acquiring row locks before the
write path commits.

The same principle applies in docs, design reviews, and chat. "The system queues
requests to avoid overwhelming the host" beats "we queue requests to avoid
overwhelming the host" because the reader knows the system does it, not some
unspecified group of humans.

One rule: every sentence names its actor. If the actor is obvious or irrelevant,
the sentence becomes imperative. There is no third option.
