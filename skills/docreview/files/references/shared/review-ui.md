# The review page contract

Use this contract for the pages the lawyer reads: the review setup page, the
privilege queue and the Requests and Documents findings page. Each is a single
HTML file written to the session's Output folder and opened in the preview
pane. They are legal review surfaces, not client presentations.

Build each page by hand from the register's own rows. A number on a page and
the same number in the register are the same number, reached the same way.

## Reading order and language

- Lead with the lawyer's decision, what it authorises and what it does not.
  Keep stable identifiers, framework versions and internal mechanics in a
  collapsed technical area.
- Write everything the lawyer reads in ordinary legal-review language. Internal
  words such as call, bundle, batch and staged may appear in a collapsed
  technical area, never as the label on a decision or a next action.
- Use one status vocabulary everywhere: **Responsive**, **Nothing found**,
  **Needs a decision**, **Needs your eyes** and **Held**. Pair every status
  colour with its text; colour is never the only signal.
- "Nothing found" stays scoped to the supplied visible text of the identified
  unit. It never implies absence across the production or in the world.
- Amber is for a discrete item that needs attention. Do not turn a whole page
  amber because one item needs a decision.
- Where the framework holds request sets that were outside this comparison,
  head that section **Scope of this page** and say plainly that no result,
  positive or negative, was reached for them. Do not show an unexplained count
  of requests that were not checked.
- For a scanned or image-only file, ask the lawyer to look at every page and at
  the proposed matches and non-matches before marking it reviewed. Do not ask
  them to confirm a bundle.
- Say on every page which tranche it covers, and which documents are not in it.

## Privilege on the page

- The held count and the held labels appear before any finding, on the first
  page the lawyer sees in the session.
- A held unit shows its label, its state and nothing else. No quote, no
  extract, no characterization, no first line.
- The page never releases a hold and never changes a privilege state. It
  displays what the register says.

## Look and feel

- Define the palette once at the top of the page, as custom properties, with a
  light and a dark value for every foreground, surface, border, focus and
  status colour. Do not invent a second palette further down the page.
- A warm paper background, quiet white and charcoal surfaces, a deep green for
  the primary action and restrained amber and red for status is the house
  presentation. Keep the chrome quiet so the evidence stays dominant.
- System fonts only. Body text sans-serif; a restrained legal serif may carry
  principal headings and quoted document language; monospace is for stable
  identifiers. Weights 400 and 500 only. Secondary text stays at least 11px.
- One `LQ · Document Review` masthead. No nested-card dashboards, decorative
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
  service, and make no network call of any kind. The page is opened in the
  preview pane from the Output folder, not from anywhere on disk.
- The page carries no timestamp, machine name or absolute path, so the same
  rows give the same page.
- Nothing on the page changes a finding, a quote, a framework item, a privilege
  state or a lawyer's ruling. It displays them.

## Showing the source, and what is lost

A link to the produced file is where the words came from, and it is not by
itself a review experience. Every reviewed document that is not held needs
something readable on the page beside the finding: the quoted passage in full,
with enough of the surrounding text to read it in context, and where it sits.

Where the page cannot carry the passage — a scan, an image, a format that did
not open, an encrypted file — say so in a visible **Needs your eyes** or parked
queue with the reason, and hold every finding that depends on it. Never turn a
document that could not be read into **Nothing found**.

Say the loss plainly, once, on the first page the lawyer sees: this skill does
not hand back a marked-up copy of the production. It gives a page that quotes
the words and says where they sit, and the lawyer opens the original alongside
it. Do not present a quoted extract as a substitute for reading a page whose
layout matters.
