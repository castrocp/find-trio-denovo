#!/usr/bin/env python

from __future__ import print_function
import sys

'''
Still have to look into the problem of not all entries being phased in the original VCF.
Could consider filtering out the unphased entried.  Otherwise figure out how to convert them to phased
'''

# find-trio-denovo <VCFfilename> <childID> <dadID> <momID>

################################ OPEN THE TAB-DELIMITED CONVERTED VCF FILE ####################################
#############################################################################################################
def main():
	inFileName = sys.argv[1] 
	childGeno  = sys.argv[2]
	dadGeno = sys.argv[3]
	momGeno = sys.argv[4]

#not sure how this will work, because the IDs might not always be in this order in the converted VCF file. 
#They just hapen to be for the practice vcf file.  Will have to be changed when the child's ID is in a 
#different column
	
	with open (inFileName,'r') as infile:  #when you use "with open" you don't have to close the file later
		next(infile) #Skips the header. Will need to go back to print header once though
		for line in infile:
			(chrom, pos, ref, childGeno, dadGeno, momGeno)= line.strip("\n").split("\t")
			
			#now split the genotypes by into individual alleles
			(childAllele1, childAllele2) = childGeno.split("/")      #will need to split on "|" also, for the unphased entries
			(dadAllele1, dadAllele2) = dadGeno.split("/")
			(momAllele1, momAllele2) = momGeno.split("/")

			#create two lists; one containing both child alleles, the other containing all parent alleles
			childAlleles = [childAllele1, childAllele2]
			parentAlleles = [dadAllele1, dadAllele2, momAllele1, momAllele2]
			
							 				
			print("test next line")  #This will print once for each line of the VCF the program goes through
			
			#want to check for each child allele in all parent alleles
			for i in xrange(0,2):   #will check for matches to childAllele1 and then childAllele2
									#xrange (0,2) looks at index 0, and then index 1. Doesn't include "2"
				found_in_dad = 0
				found_in_mom = 0

				for j in xrange(0,4):  #will check all parent alleles for a match; indices 0-3
					if childAlleles[i] == parentAlleles[j]:
						if j < 2: #parentAlleles[0] and parentAlleles[1] are dad's alleles. 2 and 3 are mom's
							found_in_dad = 1
						else:
							found_in_mom = 1  
				
				if found_in_dad == 0 and found_in_mom == 0: #if alleles not found in parents, found_in_dad/mom will = 0
					recordVariant(line)  #write the line to the output file
				else:
					print("it's in there somewhere") #eventually this should just be "do nothing"
				
				'''
				If it goes through all 4 parent alleles and doesn't find a match, denovo variant implied.
				Could exit loop and print variant line if the first child allele isn't found in parents 
				Wouldn't be a need to check second child allele
				'''

################################ CREATE FILE TO STORE DENOVO VARIANT INFO ####################################
#############################################################################################################

def recordVariant(line):
	file = open("denovoVariants.txt" , "w")
	file.write(line)
	file.close()


if __name__ == '__main__':
	main()