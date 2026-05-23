## Test design notes

A full test suite should live in `tests.py`. This woul run all function level tests and spin up a QuestDB instance for integration testing. To do that, it would have to also run something with docker compose, which is unfortunate because I'd rather just run `py tests.py` than some weird docker compose thing.

As functions are refactored into their own files for cleanliness, function level test suites should be made in those files as well. 

For tests that require a QuestDB instance, their should ideally be a way to test functionality without spinning up a full database. I don't know how that should work yet.

For tests requiring `labjack ljm` functions, I think the best solution for non hardware testing is just redefining functions in the test scope to avoid `NO DEVICE FOUND` errors. I think this could be hard, so it's worth thinking about in more detail

I'd also like a way to verify changes do not break the docker image, preferably automatically when I run the highest level test.

## TO-DO

1. **[DONE]** split `main.py` into an appropriate number of files.
2. **[TO-DO]** write function level tests
3. **[TO-DO]** Write project-level test suite into `tests.py`
4. **[TO-DO]** Figure out docker compose based testing