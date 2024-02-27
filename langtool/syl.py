from phones import can_add_std

#vowels = ['a','e','i','o','u']
#consonants = ['f','v','k','g','m','n','p','b','s','z','ʃ','ʒ','t','d','l','w','x','tʃ','dʒ']


def _valid_next(pat_item, vowels, consonants, previous=None):
    if pat_item == 'C':
        collection = consonants
    elif pat_item == 'V':
        collection = vowels
    else:
        collection = [pat_item]
    if not previous:
        for item in collection:
            yield item
    else:
        for phoneme in collection:
            if can_add_std(previous, phoneme):
                yield phoneme

def _get_all_valid_remainders(pat, vowels, consonants, previous):
    remainder = pat[1:]
    if remainder:
        for prefix in _valid_next(pat[0], vowels, consonants, previous):
            for suffix in _get_all_valid_remainders(remainder, vowels, consonants, prefix):
                yield prefix + suffix
    else:
        for item in _valid_next(pat[0], vowels, consonants, previous):
            yield item

def valid_syllables(vowels, consonants, *patterns):
    for pat in patterns:
        for syllable in _get_all_valid_remainders(pat, vowels, consonants, None):
            yield syllable

n = 0
for item in valid_syllables('ai', 'smphn', 'V', 'CV', 'CVC', 'CCV', 'CCCV'):                    
    print(item)
    n += 1

print(f"\nn = {n}")

need to prevent a consonant from being reused without intervening vowel
need to allow a lang to declare combinations that it doesn't support (e.g., ps)


