#!/usr/bin/env python

from __future__ import print_function
import sys
import re
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

	with open (inFileName, 'r') as infile:  #when you use "with open" you don't have to close the file later
            with open (inFileName + ".variants", "w") as variantFile:
                with open (inFileName + ".variants.as.unphased", "w") as unphasedFile:
                    for line in infile:
                            if line.startswith("#"):   # header and info lines start with "#"
                                    variantFile.write(line)
                                    unphasedFile.write(line)
                            else:
                                    (is_variant, is_unphased) = process_line(line, dadIdx-2, momIdx-2, childIdx-2, variant_count, unphased_count)
                                    if is_variant:
                                        variant_count += 1
                                        variantFile.write(line)

                                    if is_unphased:
                                        unphased_count += 1
                                        unphasedFile.write(line)

                    completion_msg = "\nThe script took {0} minutes\n".format((time.time() - startTime/60))

                    variantFile.write(completion_msg)
                    variantFile.write("{0} phased and unphased variants were found".format(variant_count))

                    unphasedFile.write(completion_msg)
                    unphasedFile.write("{0} variants were found when all lines were treated as unphased".format(unphased_count))

################################ CREATE FILE TO STORE DENOVO VARIANT INFO ####################################
#############################################################################################################

def process_line(line, dadIdx, momIdx, childIdx, variant_count, unphased_count):
        is_unphased = False
        is_variant = False

        (chrom, pos, ID, ref, alt, qual, Filter, info, format, samples) = line.strip("\n").split("\t", 9)
        samples = samples.split("\t")
        dadgeno = samples[dadIdx]
        momgeno = samples[momIdx]
        childgeno = samples[childIdx]

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

        #Treat all lines as unphased and record variants in second output file
        if ((not child_in_dad[0] and not child_in_mom[0]) or # variant because child1 not in either parent
            (not child_in_dad[1] and not child_in_mom[1]) or # variant because child2 not in either parent
            (not child_in_dad[0] and not child_in_dad[1]) or # variant because neither child allele in dad
            (not child_in_mom[0] and not child_in_mom[1])): # variant because neither child allele in mom
                is_unphased = True

                # Variant conditions if the data is unphased
                is_variant = not phased

        # Variant conditions if the data is phased
        if (phased and (not child_in_dad[0] or not child_in_mom[1])):
                is_variant = True

        return (is_variant, is_unphased)

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
