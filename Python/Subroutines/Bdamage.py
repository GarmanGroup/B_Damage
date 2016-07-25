# Copyright Thomas Dixon 2015

#calculate the distance between two atoms
def calcDist(atomA, atomB):
    from parsePDB import atom as a #for utilising the 'atom' class
    import math #for obtaining the square root
    #obtain two sets of atom coordinates for the atoms
    aCoords = atomA.xyzCoords
    bCoords = atomB.xyzCoords
    #find the linear displaements of the atoms from each other along the three Cartesian axes
    x = aCoords[0][0] - bCoords[0][0]
    y = aCoords[1][0] - bCoords[1][0]
    z = aCoords[2][0] - bCoords[2][0]
    #find the distance between the two atoms 
    d = math.sqrt(x**2 + y**2 + z**2)
    return d
#end calcDist

#method to count the number of atoms within the given radius of an atom
def countInRadius(atm, atomList, r):
    from parsePDB import atom as a #for utilising the 'atom' class
    from Bdamage import calcDist #calcualtes the distance between two atoms in 3D space
    #set packing density counter to 0
    PD = int(0)
    #for every atom
    for atom in atomList:
        #calculate the distance between the two atoms
        if calcDist(atm, atom) < r:
            #if the distance is less than the PDT, increment the counter
            PD = int(PD + 1)
        atm.pd = PD
    #return packing density of the atom once all comparisons have been made
    return
        
#Calculate packing density for all atoms in the original PDB file
def calcPDT(auAtomList, atomList, PDT):
    from parsePDB import atom as a #for utilising the 'atom' class
    from Bdamage import countInRadius #counts atoms within PDT
    #set initial values for min/maxPD
    minPD = len(atomList)
    maxPD = 0
    #for every atom in the asymmetric unit
    for atom in auAtomList:
        countInRadius(atom, atomList, PDT)
        #update min/maxPD if necessary
        if atom.pd < minPD:
            minPD = atom.pd
        elif atom.pd > maxPD:
            maxPD = atom.pd
    print 'Packing Density (PD) values successfully calculated'
    return int(minPD), int(maxPD)
#end calcPackingDensity
    
#Segregate atoms into bins based on PD
def binAtoms(atomList, binSize, minPD, maxPD):
    from parsePDB import atom as a #for utilising the 'atom' class
    import math #to utilise more intricate maths functions
    #create value for 'adjustment number' which is a factor to be taken off all
    #PDs in order to define their group number by a ceiling function
    adjtNo = (math.floor(minPD/binSize))*binSize
    #create puppet value for the highest group number
    noOfGroups = 0
    #for every atom in the atom list
    for atm in atomList:
        #reduce PD by the adjustment value
        adjdPD = atm.pd - adjtNo + 1
        #define group number as the ceiling of adjdPD divided by bin size
        groupNo = int(math.ceil(adjdPD/binSize))
        atm.gn = groupNo
        #update noOfGroups if necessary
        if groupNo > noOfGroups:
            noOfGroups = groupNo
    return noOfGroups, adjtNo
#end binAtoms
    
#calculate Bdamage value for every atom in AU
def calcBdam(atomList, numberOfGroups):
    from parsePDB import atom as a #for utilising the 'atom' class
    #initialise variables for all group numbers
    sumB = [0] * numberOfGroups
    noAtm = [0] * numberOfGroups
    avB = [0] * numberOfGroups
    #find sum of all B factors of atoms in their groups
    for atom in atomList:
        gNo = int(atom.gn - 1) #take away 1 to account for cardinality vs ordinality
        sumB[gNo] = float(sumB[gNo]) + float(atom.bFactor)
        noAtm[gNo] = int(noAtm[gNo]) + 1
    #find the average B factor for each group number
    for gNo in xrange(numberOfGroups):
        #don't calculate when 0 atoms are in the bin
        if not noAtm[gNo] == 0:
            avB[gNo] = float(sumB[gNo])/int(noAtm[gNo])
    #calculate B damage for each atom and update this value for the atom object
    for atom in atomList:
        gNo = int(atom.gn - 1)
        atom.bd = float(atom.bFactor)/float(avB[gNo])
    #return outputs of the script
    return noAtm, avB
#end calcBdam        