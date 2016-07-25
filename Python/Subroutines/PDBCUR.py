# Copyright Thomas Dixon 2015

def genPDBCURinputs(PDBCURinputFile):
    import os #for operating system usability
    #check if an input file has already been created
    if os.path.exists(PDBCURinputFile):
        #inform user file already exists
        print 'Input file for PDBCUR already exists at %s' % PDBCURinputFile
        #exit method if file exists
        return    
    #open a text file for writing
    print 'Creating input file for PDBCUR at %s' % PDBCURinputFile
    #write input keywords to file for use with PDBCUR
    with open(PDBCURinputFile,'w') as f:
        #delhydrogen keyword removes all hydrogen atoms from PDB
        f.write('delhydrogen\n')
        #cutocc keyword removes all atoms with occupancy of 0 from PDB
        f.write('cutocc\n')
        #mostprob keyword only keeps atoms from conformations with the highest occupancy
        #if equal occupancies then only one is retained (A)
        f.write('mostprob\n')
        #noanisou keyword removes all ANISOU information from PDB
        f.write('noanisou\n')
        #genunit keyword generates a unit cell
        f.write('genunit\n')
        f.close
#end genPDBCURinputs
        
def runPDBCUR(pathToPDB, PDBCURoutputPDB, PDBCURinputFile, PDBCURlog, owChoice):
    import os #for operating system usability
    prompt = '> '
    #check if output file has already been created
    if os.path.exists(PDBCURoutputPDB):
        #inform user file already exists
        print 'Output file from PDBCUR already exists at %s\n' % PDBCURoutputPDB
        if owChoice == 'all':
            print 'Overwriting existing file'
            #delete the exisiting file and continue with method
            os.remove(PDBCURoutputPDB)
        #exit method if file exists
        elif owChoice == 'none':
            return
        else:
            print 'Do you want to overwrite the existing file?\n'
            print '--USER INPUT-- type your choice and press RETURN\n'
            print 'yes = overwrite this file (DEFAULT)'
            print 'no = do not overwrite this file'
            owChoice = raw_input(prompt)
            if owChoice == 'yes':
                print 'Overwriting existing file'
                #delete the exisiting file and continue with method
                os.remove(PDBCURoutputPDB)
            elif owChoice == 'no':
                return
            else:
                print 'Overwriting existing file'
                #delete the exisiting file and continue with method
                os.remove(PDBCURoutputPDB)
    #create a string for command line input to run PDBCUR
    runPDBCURcommand = 'pdbcur xyzin %s xyzout %s < %s > %s' % (pathToPDB, PDBCURoutputPDB, PDBCURinputFile, PDBCURlog)
    #run PDBCUR to specifications
    print 'Running PDBCUR (Winn et al. 2011) to process the PDB file'
    os.system(runPDBCURcommand)
    #inform user of generated PDBCUR output file
    print 'PDBCUR log is printed below\n'
    #print PDBCUR output to log file
    PDBCURlogText = open(PDBCURlog,'r')
    for line in PDBCURlogText:
        print line
    PDBCURlogText.close()
    #delete separate PDBCUR log file and input file
    os.remove(PDBCURlog)
#end runPDBCUR 