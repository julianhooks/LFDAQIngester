# To-do List

`[{status}] _{date}_ {assigner git user} to {assignee git user}` 

**[TO-DO]** _05/07/2026_ @julianhooks to @julianhooks
- Fix DOCKERFILE to install drivers one stage before installing python requirements

**[TO-DO]** _05/07/2026_ @julianhooks to @julianhooks
- Fix DOCKERFILE to install correct drivers for system architecture

**[TO-DO]** _05/07/2026_ @julianhooks to @julianhooks
- Fix over-flushing bug in questDB ingress handler
  - There is an autoflush option for the handler that we should turn on

**[TO-DO]** _05/07/2026_ @julianhooks to @julianhooks
- Set up a better logging configuration (debug level in stream when in debug mode, info level in file and stream when in prod)

**[TO-DO]** _05/07/2026_ @julianhooks to @julianhooks
- Refactor `setup()` into `getInstruments()` `getLabJack()` `getIngestHandle()` `userConfig()`

**[TO-DO]** _05/07/2026_ @julianhooks to @julianhooks
- Fix `getInstruments()`, `getIngestHandle` to get login credentials from environment variables

**[TO-DO]** _05/07/2026_ @julianhooks to @julianhooks
- Build out calibration function namespace

**[TO-DO]** _05/07/2026_ @julianhooks to @julianhooks
- Develop testing plan in testing.md 

**[DONE]** _05/07/2026_ @julianhooks to @julianhooks 
- Fix bug in instrument loading loop where all instruments are loaded regardless of active status or labjack status.

