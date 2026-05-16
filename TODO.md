# To-do List

`**[{status}]** _{date_assigned}_ -> _{date_completed}_ {assigner git user} to {assignee git user}` 

**[IN-PROGRESS]** _05/07/2026_ @julianhooks to @julianhooks
- Fix over-flushing bug in questDB ingress handler
  - There is an autoflush option for the handler that we should turn on

**[TO-DO]** _05/07/2026_ @julianhooks to @julianhooks
- Set up a better logging configuration (debug level in stream when in debug mode, info level in file and stream when in prod)

**[TO-DO]** _05/07/2026_ @julianhooks to @julianhooks
- Fix `getInstruments()`, `getIngestHandle` to get login credentials from environment variables

**[TO-DO]** _05/07/2026_ @julianhooks to @julianhooks
- Develop testing plan in testing.md 

**[TO-DO]** _05/07/2026_ @julianhooks to @julianhooks
- Add `calibration.py` for calibration function clean up
  - Build out calibration function namespace with usable timer functions

**[TO-DO]** _05/07/2026_ @julianhooks to @julianhooks
- Fix DOCKERFILE to install drivers one stage before installing python requirements

**[TO-DO]** _05/07/2026_ @julianhooks to @julianhooks
- Fix DOCKERFILE to install correct drivers for system architecture

**[TO-DO]** _05/15/2026_ @julianhooks to @julianhooks
- Add docstrings to existing functions

**[DONE]** _05/07/2026_ -> _05/07/2026_ @julianhooks to @julianhooks 
- Fix bug in instrument loading loop where all instruments are loaded regardless of active status or labjack status.

**[DONE]** _05/15/2026_ -> _05/15/2026_ @julianhooks to @julianhooks
- Add type annotations via `typing.Annotated` and regular type hints

**[DONE]** _05/07/2026_ -> _05/15/2026_ @julianhooks to @julianhooks
- Refactor `setup()` into `getInstruments()` `getLabJack()` `getIngestHandle()` and ~~`userConfig()`~~ `setup()`
- May make `userConfig()` into `setup()` and move non-user adjustable setup tasks into `main()`
  - Seems cleaner this way
- Also needed to update onexit to account for `getIngestHandle()` making it possible to refactor away from mnually calling `__enter__` in `setup`