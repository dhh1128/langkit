from langkit.syllable import candidates

i = 0
for syl in candidates('aeiou', 'smphntk', None, 'CCCV'):
    print(f"{i} {syl}")
    i += 1

