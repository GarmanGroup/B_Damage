# RABDAM – identifying specific radiation damage in MX structures
A program to calculate the *B*<sub>Damage</sub> and *B*<sub>net</sub> metrics to quantify the extent of specific radiation damage present within an individual MX structure. Suitable for running on any standard format PDB file.

\*\***NOTE:** These scripts are under development, and are updated regularly. The program is currently being extended to incorporate nucleic acids analysis. Whilst these new capabilities are being tested, it is strongly recommended that presently RABDAM is only used to assess damage to protein crystal structures.\*\*


## Contents
-	[How to run in brief](#how-to-run-in-brief)
- [Background](#background)
-	[Usage](#usage)
    -	[System requirements](#system-requirements)
    - [Data requirements](#data-requirements)
    -	[Running RABDAM](#running-rabdam)
    -	[Writing the RABDAM input file](#writing-the-rabdam-input-file)
- [An example RABDAM run](#an-example-rabdam-run)
-	[Queries](#queries)
-	[Contributors](#contributors)
-	[Citing RABDAM](#citing-rabdam)

## How to run in brief
RABDAM is a command line program. To run the program with its recommended default parameter values, execute:

`python rabdam.py –f XXXX`

, where XXXX is the 4 character PDB accession code of the MX structure under study. Alternatively, you can provide RABDAM with a file path to a locally saved PDB file:

`python rabdam.py –f path/to/pdb_file.pdb`

See the “*Usage*” section below for further details.

## Background
During macromolecular crystallography (MX) data collection, X-rays are also absorbed by and deposit energy within the crystal under study, causing damage. This damage can result in localised chemical changes to the crystalline macromolecule copies, for example to disulfide bond cleavage in proteins, *etc*. Such *specific radiation damage* manifestations can lead to incorrect biological conclusions being drawn from an MX structure if they are not identified and accounted for. Unfortunately, the high intensities of third generation synchrotron sources have resulted in specific radiation damage artefacts commonly being present in MX structures deposited in the Protein Data Bank (PDB) even at 100 K.

The chemical changes induced by specific radiation damage cause an accompanying increase in the atomic *B*<sub>factor</sub> values of affected sites. Multiple factors can affect an atom’s *B*<sub>factor</sub> value in addition to radiation damage however, the most important of these being its mobility. The increase in *B*<sub>factor</sub> caused by specific radiation damage is insufficiently large to distinguish damage from mobility.

There is a strong positive correlation between the mobility of an atom within a crystal structure and its packing density, *i.e.* the number of atoms present in its local environment. The *B*<sub>Damage</sub> metric is *B*<sub>factor</sub> corrected for packing density: specifically, the *B*<sub>Damage</sub> value of an atom *j* is equal to the ratio of its *B*<sub>factor</sub> to the average *B*<sub>factor</sub> of atoms 1 to *n* which occupy a similar packing density environment to atom *j*. The *B*<sub>Damage</sub> metric has been shown to identify expected sites of specific radiation damage in damaged MX structures (Gerstel *et al.*, 2015).

![Images/BDamage_equation.png](Images/BDamage_equation.png)

The method of calculating an atom’s *B*<sub>Damage</sub> value is summarised in the diagram below:

___

![Images/BDamage_methodology.png](Images/BDamage_methodology.png)
Calculation of the *B*<sub>Damage</sub> metric. From an input PDB file of the asymmetric unit of a macromolecule of interest, RABDAM **(A)** generates a copy of the unit cell, followed by **(B)** a 3x3x3 assembly of unit cells. **(C)** Atoms in the 3x3x3 unit cell assembly that lie further than 14 Å from the asymmetric unit are discounted. **(D)** The packing density of an atom *j* in the asymmetric unit is calculated as the number of atoms within a 14 Å radius. **(E)** Asymmetric unit atoms are ordered by packing density; the *B*<sub>Damage</sub> value of atom *j* is then calculated as the ratio of its *B*<sub>factor</sub> to the average of the *B*<sub>factor</sub> values of atoms grouped, via sliding window, as occupying a similar packing density environment. Note that hydrogen atoms are not considered in the calculation of *B*<sub>Damage</sub>.

___

The *B*<sub>net</sub> metric is a derivative of the (per-atom) *B*<sub>Damage</sub> metric that summarises in a single value the overall extent of specific radiation damage suffered by an MX structure. One of the best-characterised chemical changes resulting from specific radiation damage that occurs within proteins\* is the decarboxylation of Glu and Asp residues; the *B*<sub>net</sub> metric is calculated from a kernel density plot of the *B*<sub>Damage</sub> values of a structure’s Glu and Asp terminal oxygen atoms as the ratio of the area under the curve either side of the median of the (overall) *B*<sub>Damage</sub> distribution.

(\* An equivalent of this protein-specific *B*<sub>net</sub> metric for nucleic acids is currently being developed - see program description.)

The method of calculating the *B*<sub>net</sub> value for a protein structure is summarised in the diagram below:

___

![Images/Bnet_calculation.png](Images/Bnet_calculation.png)
The *B*<sub>net</sub> metric is calculated as the ratio of the area either side of the median (of the overall *B*<sub>Damage</sub> distribution) underneath a kernel density estimate of the *B*<sub>Damage</sub> values of the terminal oxygen atoms of Glu and Asp residues.

___

RABDAM calculates the values of the *B*<sub>Damage</sub> and *B*<sub>net</sub> metrics for a standard format PDB file, as detailed in the following sections.

## Usage
#### System requirements
RABDAM is written in Python 2.7. In addition, it is dependent upon the following packages / programs that are not included in the [Anaconda Python 2.7 distribution](https://www.continuum.io/downloads):

-	The [seaborn](https://seaborn.pydata.org/) Python plotting library (version 0.7.1 or later)
-	The [CCP4 software suite](http://www.ccp4.ac.uk/) (RABDAM has a dependency on the CCP4 suite program PDBCUR)

To check whether your computer is missing any of the packages / programs required to run RABDAM, execute:

`python rabdam.py --dependencies`

\*\***NOTE:** Owing to its PDBCUR dependence, RABDAM can only be run in a terminal / command prompt in which CCP4 programs can also be run (*e.g.* the CCP4 console).\*\*

RABDAM will take approximately 2 minutes to run a 200 kDa structure on a single processor (as estimated from tests performed under Windows 7 on a 3.70 GHz Intel i3-4170 processor).

___

#### Data requirements
RABDAM can be run on any standard format PDB file of a single model of your MX structure of interest (specifically, it requires the CRYST1 line from the header information, as well as the ATOM / HETATM records). Note however that because *B*<sub>Damage</sub> is a per-atom metric, it should only be calculated for structures for which *B*<sub>factor</sub> values have been refined per-atom. Furthermore, owing to the correlation between *B*<sub>factor</sub> and occupancy, the only main-chain (*i.e.* non-ligand) atoms subject to occupancy refinement should be those in alternate conformers (whose occupancy should sum to 1).

____

#### Running RABDAM
RABDAM is a command line program. There are four main command line flags that control the program run:

-	`-i` / `--input`
-	`-f` / `--pdb_file`
-	`-r` / `--run`
-	`-o` / `--output`

The `-i` and `-f` flags control the input to the program. One of these two mutually exclusive flags is required for RABDAM to run.

The `-i` flag is used to specify the name of the input txt file listing your selected program parameter values (see the "*Constructing an input file*"’ section below for details of what this input file should include). If the input file is located in the same directory as the rabdam.py script, you only need provide the file name to run RABDAM:

`python rabdam.py -i input_file.txt`

Otherwise however you will need to provide its full file path:

`python rabdam.py -i path/to/input_file.txt`

Alternatively, if you wish to perform a run of RABDAM using entirely default parameter values, it is possible to run RABDAM without an input file; in this case the `-f` flag is used to provide RABDAM with either a 4 character PDB accession code (XXXX), or a file path (path/to/pdb_file.pdb), of the MX structure to be analysed:

`python rabdam.py -f XXXX` / `python rabdam.py -f path/to/pdb_file.pdb`

The `-r` and `-o` flags control the output from the program. Both of these flags are optional.

The `-r` flag can be used to instruct RABDAM to run to completion (default), or to stop / start part way through its full run. RABDAM is structured such that it writes the *B*<sub>Damage</sub> values calculated for an input MX structure to a DataFrame; this DataFrame is then used to write the program output files. Through use of the `-r` flag it is possible to instruct RABDAM to stop (`-r df` / `-r dataframe`), or start (`-r analysis`), its run following DataFrame construction. This option will save time if for example you wish to change the formatting of the program output files (see the “*Constructing an input file*” section below) without changing the *B*<sub>Damage</sub> distribution itself.

The `-o` flag can be used to control the selection of output files that the program writes. By default RABDAM writes 4 output files:

- `kde` : a kernel density estimate of the distribution of *B*<sub>Damage</sub> values calculated for the input MX structure
- `pdb` : a PDB file in which the *B*<sub>factor</sub> column of the ATOM / HETATM records is replaced by *B*<sub>Damage</sub> values
- `csv` : a csv file listing the properties (both those in the input PDB file and those calculated by RABDAM) of all atoms in the input MX structure included in the *B*<sub>Damage</sub> analysis
- `bnet` : a kernel density estimate of the *B*<sub>Damage</sub> values of the terminal oxygen atoms of Glu and Asp residues, plus the value of the (protein-specific) *B*<sub>net</sub> value calculated from this distribution (see the “*Background*” section)

It is possible to control which of these output files RABDAM writes using the `-o` flag plus the keyword names of the output files (highlighted in the list above) in any order. For example, to obtain the csv and *B*<sub>net<sub> output files, execute:

`python rabdam.py –o csv bnet`

You can also instruct RABDAM to write an html file summarising the program output (in addition to the 4 output files described above) using the `summary` keyword:

`python rabdam.py -o summary`

In addition, there are two supplementary command line flags:

- `-h` / `--help`
- `--dependencies`

The `-h` flag displays a help message in the terminal / command prompt listing the different command line flags that can / must be specified when running RABDAM. The `--dependencies` flag directs the program to test whether the system it is being run on has the necessary Python packages / programs installed for RABDAM to run to completion.

___

#### Writing the RABDAM input file
See example_input.txt for the basic structuring.

___

## An example RABDAM run

## Queries
Please email kathryn.shelley@queens.ox.ac.uk.

## Contributors
- Kathryn Shelley
- Tom Dixon
- Jonny Brooks-Bartlett

## Citing RABDAM
The initial development and testing of the *B*<sub>Damage</sub> metric is described in:

- Gerstel M, Deane CM, Garman EF (2015) Identifying and quantifying radiation damage at the atomic level. *J Synchrotron Radiat* **22**: 201-212. [http://dx.doi.org/doi:10.1107/S1600577515002131](http://dx.doi.org/doi:10.1107/S1600577515002131)

Please cite this paper if you use RABDAM to analyse specific radiation damage in your MX structure.

RABDAM is dependent upon the CCP4 suite program PDBCUR:

- Winn MD, Ballard CC, Cowtan KD, Dodson EJ, Emsley P, Evans PR, Keegan RM, Krissinel EB, Leslie AGW, McCoy A, McNicholas SJ, Murshudov GN, Pannu NS, Potterton EA, Powell HR, Read RJ, Vagin A, Wilson KS (2011) Overview of the CCP4 suite and current developments. *Acta Crystallogr Sect D Biol Crystallogr* **67**: 235-242.
