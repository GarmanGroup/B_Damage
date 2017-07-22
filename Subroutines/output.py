

class generate_output_files():
    def __init__(self, pdb_file_path, df):
        self.pdb_file_path = pdb_file_path
        self.pdb_code = pdb_file_path.split('/')[-1]
        self.df = df

    def make_csv(self, bdamatomList, window):
        # Returns a csv file containing a complete set of atom information
        # (including both that provided in the input PDB file and also the
        # BDamage values calculated by RABDAM) for all atoms considered for
        # BDamage analysis. (This provides the user with a copy of the raw data
        # which they can manipulate as they wish.)

        newFile = open('%s_BDamage.csv' % self.pdb_file_path, 'w')

        # Defines column header abbreviations
        newFile.write('REC = RECORD NAME\n'
                      'ATMNUM = ATOM SERIAL NUMBER\n'
                      'ATMNAME = ATOM NAME\n'
                      'CONFORMER = ALTERNATE LOCATION INDICATOR\n'
                      'RESNAME = RESIDUE NAME\n'
                      'CHAIN = CHAIN IDENTIFIER\n'
                      'RESNUM = RESIDUE SEQUENCE NUMBER\n'
                      'XPOS = ORTHOGONAL COORDINATES FOR X IN ANGSTROMS\n'
                      'YPOS = ORTHOGONAL COORDINATES FOR Y IN ANGSTROMS\n'
                      'ZPOS = ORTHOGONAL COORDINATES FOR Z IN ANGSTROMS\n'
                      'OCC = OCCUPANCY\n'
                      'BFAC = B FACTOR (TEMPERATURE FACTOR)\n'
                      'ELEMENT = ELEMENT SYMBOL\n'
                      'CHARGE = CHARGE ON ATOM\n'
                      'PD = PACKING DENSITY (ATOMIC CONTACT NUMBER)\n')
        newFile.write('AVRG_BF = AVERAGE B FACTOR FOR ATOMS IN A SIMILAR '
                      'PACKING DENSITY ENVIRONMENT (SLIDING WINDOW SIZE '
                      '= %s)\n' % window)
        newFile.write('BDAM = B DAMAGE VALUE\n'
                      '\n')
        # Writes column headers
        newFile.write('REC' + ','
                      'ATMNUM' + ','
                      'ATMNAME' + ','
                      'CONFORMER' + ','
                      'RESNAME' + ','
                      'CHAIN' + ','
                      'RESNUM' + ','
                      'XPOS' + ','
                      'YPOS' + ','
                      'ZPOS' + ','
                      'OCC' + ','
                      'BFAC' + ','
                      'ELEMENT' + ','
                      'CHARGE' + ','
                      'PD' + ','
                      'AVRG_BF' + ','
                      'BDAM' + '\n')

        # Writes properties of each atom considered for BDamage analysis.
        for atm in bdamatomList:
            newFile.write(atm.lineID + ',')
            newFile.write(str(atm.atomNum) + ',')
            newFile.write(atm.atomType + ',')
            newFile.write(atm.conformer + ',')
            newFile.write(atm.resiType + ',')
            newFile.write(atm.chainID + ',')
            newFile.write(str(atm.resiNum) + ',')
            newFile.write(str(atm.xyzCoords[0][0]) + ',')
            newFile.write(str(atm.xyzCoords[1][0]) + ',')
            newFile.write(str(atm.xyzCoords[2][0]) + ',')
            newFile.write(str(atm.occupancy) + ',')
            newFile.write(str(atm.bFactor) + ',')
            newFile.write(atm.atomID + ',')
            newFile.write(str(atm.charge) + ',')
            newFile.write(str(atm.pd) + ',')
            newFile.write(str(atm.avrg_bf) + ',')
            newFile.write(str(atm.bd) + '\n')

        newFile.close()

    def make_histogram(self, threshold, highlightAtoms):
        # Returns a kernel density estimate of the BDamage values of every atom
        # considered for BDamage analysis. Any atom whose number is listed
        # in the highlightAtoms option in the input file will be marked on the
        # plot. (Note that it is recommended no more than 6 atoms are listed
        # in the highlightAtoms option in the input file (beyond 6 atoms, the
        # colour scheme will repeat itself, and in addition the key may not fit
        # onto the graph).)

        import matplotlib.pyplot as plt
        import seaborn as sns

        plt.clf()  # Prevents the kernel density estimate of all atoms
        # considered for BDamage analysis from being plotted on the same axes
        # as the kernel density estimate of the atoms considered for
        # calculation of the Bnet summary metric

        # Generates kernel density plot
        plot = sns.distplot(self.df.BDAM.values, hist=False, rug=True)

        # Marks on the positions of any atoms whose numbers are listed in the
        # highlightAtoms option specified in the input file.
        xy_values = plot.get_lines()[0].get_data()
        y_values = xy_values[1]

        highlighted_atoms = []
        for number in highlightAtoms:
            for index, value in enumerate(self.df.ATMNUM.values):
                if int(number) == value:
                    b_dam_value = self.df.BDAM.values[index]
                    line, = plt.plot([b_dam_value, b_dam_value],
                                     [0, max(y_values)], linewidth=2,
                                     label=' atom ' + str(number) +
                                     '\n BDamage = {:.2f}'.format(b_dam_value))
                    highlighted_atoms.append(line)
                    break

        if len(highlighted_atoms) >= 1:
            plt.legend(handles=highlighted_atoms)
        plt.xlabel('B Damage')
        plt.ylabel('Normalised Frequency')
        plt.title(self.pdb_code + ' kernel density plot')
        plt.savefig(self.pdb_file_path + '_BDamage.png')

    def calculate_Bnet(self, window_name, pdt_name):
        # Plots a kernel density estimate of the BDamage values of Glu O and
        # Asp O atoms. The summary metric Bnet is then calculated as the ratio
        # of the areas under the curve either side of the median (of the
        # overall BDamage distribution).

        import os
        import matplotlib.pyplot as plt
        import seaborn as sns
        import pandas as pd

        # Calculates median of overall BDamage distribution
        median = self.df.BDAM.median()

        # Selects Glu / Asp terminal oxygen atoms from complete DataFrame.
        a = self.df[(self.df.RESNAME.isin(['GLU']))
                    & (self.df.ATMNAME.isin(['OE1', 'OE2']))]
        b = self.df[(self.df.RESNAME.isin(['ASP']))
                    & (self.df.ATMNAME.isin(['OD1', 'OD2']))]
        dataframes = [a, b]
        prot = pd.concat(dataframes)
        # Selects atoms of sugar-phosphate C-O bonds from complete DataFrame.
        na = self.df[self.df.ATMNAME.isin(["O3'", "O5'", "C3'", "C5'"])]

        if prot.empty and na.empty:
            print('\nNo sites used for Bnet calculation present in structure\n')

        if not prot.empty:
            plt.clf()  # Prevents the kernel density estimate of the atoms
            # considered for calculation of the Bnet summary metric from being
            # plotted on the same axes as the kernel density estimate of all
            # atoms considered for BDamage analysis.
            plot = sns.distplot(prot.BDAM.values, hist=False, rug=True)
            plt.xlabel("B Damage")
            plt.ylabel("Normalised Frequency")
            plt.title(self.pdb_code + ' kernel density plot')

            # Extracts an array of 128 (x, y) coordinate pairs evenly spaced
            # along the x(BDamage)-axis from the kernel density plot. These
            # coordinate pairs are used to calculate, via the trapezium rule,
            # the area under the curve between the smallest value of x and the
            # median (= area LHS), and the area under the curve between the
            # median and the largest value of x (= area RHS). The Bnet summary
            # metric is then calculated as the ratio of area RHS to area LHS.
            xy_values = plot.get_lines()[0].get_data()
            x_values = xy_values[0]
            y_values = xy_values[1]

            total_area_LHS = 0
            for index, value in enumerate(y_values):
                if x_values[index] < median:
                    area_LHS = (((y_values[index] + y_values[index+1]) / 2)
                                * ((x_values[-1]-x_values[0]) / (len(x_values)-1)))
                    total_area_LHS = total_area_LHS + area_LHS

            total_area_RHS = 0
            for index, value in enumerate(y_values):
                if x_values[index] >= median and index < len(y_values)-1:
                    area_RHS = (((y_values[index] + y_values[index+1]) / 2)
                                * ((x_values[-1]-x_values[0]) / (len(x_values)-1)))
                    total_area_RHS = total_area_RHS + area_RHS

            # Calculates area ratio (= Bnet)
            ratio = total_area_RHS / total_area_LHS

            plt.annotate('Bnet = {:.1f}'.format(ratio),
                         xy=(max(x_values)*0.65, max(y_values)*0.9),
                         fontsize=10)
            plt.annotate('Median = {:.2f}'.format(median),
                         xy=(max(x_values)*0.65, max(y_values)*0.85),
                         fontsize=10)
            plt.savefig(self.pdb_file_path + '_Bnet_Protein.png')

            if not os.path.isfile('Logfiles/Bnet_Protein.csv'):
                Bnet_list = open('Logfiles/Bnet_Protein.csv', 'w')
                Bnet_list.write('PDB' + ',')
                Bnet_list.write('Bnet' + ',')
                Bnet_list.write('Window_size (%)' + ',')
                Bnet_list.write('PDT' + ',')
                Bnet_list.close()
            Bnet_list = open('Logfiles/Bnet_Protein.csv', 'a')
            Bnet_list.write('\n%s' % self.pdb_code + ',')
            Bnet_list.write('%s' % ratio + ',')
            Bnet_list.write('%s' % window_name + ',')
            Bnet_list.write('%s' % pdt_name + ',')
            Bnet_list.close()

        if not na.empty:
            plt.clf()  # Prevents the kernel density estimate of the atoms
            # considered for calculation of the Bnet summary metric from being
            # plotted on the same axes as the kernel density estimate of all
            # atoms considered for BDamage analysis.
            plot = sns.distplot(na.BDAM.values, hist=False, rug=True)
            plt.xlabel("B Damage")
            plt.ylabel("Normalised Frequency")
            plt.title(self.pdb_code + ' kernel density plot')

            # Extracts an array of 128 (x, y) coordinate pairs evenly spaced
            # along the x(BDamage)-axis from the kernel density plot. These
            # coordinate pairs are used to calculate, via the trapezium rule,
            # the area under the curve between the smallest value of x and the
            # median (= area LHS), and the area under the curve between the
            # median and the largest value of x (= area RHS). The Bnet summary
            # metric is then calculated as the ratio of area RHS to area LHS.
            xy_values = plot.get_lines()[0].get_data()
            x_values = xy_values[0]
            y_values = xy_values[1]

            total_area_LHS = 0
            for index, value in enumerate(y_values):
                if x_values[index] < median:
                    area_LHS = (((y_values[index] + y_values[index+1]) / 2)
                                * ((x_values[-1]-x_values[0]) / (len(x_values)-1)))
                    total_area_LHS = total_area_LHS + area_LHS

            total_area_RHS = 0
            for index, value in enumerate(y_values):
                if x_values[index] >= median and index < len(y_values)-1:
                    area_RHS = (((y_values[index] + y_values[index+1]) / 2)
                                * ((x_values[-1]-x_values[0]) / (len(x_values)-1)))
                    total_area_RHS = total_area_RHS + area_RHS

            # Calculates area ratio (= Bnet)
            ratio = total_area_RHS / total_area_LHS

            plt.annotate('Bnet = {:.1f}'.format(ratio),
                         xy=(max(x_values)*0.65, max(y_values)*0.9),
                         fontsize=10)
            plt.annotate('Median = {:.2f}'.format(median),
                         xy=(max(x_values)*0.65, max(y_values)*0.85),
                         fontsize=10)
            plt.savefig(str(self.pdb_file_path)+'_Bnet_NA.png')

            if not os.path.isfile('Logfiles/Bnet_NA.csv'):
                Bnet_list = open('Logfiles/Bnet_NA.csv', 'w')
                Bnet_list.write('PDB' + ',')
                Bnet_list.write('Bnet' + ',')
                Bnet_list.write('Window_size (%)' + ',')
                Bnet_list.write('PDT' + ',')
                Bnet_list.close()
            Bnet_list = open('Logfiles/Bnet_NA.csv', 'a')
            Bnet_list.write('\n%s' % self.pdb_code + ',')
            Bnet_list.write('%s' % ratio + ',')
            Bnet_list.write('%s' % window_name + ',')
            Bnet_list.write('%s' % pdt_name + ',')
            Bnet_list.close()