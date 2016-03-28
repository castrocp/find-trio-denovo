#!/usr/bin/env python

from __future__ import print_function
import sys
import re
import csv
import time

#find-trio-denovo <VCFfilename> <first person> <second person> <third person> (type "dad" "mom" or "child")

################################ OPEN THE VCF FILE ##########################################################
#############################################################################################################
def main():
	startTime = time.time()
	inFileName = sys.argv[1] 
	firstCol = sys.argv[2]   # user inputs the order of the parent and child columns
	secondCol = sys.argv[3]  # so that the program knows which is being read
	thirdCol = sys.argv[4]

	variant_count = 0 #counts phased and unphased variants
	unphased_count = 0 #separate counter for variants with all lines treated as unphased

	with open (inFileName,'r') as infile:  #when you use "with open" you don't have to close the file later
		for line in infile:
			if line.startswith("#"):   # header and info lines start with "#"
				recordVariant(line)   
				unphasedVariants(line)
			else:  
				if firstCol == "dad" and secondCol == "mom":
					(chrom, pos, ID, ref, alt, qual, Filter, info, format, dadgeno, momgeno, childgeno)= line.strip("\n").split("\t")
				elif firstCol == "dad" and secondCol == "child":
					(chrom, pos, ID, ref, alt, qual, Filter, info, format, dadgeno, childgeno, momgeno)= line.strip("\n").split("\t")
				elif firstCol == "mom" and secondCol =="dad":
					(chrom, pos, ID, ref, alt, qual, Filter, info, format, momgeno, dadgeno, childgeno)= line.strip("\n").split("\t")
				elif firstCol == "mom" and secondCol == "child":
					(chrom, pos, ID, ref, alt, qual, Filter, info, format, momgeno, childgeno, dadgeno)= line.strip("\n").split("\t")
				elif firstCol == "child" and secondCol == "dad":
					(chrom, pos, ID, ref, alt, qual, Filter, info, format, childgeno, dadgeno, momgeno)= line.strip("\n").split("\t")
				elif firstCol ==  "child" and secondCol == "mom":
					(chrom, pos, ID, ref, alt, qual, Filter, info, format, childgeno, momgeno, dadgeno)= line.strip("\n").split("\t")

				# split each of the dad/mom/child columns by ":", to access only the genotype
				# first element of the list is the genotype when format is Genotype:Quality:ReadDepth:etc.
				dadgeno_list = dadgeno.split(":")
				dadGeno = (dadgeno_list[0])
				
				momgeno_list = momgeno.split(":")
				momGeno = (momgeno_list[0])
				
				childgeno_list = childgeno.split(":")
				childGeno = (childgeno_list[0])
				
				#now split the genotypes into individual alleles
				#will split on "/" or "|"
				(dadAllele1, dadAllele2) = re.split(r"/|\|",dadGeno)	    #to apply to both phased 
				(momAllele1, momAllele2) = re.split(r"/|\|",momGeno)	    #and unphased entries
				(childAllele1, childAllele2) = re.split(r"/|\|",childGeno)

				#checks which delimiter was used.  | = phased .   / = unphased
				#assumes that delimiter on dadGeno is same as momGeno and childGeno 
				dialect = csv.Sniffer().sniff(dadGeno,["/","|"])
				delim = (dialect.delimiter)

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
						recordVariant(line) # variant because neither child allele in parents
						variant_count +=1
					elif child1_in_dad == 0 or child2_in_mom == 0:	
						recordVariant(line) #variant because one parent didn't contribute an allele
						variant_count +=1
					
				# Variant conditions if the data is unphased
				# each child allele can now come from either parent, so it's a variant only if it's not in either parent
				# before, only checked first child allele against dad. now need to check against mom also.
					
				elif delim == "/":   #can just be "else"  Wrote it out to make it clear for now
					if child1_in_dad == 0 and child1_in_mom == 0:
						recordVariant(line) #variant because child1 not in either parent
						unphasedVariants(line) #also write to second output file, where all lines are treated as unphased
						variant_count +=1
						unphased_count +=1
					elif child2_in_mom == 0 and child2_in_dad == 0:
						recordVariant(line) #variant because child2 not in either parent
						unphasedVariants(line)
						variant_count +=1
						unphased_count +=1
					elif child1_in_dad == 0 and child2_in_dad ==0:
						recordVariant(line) #variant because neither child allele in dad
						unphasedVariants(line)
						variant_count +=1
						unphased_count +=1
					elif child1_in_mom == 0 and child2_in_mom ==0:
						recordVariant(line) #variant because neither child allele in mom
						unphasedVariants(line)
						variant_count +=1
						unphased_count +=1
				
				#Treat phased lines as unphased and record variants in second output file
				if delim == "|":   
					if child1_in_dad == 0 and child1_in_mom == 0:
						unphasedVariants(line) 
						unphased_count +=1
					elif child2_in_mom == 0 and child2_in_dad == 0:
						unphasedVariants(line)
						unphased_count +=1
					elif child1_in_dad == 0 and child2_in_dad ==0:
						unphasedVariants(line)
						unphased_count +=1
					elif child1_in_mom == 0 and child2_in_mom ==0:
						unphasedVariants(line)
						unphased_count +=1

	recordVariant("\n")			
	recordVariant('The script took {0} minutes'.format( (time.time() - startTime)/60 ) )
	recordVariant("\n")
	recordVariant(str(variant_count) + " phased and unphased variants were found")

	unphasedVariants("\n")	
	unphasedVariants('The script took {0} minutes'.format( (time.time() - startTime)/60 ) )
	unphasedVariants("\n")
	unphasedVariants(str(unphased_count) + " variants were found when all lines were treated as unphased")

################################ CREATE FILE TO STORE DENOVO VARIANT INFO ####################################
#############################################################################################################

def recordVariant(line): 
	file = open(sys.argv[1]+".variants" , "a") #open output file in "append" mode
	file.write(line) 						   #includes both phased and unphased variants
	file.close()

def unphasedVariants(line): 			    				#creates a separate output file that records variants 
	file = open(sys.argv[1]+".variants.as.unphased" , "a")	#treating all lines as unphased
	file.write(line)
	file.close()

if __name__ == '__main__':
	main()