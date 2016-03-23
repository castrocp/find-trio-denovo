#!/usr/bin/env python

from __future__ import print_function
import sys
import re
import csv
import time

#file input is tab-delimited file created with "vcf-to-tab" VCF tools program

#find-trio-denovo <VCFfilename> <childID> <dadID> <momID>

################################ OPEN THE TAB-DELIMITED CONVERTED VCF FILE ####################################
#############################################################################################################
def main():
	startTime = time.time()
	inFileName = sys.argv[1] 
	#dadGeno = sys.argv[2]   #not sure why I originally wrote this.  Arguments don't seem to be necessary.
	#momGeno= sys.argv[3]
	#childGeno= sys.argv[4]

	variant_count = 0
	with open (inFileName,'r') as infile:  #when you use "with open" you don't have to close the file later
		for line in infile:
			if line.startswith("#"):   # header and info lines start with "#"
				print(line.strip("\n"))   #later, instead of printing, write to file
			else:
				(chrom, pos, ID, ref, alt, qual, Filter, info, format, dadgeno, momgeno, childgeno)= line.strip("\n").split("\t")
				#FIND OUT IF TRIO VCF FILES ALWAYS HAVE DAD/MOM/CHILD IN THAT ORDER.  

				# practice data is in format Genotype:Quality:ReadDepth
				# This won't necessarily be the same format for all VCF files though
				#create array of X length, and just refer to first element of array

				# split each of the dad/mom/child columns by ":", to access only the genotype
				(dadGeno, dadQual, dadDepth) = dadgeno.split(":")
				(momGeno, momQual, childDepth) = momgeno.split(":")
				(childGeno, childQual, childDepth) = childgeno.split(":")

				#now split the genotypes into individual alleles
				#will split on "/" or "|"
				(dadAllele1, dadAllele2) = re.split(r"/|\|",dadGeno)	    #to apply to both phased 
				(momAllele1, momAllele2) = re.split(r"/|\|",momGeno)	    #and unphased entries
				(childAllele1, childAllele2) = re.split(r"/|\|",childGeno)

				#checks which delimiter was used.  | = phased .   / = unphased
				#assumes that delimiter on dadGeno is same as momGeno and childGeno 
				dialect = csv.Sniffer().sniff(dadGeno,["/","|"])
				delim = (dialect.delimiter)

				'''
				if delim == "|":   #testing
					print("this line is phased")
				else:
					print("this line is unphased")
				'''

				#create two lists; one containing both child alleles, the other containing all parent alleles
				childAlleles = [childAllele1, childAllele2]
				parentAlleles = [dadAllele1, dadAllele2, momAllele1, momAllele2]
				
				child1_in_dad = 0   #to track whether alleles match or not
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

				#The following conditions were written when I was taking all 4 nucleotides into account
				#In a VCF, it will usually only be comparing a "0" (ref) or "1" (alt)
				#It still works, but might be more than what's necessary

				# Variant conditions if the data is phased
				if delim == "|":
					if child1_in_dad == 0 and child2_in_mom == 0:
						print(line) # variant because neither child allele in parents
						variant_count +=1
					elif child1_in_dad == 0 or child2_in_mom == 0:	
						print(line) #variant because one parent didn't contribute an allele
						variant_count +=1
					
				# Variant conditions if the data is unphased
				# each child allele can now come from either parent, so it's a variant only if it's not in either parent
				# before, only checked first child allele against dad. now need to check against mom also.
					
				elif delim == "/":   #can just be "else"  Wrote it out to make it clear for now
					if child1_in_dad == 0 and child1_in_mom == 0:
						print(line) #variant because child1 not in either parent
						variant_count +=1
					elif child2_in_mom == 0 and child2_in_dad == 0:
						print(line) #variant because child2 not in either parent
						variant_count +=1
					elif child1_in_dad == 0 and child2_in_dad ==0:
						print(line) #variant because neither child allele in dad
						variant_count +=1
					elif child1_in_mom == 0 and child2_in_mom ==0:
						print(line) #variant because neither child allele in mom
						variant_count +=1
				
	print()
	print('The script took {0} minutes'.format( (time.time() - startTime)/60 ) )
	print(str(variant_count) + " variants were found")

################################ CREATE FILE TO STORE DENOVO VARIANT INFO ####################################
#############################################################################################################

def recordVariant(line):
	file = open("denovoVariants.txt" , "w")
	file.write(line)
	file.close()


if __name__ == '__main__':
	main()