#!/usr/bin/env python

from __future__ import print_function
import sys

'''
Still have to look into the problem of not all entries being phased in the original VCF.
Could consider filtering out the unphased entried.  Otherwise figure out how to convert them to phased
'''

#file input is tab-delimited file created with "vcf-to-tab" VCF tools program

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
			(childAllele1, childAllele2) = childGeno.split("/")    #will need to split on "|" also,
			(dadAllele1, dadAllele2) = dadGeno.split("/")		   #when the code is applied to VCF containing
			(momAllele1, momAllele2) = momGeno.split("/")	       #both phased and unphased entries

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

				#EACH CHILD ALLELE MUST BE FOUND, SO THERE SHOULD BE SOME CONDITIONAL STATEMENT
				#INSIDE THE CHILD ALLELE FOR LOOP

				if found_in_dad == 0 and found_in_mom == 0: #if alleles not found in parents, found_in_dad/mom will = 0
					print("child allele not in mom or dad") #later, use the record_variant function here to write to output file instead
				#now it'll go back and check the child's second allele
				#if that second allele is also not in either, it will print variant line a 2nd time

			# went back and adjusted the indentation of the next if statements. If the following if 
			# statements are indented, they will be checked after only checking the first child allele.
			# Have them outside of the for loop allows both child alleles to be compared before
			# looking at found_in_dad/mom

			#situation where child allele is not found in either parent
			#if found_in_dad == 0 and found_in_mom == 0: 
				#print(line)  
			#this doesn't work because if only one of the child's alleles is found in both parents, both
			#will = 1, but it should still be a variant need to modify to make sure EACH child allele matches something
				
			#situation where both child alleles come from the dad or both from mom	
			if found_in_dad == 1 and found_in_mom == 0: #child alleles only found in dad, none in mom
				print("no child alleles in mom")  #later, use the record_variant function here to write to output file instead
			elif found_in_dad == 0 and found_in_mom == 1: #child alleles only found in mom, none in dad
				print("no child alleles in dad")
			else:
				print("no variant found") #eventually this should just be "do nothing"
				
	
################################ CREATE FILE TO STORE DENOVO VARIANT INFO ####################################
#############################################################################################################

def recordVariant(line):
	file = open("denovoVariants.txt" , "w")
	file.write(line)
	file.close()


if __name__ == '__main__':
	main()