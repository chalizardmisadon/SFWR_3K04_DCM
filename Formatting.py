def createField(string):
    create frame
    create label
    create entry
    dictionary[string]['frame'] = frame
    dictionary[string]['label'] = label
    dictionary[string]['entry'] = entry
    dictionary[string]['array'] = array


def updateArray(string, array):
    dictionary[string]['array'] = array
    


createField("Lower Rate Limit")
