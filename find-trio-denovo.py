#!/usr/bin/env python

from __future__ import print_function
import sys
import re
import csv
import time

#find-trio-denovo <VCFfilename> <first person> <second person> <third person> (type "dad" "mom" or "child")

#GO BACK AND ADD 2 ARGUMENTS THAT WILL ALLOW THE USER TO NAME THE 2 OUTPUT FILES

################################ OPEN THE VCF FILE ##########################################################
#############################################################################################################
def main():
	startTime = time.time()
	inFileName = sys.argv[1]
        momIdx = sys.argv.index("mom")
        dadIdx = sys.argv.index("dad")
        childIdx = sys.argv.index("child")

	variant_count = 0 #counts phased and unphased variants
	unphased_count = 0 #separate counter for variants with all lines treated as unphased

	with open (inFileName,'r') as infile:  #when you use "with open" you don't have to close the file later
		for line in infile:
			if line.startswith("#"):   # header and info lines start with "#"
				recordVariant(line)
				unphasedVariants(line)
			else:
                                (chrom, pos, ID, ref, alt, qual, Filter, info, format, samples) = line.strip("\n").split("\t", 9)
                                samples = samples.split("\t")
                                dadgeno = samples[dadIdx - 2]
                                momgeno = samples[momIdx - 2]
                                childgeno = samples[childIdx - 2]

				(dadAlleles, dadPhased) = extract_genes(dadgeno)
				(momAlleles, momPhased) = extract_genes(momgeno)
				(childAlleles, childPhased) = extract_genes(childgeno)

				# assumes that delimiter on dadGeno is same as momGeno and childGeno
                                if dadPhased != momPhased or dadPhased != childPhased:
                                    print("Family phasing doesn't match!")
                                    exit(1)

                                phased = dadPhased

                                child_in_dad = child_in_parent(childAlleles, dadAlleles)
                                child_in_mom = child_in_parent(childAlleles, momAlleles)

				#The following conditions were written when I was taking all 4 nucleotides into account
				#In a VCF, it will usually only be comparing a "0" (ref) or "1" (alt)
				#It still works, but might be more than what's necessary

				# Variant conditions if the data is phased
                                if phased:
                                        if not child_in_dad[0] or not child_in_mom[1]:
                                                recordVariant(line) # variant because neither child allele in parents
                                                variant_count +=1

                                        #Treat phased lines as unphased and record variants in second output file
                                        if ((not child_in_dad[0] and not child_in_mom[0]) # variant because child1 not in either parent
                                            (not child_in_dad[1] and not child_in_mom[1]) # variant because child2 not in either parent
                                            (not child_in_dad[0] and not child_in_dad[1]) # variant because neither child allele in dad
                                            (not child_in_mom[0] and not child_in_mom[1])): # variant because neither child allele in mom
                                                unphasedVariants(line)
                                                unphased_count +=1

                                # Variant conditions if the data is unphased
                                # each child allele can now come from either parent, so it's a variant only if it's not in either parent
                                # before, only checked first child allele against dad. now need to check against mom also.
                                else:
                                        if ((not child_in_dad[0] and not child_in_mom[0]) # variant because child1 not in either parent
                                            (not child_in_dad[1] and not child_in_mom[1]) # variant because child2 not in either parent
                                            (not child_in_dad[0] and not child_in_dad[1]) # variant because neither child allele in dad
                                            (not child_in_mom[0] and not child_in_mom[1])): # variant because neither child allele in mom
                                                recordVariant(line)
                                                unphasedVariants(line) # also write to second output file, where all lines are treated as unphased
                                                variant_count +=1
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

def unphasedVariants(line): #creates a separate output file that records variants
	file = open(sys.argv[1]+".variants.as.unphased" , "a")	#treating all lines as unphased
	file.write(line)
	file.close()

def extract_genes(unparsed_geno):
        # split the data by ":", to access only the genotype
        # first element of the list is the genotype when format is Genotype:Quality:ReadDepth:etc.
        geno = unparsed_geno.split(":")[0]

        # split the genotypes into individual alleles - split on "/" or "|"
        alleles = re.split(r"/|\|", geno)

        # checks which delimiter was used. | = phased vs / = unphased
        phased = geno.find("|") > -1

        return [alleles, phased]

def child_in_parent(childAlleles, parentAlleles):
        child_in_parent = []
        for idx, childAllele in enumerate(childAlleles):
            child_in_parent.insert(idx, childAllele in parentAlleles)

        return child_in_parent

if __name__ == '__main__':
	main()
