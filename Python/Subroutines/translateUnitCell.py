#Copyright Thomas Dixon 2015

#convert the unit cell paramenters to Cartesian coordinates
def convertToCartesian(unitCell):
    import math #facilitates using more intricate maths operations
    import numpy as np #facilitates matrix manipulation
    print 'Converting the unit cell basis vectors to Cartesian coordinates'
    a = float(unitCell[0])
    b = float(unitCell[1])
    c = float(unitCell[2])
    alpha = float(unitCell[3])
    beta = float(unitCell[4])
    gamma = float(unitCell[5])
    #define parameter v, which is the volume of a unit parallelepiped with the 
    #same angles as the unit cell
    v = math.sqrt(1 - math.pow((math.cos(alpha)),2) - math.pow((math.cos(beta)),2) - math.pow((math.cos(gamma)),2) + 2*(math.cos(alpha))*(math.cos(beta))*(math.cos(gamma)))
    #define the elements of the conversion matrix
    a11 = a
    a12 = b*math.cos(gamma)
    a13 = c*math.cos(beta)
    a21 = 0
    a22 = b*math.sin(gamma)
    a23 = c*(math.cos(alpha)-(math.cos(beta)*math.cos(gamma))/math.sin(gamma))
    a31 = 0
    a32 = 0
    a33 = c*(v/math.sin(gamma))
    #create the conversion matrix
    conversionMatrix = np.array([[a11,a12,a13],[a21,a22,a23],[a31,a32,a33]])
    #define the fractional basis vectors for each direction; a, b and c
    aVector = np.array([[1],[0],[0]])
    bVector = np.array([[0],[1],[0]])
    cVector = np.array([[0],[0],[1]])
    #convert the lattice basis vector in each direction to Cartesian coordinates
    aCartesianVector = np.dot(conversionMatrix, aVector)
    bCartesianVector = np.dot(conversionMatrix, bVector)
    cCartesianVector = np.dot(conversionMatrix, cVector)
    cartesianVectors = (aCartesianVector,bCartesianVector,cCartesianVector)
    print 'Conversion complete\n'
    return cartesianVectors    
#end convertToCartesian
    
#obtain an array of XYZcoordinates from input list of atom objects
def getXYZlist(atomList):
    from parsePDB import atom as a #for utilising the 'atom' class
    #initialise list with the right number of fields
    noAtoms = len(atomList)
    xyzList = [0]*noAtoms
    #strip atomic xyz coordinares or all of the input atoms
    for n in xrange (noAtoms):
        #append the xyzCoords of atom to the list
        xyzList[n] = atomList[n].xyzCoords
    return xyzList
#end getXYZlist
        
    
def translateUnitCell(atomXYZlist, cartesianVectors, aTrans, bTrans, cTrans):
    import copy #for making shallow copies of variables/lists/objects etc.
    duplicate = copy.copy
    import numpy as np #facilitates matrix manipulation
    from parsePDB import atom as a #for utilising the 'atom' class
    #create puppet list to fill with atom objects
    newXYZlist = [0]*len(atomXYZlist)
    #convert a/b/cTrans into matrices
    aTransMat = np.array([[aTrans],[aTrans],[aTrans]])
    bTransMat = np.array([[bTrans],[bTrans],[bTrans]])
    cTransMat = np.array([[cTrans],[cTrans],[cTrans]])
    #multiply a/b/cTrans matrices by the a/b/c Cartesian translation vector
    aVec = np.multiply(aTransMat,cartesianVectors[0])
    bVec = np.multiply(bTransMat,cartesianVectors[1])
    cVec = np.multiply(cTransMat,cartesianVectors[2])
    #add the three vectors together to give a single translation vector
    transVector = np.add(aVec, bVec)
    transVector = np.add(transVector, cVec)
    for n in xrange (len(atomXYZlist)):
        #apply this transformation to the atoms xyzCoords and write back to list
        newXYZlist[n] = np.add(np.array(duplicate(atomXYZlist[n])), transVector).tolist()
    print 'Successfully translated by (%2sa,%2sb,%2sc) unit cells' % (aTrans, bTrans, cTrans)
    return newXYZlist   
#end translateUnitCell