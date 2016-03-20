#!/usr/bin/env python

from __future__ import print_function
import sys
import re
import csv


#Still have to consider the problem of not all entries being phased in the original VCF.

#file input is tab-delimited file created with "vcf-to-tab" VCF tools program

#find-trio-denovo <VCFfilename> <childID> <dadID> <momID>

################################ OPEN THE TAB-DELIMITED CONVERTED VCF FILE ####################################
#############################################################################################################
def main():
	inFileName = sys.argv[1] 
	childGeno  = sys.argv[2]
	dadGeno = sys.argv[3]
	momGeno = sys.argv[4]

#not sure how this will work, because the IDs might not always be in this order in the converted VCF file. 
#They just hapen to be for the practice vcf file.  Will have to be changed if child and parent IDs are
#in a different order.
	
	with open (inFileName,'r') as infile:  #when you use "with open" you don't have to close the file later
		next(infile) #Skips the header. Will need to go back to print header once though
		for line in infile:
			(chrom, pos, ref, childGeno, dadGeno, momGeno)= line.strip("\n").split("\t")
			
			#now split the genotypes by into individual alleles
			(childAllele1, childAllele2) = re.split(r"/|\|",childGeno)  #will split on "/" or "|"
			(dadAllele1, dadAllele2) = re.split(r"/|\|",dadGeno)	    #to apply to both phased and unphased entries
			(momAllele1, momAllele2) = re.split(r"/|\|",momGeno)	   

			#checks which delimiter was used.  / = phased .   | = unphased
			#assumes that delimiters on dadGeno and momGeno are same as childGeno 
			dialect = csv.Sniffer().sniff(childGeno,["/","|"])
			delim = (dialect.delimiter)

			if delim == "/":
				print("phased")
			else:
				print("unphased")

			#create two lists; one containing both child alleles, the other containing all parent alleles
			childAlleles = [childAllele1, childAllele2]
			parentAlleles = [dadAllele1, dadAllele2, momAllele1, momAllele2]
						 				
			print("test next line")  #This will print once for each line of the VCF the program goes through
			
			child1_in_dad = 0   #first child allele found in either dad allele
			child2_in_dad = 0
			child1_in_mom = 0
			child2_in_mom = 0

			#want to check for each child allele in all parent alleles
			for i in range(0,2):   
				for j in range(0,4):  #will check all parent alleles for a match; indices 0-3
					if childAlleles[i] == parentAlleles[j]:
					#parentAlleles[0] and parentAlleles[1] are dad's 1st and 2nd alleles
					#parentAlleles[2] and parentAlleles[3] are mom's 1st and 2nd alleles
						
						#check child's first allele
						if i==0 and j==0: 
							child1_in_dad = 1
						elif i==0 and j==1:
							child1_in_dad = 1
						elif i==0 and j==2:
							child1_in_mom = 1
						elif i==0 and j==3:
							child1_in_mom = 1
 						
 						#check child's second allele
						elif i==1 and j==0: 
							child2_in_dad = 1
						elif i==1 and j==1:
							child2_in_dad = 1
						elif i==1 and j==2:
							child2_in_mom = 1
						elif i==1 and j==3:
							child2_in_mom = 1

						#child2 in dad and child1 in mom not being used at this point
						#should be useful when unphased data is incorporated though

			# only want to print/write once, so only consider one situation at a time with elif and or. Once any single variant
			# situation is true, print and exit to move to next line. For now I don't care which specific
			# variant situation I have; only whether it's a variant or not. 
	
			if child1_in_dad == 0 and child2_in_mom == 0:
				print("variant because neither child allele in parents")
			elif child1_in_dad == 0 or child2_in_mom == 0:	
				print("variant because one of the variants isn't in the correct parent")

			# incorporate unphased situations
			# each child allele can now come from either parent, so it's a variant only if it's not in either
			# before, only checked first child allele against dad. now need to check against mom also.
			elif child1_in_dad == 0 and child1_in_mom == 0:
				print("unphased variant")
			elif child2_in_mom == 0 and child2_in_dad == 0:
				print("unphased variant")

			
			 

				
			'''
			Might need to keep track of individual parent alleles when dealing with unphased
			data, but for now going to ignore this

			#child alleles not found in either parent (G/T   C/T   C/T)
			if in_child1_dad1 == 0 and in_child1_dad2 == 0 and in_child1_mom1 == 0 and in_child1_mom2 == 0:
				print("first child allele isn't found in either parent")
			if in_child2_dad1 == 0 and in_child2_dad2 == 0 and in_child2_mom1 == 0 and in_child2_mom2 == 0:
				print("second child allele isn't found in either parent")
			
			#child alleles both found only in dad  
				#ex. (A/G  A/G  T/T)
			if in_child1_dad1 == 1 and in_child1_dad2 == 0 and in_child1_mom1 == 0 and in_child1_mom2 == 0 and in_child2_dad1 == 0 and in_child2_dad2 == 1 and in_child2_mom1 == 0 and in_child2_mom2 == 0:
				print("both child alleles are only in dad")
			
			#child alleles both found only in mom 
				#ex. (A/A   G/G    A/A)
			if in_child1_dad1 == 0 and in_child1_dad2 == 0 and in_child1_mom1 == 1 and in_child1_mom2 == 1 and in_child2_dad1 == 0 and in_child2_dad2 == 0 and in_child2_mom1 == 1 and in_child2_mom2 == 1:
				print("both child alleles are only in mom")
				#ex. (A/T  G/G   A/T)
			if in_child1_dad1 == 0 and in_child1_dad2 == 0 and in_child1_mom1 == 1 and in_child1_mom2 == 0 and in_child2_dad1 == 0 and in_child2_dad2 == 0 and in_child2_mom1 == 0 and in_child2_mom2 == 1:
				print("both child alleles are only in mom")

			#so far this works, but too many options to go through. must be a more efficient way
			'''

################################ CREATE FILE TO STORE DENOVO VARIANT INFO ####################################
#############################################################################################################

def recordVariant(line):
	file = open("denovoVariants.txt" , "w")
	file.write(line)
	file.close()


if __name__ == '__main__':
	main()