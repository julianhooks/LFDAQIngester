What do I want my code to look like?

main() -> Nothing
    program setup() -> Nothing
        setup logger
        labjack initLabJack() -> Labjack handle
            connect to labjack
    
        config()
            Setup non-read registers (counters, temp, etc.)            
            setup globals (server address)
            setup server configs

        getInstruments() -> instrument list 
    
        questDB write setup() -> questDBHandle

    primaryLoop() -> Nothing
        for each instrument forever:
            getUncalibratedData(labjackHandle)
            calibrateData()
            writeAllData(questDBHandle)
    onexit(handles) -> Nothing
        cleanup
