import csv
import pprint
from splitter import *
from colorama import *
import sys


init()

# Read in test address file
f = open(os.path.join('tests','test_suite.csv')
r = csv.reader(f)

column_names = [header.replace('\n', ' ') for header in r.next()]

print ("\nReading data from file:")

#check latest entries first
for row in reversed(list(r)):

    address = dict(zip(column_names, row))

    print Fore.WHITE + address['address'] + Fore.YELLOW

    a = Address(address['address'])

    parsed = a.get_best_variant()
    result = parsed['result']

    correct_parse = True
    for part, value in address.iteritems():

        if part in ['address', 'expected_fail']:
            continue
        if not result.get(part, '') == str(value):
            if address.get('expected_fail'):
                sys.stdout.write(Fore.YELLOW + Style.BRIGHT)
            else:
                sys.stdout.write(Fore.RED + Style.BRIGHT)
            print "expected " + part + ": '" + str(value) + "', got: '" + result.get(part, "<none>") + "'" + Fore.WHITE + Style.NORMAL
            correct_parse = False

    if not correct_parse:
        if address.get('expected_fail'):
            print Style.BRIGHT + Back.YELLOW + address['address'] + " -- expected fail**" + Fore.WHITE + Style.NORMAL + Back.BLACK
        else:
            print Fore.RED + Style.BRIGHT + address['address'] + " -- **fail**" + Fore.WHITE + Style.NORMAL
            #pprint.pprint (result)
            pprint.pprint(a.get_best_variant())
            pprint.pprint(a.get_costed_variants(True)[:10])
            # for  v in a.getVariants():
            #    for p in v['variant']:
            #        if p and p.getType().name() == 'location_qualifier':
            #            print p
            # print v['variant']
            break

    else:
        print Fore.GREEN + " pass!" + Fore.WHITE

    #
    #pprint.pprint( a.getVariants())
    # break
