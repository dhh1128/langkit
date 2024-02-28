from phonemizer import phonemize
from phonemizer.phonemize import phonemize_to_details

# List of IPA consonants
consonants = ['p', 'b', 't', 'd', 'k', 'g', 'm', 'n', 'ŋ', 'f', 'v', 'θ', 'ð', 's', 'z', 'ʃ', 'ʒ', 'h', 'tʃ', 'dʒ', 'r', 'j', 'w', 'l']

def dump():
    # Convert IPA symbols to phonetic features
    for consonant in consonants:
        phonetic_details = phonemize_to_details(consonant, lang="en")
        print(f"Consonant: {consonant}, Phonetic Features: {phonetic_details}")

if __name__ == '__main__':
    dump()