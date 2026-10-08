# Transfer folder (temporary)

`tm1-data-pipeline.patch` is the DATA 298A data-pipeline change for the team repository
(298A-Team-2-Topic-23/Low-Resource-and-Code-Switched-Language-Systems). It is parked here only so it
can be downloaded; apply it in the team repo with `git apply`, commit it there under your own
account, then delete this folder.

`files/` holds the same change as plain files at their repo-relative paths, for updating a working
tree where an older version of the patch was already applied:
`git archive FETCH_HEAD tm1-transfer/files | tar -x --strip-components=2`
