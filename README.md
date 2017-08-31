# svn-shelve

Guido van Rossum, while at Google, led the development of 'Mondrian' [[video](https://www.youtube.com/watch?v=CKjRt48rZGk)]
which was a code review UI for a tech that existed on the command-line for a couple of years. The year was 2006. This
was 18 months before GitHub launched with pull-requests - for arbitrary branching models (even if they did
[popularize their own model - GitHub Flow](https://guides.github.com/introduction/flow/)).

Google's branching model was trunk-based development, and Googlers were required to fit that model (thousands of them
in one monorepo), and code review was essential in order to not break the build. Plucking a pending commit from a
developer's (or test engineer's) workstation, taking it to somewhere central for review (and CI + telemetry) is
essential if you want to **never break the build**, and have no commit that requires follow up work to fit
standards, patterns, eliminate bugs that more experienced people could see at the outset.

Google's system would take a tar.gz from your dev workstation and pull/push it to the build/review infra. Probably
unpacking it and writing rows to a database to support the Mondrian UI and workflow.

Maybe the same can be done as supplementary commands for Subversion. You get to stay in Subversion (if you want),
for a trunk-based development branching model, but also have pre-integrate review, CI, etc.

Maybe Git is an admirable tool for facilitating that. And Python (well it's easy to prototype in it).

Let's start with 'shelve' (and un-shelve).

After that, Pull-Request, stash and others.

