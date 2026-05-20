A full test suite will live in `tests.py`. This will include running all function level tests and spinning up a QuestDB instance.

As functions are refactored into their own files for cleanliness, function level test suites will be moved into those folders as well. For tests that require a questDB instance, we can either spin one up for a full test, or point the http requests back to us and run a check to see if they look right. I think spinning up a db is easier but takes more time to run, while request checking would be faster to run but take longer to develop.

1. **[TO-DO]** split `main.py` into an appropriate number of files.
2. **[TO-DO]** write function level tests
3. **[TO-DO]** Write project-level test suite into `tests.py`
4. **[TO-DO]** Figure out docker image testing