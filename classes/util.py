def normalizeListMagnitudes(list):
    # Normalize the list of magnitudes
    # so that the largest magnitude is 1.0
    # and the others are scaled accordingly.
    greatestMagnitude = -70000
    lowestMagnitude = 80000
    for obj in list:
        if obj.magnitude > greatestMagnitude:
            greatestMagnitude = obj.magnitude
        elif obj.magnitude < lowestMagnitude:
            lowestMagnitude = obj.magnitude
    for obj in list:
        obj.normMagnitude = 1-(obj.magnitude + abs(lowestMagnitude))/(greatestMagnitude + abs(lowestMagnitude)) 
    return list