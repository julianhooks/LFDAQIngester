What do I want my code to look like?

main() -> Nothing
    program config() -> Nothing
        setup logger

    program userconfig() -> Nothing    
        setup globals (server address)
        setup server configs

    labjack setup() -> Labjack handle
        connect to labjack
        labjack userconfig()
            Setup non-read registers (counters, temp, etc.)            

    getInstruments() -> instrument list 
    
    questDB write setup() -> questDBHandle

    primaryLoop() -> Nothing
        for each instrument forever:
            getUncalibratedData(labjackHandle)
            calibrateData()
            writeAllData(questDBHandle)
