# Style Rules for Technical Documentation & Codelabs

These rules apply to all output from this skill. They're drawn from common
failure modes in AI-generated technical writing.

## Word Choice

-   Use "is" / "are". Not "serves as", "stands as", "represents", or "marks".
-   Cut magic adverbs: "quietly", "deeply", "fundamentally", "remarkably". They
    add nothing.
-   Ban list: "delve", "utilize", "leverage" (verb), "harness", "streamline",
    "robust", "tapestry", "landscape" (metaphorical), "paradigm", "synergy",
    "ecosystem" (non-literal).

## Sentence Construction

-   No negative parallelism ("It's not X -- it's Y"). State what it *is*.
-   No rhetorical Q&A ("The result? Devastating."). Just make your point.
-   No countdown reveals ("Not X. Not Y. Just Z."). Say Z.
-   No gerund fragment litanies ("Fixing bugs. Writing tests. Shipping code.").
    Write complete sentences.
-   No filler transitions: "It's worth noting", "Importantly", "Interestingly",
    "Notably". If it's worth noting, note it. Don't announce that you're noting
    it.
-   No false ranges ("From X to Y") unless X and Y are on an actual spectrum.
-   No superficial -ing suffixes ("highlighting its importance", "underscoring
    its role"). These are analysis-flavored noise.

## Paragraph Structure

-   Don't fragment sentences for manufactured emphasis. ("He said this. Openly.
    In a meeting.") Write actual paragraphs.
-   Don't write listicles disguised as prose. ("The first consideration... The
    second consideration...") Use a list or write real paragraphs. Pick one.

## Tone

-   No false suspense: "Here's the kicker", "Here's where it gets interesting".
    Just continue writing.
-   No patronizing analogies: "Think of it as a highway for data." If the
    concept is simple enough to not need an analogy, don't force one. If it does
    need one, make it good.
-   No "Imagine a world where..." futurism. Describe what exists.
-   No fake vulnerability or self-awareness: "And yes, I'll admit..."
-   Don't claim something is "simple" or "clear". Demonstrate it instead.
-   Don't inflate stakes. A config change is a config change, not "a pivotal
    moment in the evolution of the system".
-   No "Let's break this down" / "Let's unpack this" / "Let's dive in". Just do
    it.
-   No vague attributions: "experts say", "industry reports suggest". Name the
    source or drop the claim.

## Formatting

-   Two em-dashes max per document.
-   No bold-first bullets (`**Keyword**: description`). Vary your list style.
-   Use straight quotes and `->` or `=>`. No unicode arrows or smart quotes.

## Composition

-   Don't summarize what you're about to say, then say it, then summarize what
    you said. State things once.
-   Don't beat a single metaphor to death. Use it, move on.
-   Don't stack historical analogies ("Apple did X, Google did Y, Amazon did
    Z...") to build false authority. One good example beats five shallow ones.
-   Don't pad a single idea into multiple sections. If the point fits in one
    section, use one section.
-   Don't write "In conclusion" or "To sum up". The reader knows it's the end.
-   Don't use the "Despite its challenges, it continues to thrive" formula. If
    there are real trade-offs, discuss them honestly in a dedicated section.

## Technical Writing Specifics

-   Name the file. Every code block needs a file path.
-   Show expected output after commands.
-   Use real paths, real class names, real function names. No placeholders like
    "YourClass" or "/path/to/your/file" unless it's genuinely variable.
-   Inline comments in code > prose explanations of code. Put the explanation
    where the reader's eyes already are.
-   One concept per code block. Don't demonstrate three things at once.
