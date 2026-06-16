# To-do List

`**[{status}]** _{date_assigned}_ -> _{date_completed}_ {assigner git user} to {assignee git user}` 

**[IN-PROGRESS]** _06/12/2026_ @julianhooks to @julianhooks 
- Fix faulty name errors triggered by pylint (_From ai suggestions_) 
- Got through all modules

**[TO-DO]** _05/15/2026_ @julianhooks to @julianhooks
- Add docstrings to existing functions

**[IN-PROGRESS]** _05/07/2026_ @julianhooks to @julianhooks
- Develop testing plan in testing.md 

**[TO-DO]** _05/07/2026_ @julianhooks to @julianhooks
- Add `calibration.py` for calibration function clean up
  - Build out calibration function namespace with usable timer functions

**[TO-DO]** _06/12/2026_ @julianhooks to @julianhooks 
- Fix docker image to work on arm64 and amd64 (_From_ai_suggestions_)
- Make sure build tools are not included in imaging (_From_ai_suggestions_) 

**[TO-DO]** _05/07/2026_ @julianhooks to @julianhooks
- Fix DOCKERFILE to install correct drivers for system architecture

**[TO-DO]** _05/07/2026_ @julianhooks to @julianhooks
- Fix DOCKERFILE to install drivers one stage before installing python requirements

**[TO-DO]** _05/20/2026_ @julianhooks to @julianhooks
- Modify `ingestLoop()` to use a pandas dataframe to store data instead of using individual rows populated during the instrument loop
  - Docs say this should increase performance, and it is the preferred method for sending data

**[DONE]** _06/12/2026_ -> _06/16/26_ @julianhooks to @julianhooks 
- Refactor `ingester.py` into a single class

**[DONE]** _06/12/2026_ -> _06/16/26_ @@julianhooks to @julianhooks 
- Refactor `instrument.py` into a single class

**[DONE]** _06/12/2026_ -> _06/16/26_ @@julianhooks to @julianhooks 
- Refactor `labjack_handle.py` into a single class

**[DONE]** _06/12/2026_ -> _06/16/26_ @@julianhooks to @julianhooks 
- Refactor `questdb_handle.py` into a single class

**[DONE]** _06/12/2026_ @julianhooks to @julianhooks 
- refactor code into modules (_From ai suggestions_)

**[DONE]** _05/07/2026_ -> _05/07/2026_ @julianhooks to @julianhooks 
- Fix bug in instrument loading loop where all instruments are loaded regardless of active status or labjack status.

**[DONE]** _05/15/2026_ -> _05/15/2026_ @julianhooks to @julianhooks
- Add type annotations via `typing.Annotated` and regular type hints

**[DONE]** _05/07/2026_ -> _05/15/2026_ @julianhooks to @julianhooks
- Refactor `setup()` into `getInstruments()` `getLabJack()` `getIngestHandle()` and ~~`userConfig()`~~ `setup()`
- May make `userConfig()` into `setup()` and move non-user adjustable setup tasks into `main()`
  - Seems cleaner this way
- Also needed to update onexit to account for `getIngestHandle()` making it possible to refactor away from mnually calling `__enter__` in `setup`

**[DONE]** _05/07/2026_ -> _05/15/2026_ @julianhooks to @julianhooks
- Fix over-flushing bug in questDB ingress handler
  - There is an autoflush option for the handler that we should turn on

**[DONE]** _05/07/2026_ -> _05/15/2026_ @julianhooks to @julianhooks
- Set up a better logging configuration (debug level in stream when in debug mode, info level in file and stream when in prod)
- Pulling some recipes from [this doc](https://docs.python.org/3/howto/logging-cookbook.html)

**[DONE]** _05/07/2026_ -> _5/16/2026_ @julianhooks to @julianhooks
- Set up environment variables for implementation specific or run specific information
  - Placed all environment variables in `.env`, with preface `LFDAQ_`
  - Added defaults in dockerfile so cloning `.env` into `DAQService` is not necesary
- Fix `getInstruments()`, `getIngestHandle` to get login credentials from environment variables
