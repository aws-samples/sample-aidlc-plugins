# Visual design for HTML mockups (visual-mockups)

How the design agent makes the HTML preview in rough-mockups and refined-mockups look designed
rather than generated, without changing what the mockup says. The markdown mockup stays the
specification; the HTML is how a person judges it. Figma renders follow Figma's own skills and the
file's design system instead of this page.

The core guides in this folder (UX guide, wireframing, interaction patterns, accessibility) still
decide behaviour and usability. This page decides the look.

## 1. Content comes only from the documents

A mockup is checked against the requirements. A value that looks real but came from nowhere gets
read as a requirement.

- Show every screen and every state the markdown names, with its example values exactly as written.
- A field the documents name but give no value for shows `—` (or a short "no example yet" in the
  workflow's language). Never fill it with a plausible name, amount, date, time, ID, address or
  payment method.
- Do not add screens, columns, buttons, filters or wording the documents do not have. When the
  layout seems to need one, list it as a question in the stage's notes instead.
- A list keeps all the example rows the documents give, unless a document says a filter hides one.
- Parts the documents mark as an assumption stay visibly marked (a dashed outline and a small label).

## 2. Decide the direction before writing markup

Write these answers as an HTML comment at the top of the file, a few words each. Refined-mockups
reads them and keeps them unless its documents change them.

- **Person:** who opens this screen, in what situation (taken from the stories and personas).
- **Job:** the one thing they came to do on each screen. That becomes the screen's focal point.
- **Feel:** two or three words that are about this product, not "clean and modern". A warehouse
  console, a clinic front desk and a shopping app call for different densities and tones.
- **Domain:** a handful of words and colours that belong to the product's world (materials,
  documents, signage, equipment), and one element that could only belong to this product.
- **Defaults to avoid:** name the three choices any generated screen of this kind would make, so
  you can decide against them on purpose.

## 3. Hierarchy

- **One focal point per screen.** The element tied to the job is the largest, the highest-contrast
  or the one with the most space around it. Everything else is deliberately quieter.
- **A type scale, not sizes picked one by one.** Choose one ratio (about 1.2 for dense tools, 1.25
  for most product screens) from a 14–16 px body and round to whole pixels.
- **Weight and colour carry most of the hierarchy.** Value, label and metadata can share one size
  and still separate by weight (600 / 500 / 400) and by text colour (primary / secondary / muted).
  Use four text tones at most.
- **Density is chosen once.** Pick the padding for this product (tight for operations consoles,
  roomier for occasional-use screens) and use the same values everywhere.
- **Group, then separate.** Related controls sit close; groups are divided by clearly larger space
  rather than by more lines.
- **Widths mean something.** A narrow side list next to wide content says the list serves the
  content; make proportions say what the screen is about.

## 4. Colour, surfaces and edges

- **Mostly neutral.** Roughly six parts base surface, three parts secondary tone, one part accent.
- **One accent colour** for the primary action and the focal element. Status colours (success,
  warning, error) appear only where they report a status, on pale tints with dark text.
- **Colours come from the domain list** in step 2. Name the CSS custom properties after the product's
  world where you can (`--ledger`, `--signal`), not only after their shade.
- **Surfaces step by a few percent of lightness.** Page, card and popover differ slightly; the side
  navigation uses the page colour with a hairline edge, not a second background. Inputs sit a touch
  darker than their surroundings.
- **Soft edges.** Borders are low-contrast hairlines, found when looked for and invisible otherwise.
- **One depth method for the whole file:** hairline borders, or one soft shadow, or tonal steps.
  Do not mix them.
- **A radius scale:** small for inputs and buttons, medium for cards, larger for dialogs. A child
  inside a rounded parent gets a smaller radius than the parent.

## 5. Components and states

- Use the native element for the job: `<button>`, `<a>`, `<input>`, `<select>`, `<table>`,
  `<dialog>`. Keep visible keyboard focus (a 2 px ring in the accent colour).
- Every interactive element has default, hover, focus and disabled looks. Show loading, empty and
  error states wherever the documents define them, and only there.
- Click and tap targets are at least 40 px high (44 px where space allows).
- Numbers that line up in columns or change (amounts, counts, quantities, dates) use
  `font-variant-numeric: tabular-nums`; codes and IDs may use a monospace face.
- One self-contained file: system font stacks, inline CSS and JavaScript, no web font, CDN or image.

## 6. Motion

- Content is visible the moment the page loads. No entrance animation on screens, rows or cards:
  a person paging through states, a screenshot and a reviewer should all see the finished screen.
- Feedback transitions (hover, press, a panel opening) stay under 200 ms, change only `transform`
  and `opacity`, and are turned off under `prefers-reduced-motion`.

## 7. What gives a generated screen away

- Every element the same size and weight, so nothing leads.
- The same card, gap and density repeated across the whole page.
- Heavy borders or strong shadows as the first thing the eye meets.
- Several accent colours, or colour and gradients used as decoration.
- A different background hue for each region.
- Large radius on small controls; thick decorative frames.
- Missing hover, focus, empty or error states.
- Values invented to make the screen look full (see section 1).

## 8. Before presenting

- **Content check:** every value on screen appears in the documents or shows `—`.
- **Squint check:** with the screen blurred, the focal point and the groups are still clear and
  nothing jumps out harshly.
- **Swap check:** if the palette and type were replaced with the usual defaults, would the screen
  lose anything? Where it would not, the choice was a default; revisit it.
- **Rough and refined match:** the refined section reuses the rough section's custom properties and
  direction comment, changing only what the refined documents change.
