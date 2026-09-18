## Start by finding the wiki

The wiki lives in a folder the lawyer owns and names, in their own file store —
not inside this skill. Nothing here is executed: every note, index, log entry and
receipt is Markdown you read and write yourself, with no hidden machine state, no
lock and no automatic history behind them.

Read [the wiki layout contract](references/wiki_schema.md), and
[the OKF profile](references/okf-profile.md) it implements, before changing
files, and follow it as written: it describes only what can be kept by hand. Files
cannot be deleted here, so a note is withdrawn rather than removed, and a
confidentiality leak is something you report and the lawyer clears.

Resolve which wiki, in this order:

1. If the user named a folder, use it.
2. Otherwise use the wiki folder already used earlier in this conversation.
3. Otherwise ask, and suggest `Documents/Cowork/wiki` as the default.
4. If a named folder is not there, say so and ask; never create a replacement
   silently, and never scan for a folder that looks like a wiki.

Ask setup questions only when no usable wiki has been named. Set up one default
wiki unless the user asks for several. Once the folder is settled, say its name
once and keep using it for the rest of the conversation; do not ask again.
