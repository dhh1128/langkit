import epitran

# Create an instance of the English Epitran object
epi = epitran.Epitran('fra-Latn')

# List of IPA consonants
consonants = ['p', 'b', 't', 'd', 'k', 'g', 'm', 'n', 'ŋ', 'f', 'v', 'θ', 'ð', 's', 'z', 'ʃ', 'ʒ', 'h', 'tʃ', 'dʒ', 'r', 'j', 'w', 'l']

# Get phonetic features of IPA consonants
def dump():
    for consonant in consonants:
        phonemes = epi.transliterate(consonant)
        print(f"Consonant: {consonant}, Phonetic Features: {phonemes}")

if __name__ == '__main__':
    dump()