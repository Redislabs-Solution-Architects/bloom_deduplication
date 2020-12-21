def runIt(x):
    val = x['value']['Value']
    name = x['value']['Name']
    #execute('TS.INCRBY', 's-unfiltered', 1, 'TIMESTAMP', int(int(x['id'].split('-')[0])/1000))
    execute('TS.INCRBY', 's-unfiltered', 1, 'TIMESTAMP', '*')
    j = execute("BF.ADD", val, "DEDUP")
    if j > 0:
        #execute('TS.INCRBY', 's-filtered', 1, 'TIMESTAMP', int(int(x['id'].split('-')[0])/1000))
        execute('TS.INCRBY', 's-filtered', 1, 'TIMESTAMP', '*')

gb =  GearsBuilder(
        reader = 'StreamReader',
        desc   = "Process messages")

gb.map(runIt)
gb.register('outfill')
