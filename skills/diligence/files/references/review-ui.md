# The review page contract

Use this contract for the three pages the lawyer reads: the review setup, the
test results, and the final crosswalk. Each is a single HTML file written to
the session's Output folder and opened in the preview pane. They are legal
review surfaces, not client presentations.

Build each page by hand from the register's own rows. A number on a page and
the same number in the register are the same number, reached the same way.

## Reading order and language

- Lead with the lawyer's decision, what it authorises and what it does not.
  Keep stable identifiers, framework versions and internal mechanics in a
  collapsed technical area or an Audit section.
- Use one status vocabulary everywhere: **Found**, **Not found**, **Needs a
  decision**, and **Needs your eyes**. Pair every status colour with its text;
  colour is never the only signal.
- "Not found" stays scoped to the supplied visible text of the identified
  review unit. It never implies absence across the room or in the world.
- Amber is for a discrete item that needs attention. Do not turn a whole page
  amber because one item needs a decision.
- Use progressive disclosure for evidence detail. Never hide the decision, the
  identity of a source, or a stop condition.
- Say on every page which tranche it covers, and which documents are not in it.

## Look and feel

- Define the palette once at the top of the page, as custom properties, with a
  light and a dark value for every foreground, surface, border, focus and
  status colour. Do not invent a second palette further down the page.
- A warm paper background, quiet white and charcoal surfaces, a deep green for
  the primary action and restrained amber and red for status is the house
  presentation. Keep the chrome quiet so the evidence stays dominant.
- System fonts only. Body text sans-serif; a restrained legal serif may carry
  principal headings and quoted agreement language; monospace is for stable
  identifiers. Weights 400 and 500 only. Secondary text stays at least 11px.
- One `LQ · Diligence Review` masthead. No nested-card dashboards, decorative
  shadows, ornamental borders, oversized icons or redundant panels of figures.
  A bounded card must carry a real decision or a real piece of evidence.

## Accessibility and width

- Work from 320px to desktop. Stack or wrap before content clips; horizontal
  scrolling is limited to tables whose columns genuinely cannot fit. No fixed
  viewport-height layouts and no internally scrolling page shell.
- Use semantic headings, links, disclosure elements, tables and native form
  controls. Preserve tab order, a visible focus treatment, a skip link and
  concise accessible names. Announce dynamic status politely; announce a
  blocker as an alert.
- Tabs carry the tablist, tab and tabpanel roles and work with clicks and
  arrow keys. Search, filters, clear actions and the theme control must
  actually work, not merely appear.
- Honour reduced-motion preferences. The first view must be useful before
  anyone interacts with it.

## Self-contained and stable

- Everything the page needs is inside it. Inline the styles and any small
  amount of script. Load no external font, stylesheet, script, image or
  service, and make no network call of any kind.
- The page carries no timestamp, machine name or absolute path, so the same
  inputs give the same page.
- Nothing on the page changes a finding, a quote, a framework item or a
  lawyer's ruling. It displays them.

## Showing the source, and what is lost

The original file is where the words came from, and a link to it is not by
itself a review experience. Every reviewed document needs something readable on
the page itself, beside the finding: the quoted passage in full, with enough of
the surrounding clause to read it in context, and the page and clause it came
from.

Where the page cannot carry the passage safely — a scanned page, an image, a
format that did not open — say so in a visible **Needs your eyes** queue with
the reason, and hold every finding that depends on it. Never turn a document
that could not be read into **Not found**.

Say the loss plainly, once, on the first page the lawyer sees: this skill does
not hand back the lawyer's own file with marks on it. It gives a page that
quotes the words and says where they sit, and the lawyer opens the original
alongside it. Do not present the quoted extract as a substitute for reading a
page whose layout matters.
