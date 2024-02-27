inventory = {
    'ɑ': 'open back vowel', # back sound made while gargling
    'ɒ': 'open back rounded vowel', # the vowel emphasized in SNL's "coffee talk" skits
    'a': 'open central vowel', # spanish a, farther forward sound than 2 previous
    'e': 'close-mid near-front vowel', # spanish e
    'i': 'close front vowel', ## ee in english green
    'ɪ': 'near-close near-front vowel', # i in english spin
    'o': 'close-mid back rounded vowel', # spanish o, not english sound that ends in [u]
    'æ': 'near-open near-front vowel', # a in english "cat"
    'u': 'close back rounded vowel', # oo in english "scoop"
    'ʊ': 'near-close near-back vowel', # oo in english "good"
    'ə': 'mid central vowel', # schwa
    'f': 'labiodental fricative',
    'v': 'voiced labiodental fricative',
    'k': 'velar plosive',
    'g': 'voiced velar plosive',
    'j': 'voiced palatal transition', # y in english yell
    'm': 'voiced bilabial nasal',
    'n': 'voiced alveolar nasal',
    'ɲ': 'voiced palatal nasal', # spanish ñ
    'p': 'bilabial plosive',
    'b': 'voiced bilabial plosive',
    's': 'alveolar fricative',
    'z': 'voiced alveolar fricative',
    'ʃ': 'palato-alveolar fricative', #sh in english ship
    'ʒ': 'voiced palato-alveolar fricative', # si in english "vision"
    'θ': 'dental fricative', # th in english "thing"
    'ð': 'voiced dental fricative', # th in english "that"
    't': 'alveolar plosive',
    'd': 'voiced alveolar plosive',
    'l': 'voiced alveo-lateral approximant',
    'w': 'voiced labial-velar transition',
    'ʔ': 'glottal plosive',
    'h': 'glottal transition',
    'x': 'velar fricative',
    'ɹ': 'voiced alveolar approximant', # r in english "car"
    'ɾ': 'voiced alveolar flap', # r in spanish "pero"
    'tʃ': 'postalveolar affricate', # ch in english "chair" 
    'dʒ': 'voiced postalveolar affricate', # dg in english "judge" 
}


def is_rounded(attribs):
    if is_vowel(attribs):
        return "rounded" in attribs
    
def is_vowel(attribs):
    return "vowel" in attribs

def get_x(attribs):
    if is_vowel(attribs):
        return 

def is_voiced(attribs):
    if not is_vowel(attribs):
        return "voiced" in attribs

def is_consonant(attribs):
    return not is_vowel(attribs)

def get_place(attribs):
    if is_vowel(attribs):
        return attribs.replace(' rounded', '').replace(' vowel', '')
    else:
        return attribs[:attribs.rfind(' ')].replace('voiced ', '')

def get_manner(attribs):
    if not is_vowel(attribs):
        return attribs[attribs.rfind(' ') + 1:]

def can_add_std(a, b):
    """
    Tell whether b can be added to a in the same syllable. Different languages
    have different combining rules. This function simply imposes a common set
    of choices that are likely to be true across many languages, eliminating
    the most common nonsensical combinations of sounds.
    """
    a_attrib = inventory[a]
    b_attrib = inventory[b]
    # Long or doubled versions of sounds are not possible
    if a_attrib == b_attrib:
        return False
    vowel_a = is_vowel(a_attrib)
    vowel_b = is_vowel(b_attrib)
    if vowel_a != vowel_b:
        # vowel + consonant and consonant + vowel are generally
        # valid, unless the consonant is second and it is a
        # transition (meaning it must move into a vowel rather
        # than the other way around)
        return 'transition' not in b_attrib
    place_a = get_place(a_attrib)
    place_b = get_place(b_attrib)
    if vowel_a: # We're evaluating possible diphthongs.
        # Diphthongs are high-effort sounds, but a schwa is the ultimate
        # relaxed sound. Doesn't make sense to combine it with something
        # that destroys that relaxation.
        if a == 'ə' or b == 'ə':
            return False
        approx_place_a = place_a.replace("near-", "")
        approx_place_b = place_b.replace("near-", "")
        # Differences only in rounding, or only slightly in
        # height or front/back are not allowed.
        if approx_place_a == approx_place_b:
            return False
        # When the mouth is fairly open, differences front-to-back
        # are not significant enough to justify a diphthong.
        if "open" in approx_place_a and "open" in approx_place_b:
            return False
        return True
    # Two consonants are trickier...
    # Two consonants with different voicing are not allowed
    if is_voiced(a_attrib) != is_voiced(b_attrib):
        return False
    # Glottal consonants can't be second.
    if place_b == 'glottal':
        return False
    # Glottal stop can only be followed by a vowel.
    if a == 'ʔ':
        return False
    manner_a = get_manner(a_attrib)
    # Transitions and flaps can't be followed by a consonant.
    if manner_a in ['transition', 'flap']:
        return False
    manner_b = get_manner(b_attrib)
    # Two consonants with the same manner of articulation are not allowed (pt, gd, ssh, chj)
    # except alveolar + labiodental (vz or fs)
    if manner_a == manner_b:
        x = ' '.join(sorted([place_a, place_b]))
        return x == "alveolar labiodental"
    if ' '.join(sorted([manner_a, manner_b])) == 'affricate fricative':
        return False
    return True
            
if __name__ == '__main__':
    n = 0
    keys = sorted(inventory.keys())
    for k in keys:
        for kk in keys:
            x = can_add_std(k, kk)
            if x:
                n += 1
                print(f"{k}{kk}")
    print(n)
            

    

