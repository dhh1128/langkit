
def _is_rounded_a(attribs):
    if _is_vowel_a(attribs):
        return "rounded" in attribs
    
def is_rounded(phoneme):
    return _is_rounded_a(COMMON_IPA.get(phoneme))
    
def _is_vowel_a(attribs):
    return "vowel" in attribs

def is_vowel(phoneme):
    attribs = COMMON_IPA.get(phoneme)
    if attribs:
        return _is_vowel_a(attribs)

def _is_voiced_a(attribs):
    if not _is_vowel_a(attribs):
        return "voiced" in attribs
    
def is_voiced(phoneme):
    return _is_voiced_a(COMMON_IPA.get(phoneme))

def _is_interrupted_a(attribs):
    return 'plosive' in attribs or 'flap' in attribs

def is_interrupted(phoneme):
    attribs = COMMON_IPA.get(phoneme)
    if attribs:
        return _is_interrupted_a(attribs)

def _is_nasal_a(attribs):
    return 'nasal' in attribs

def is_nasal(phoneme):
    attribs = COMMON_IPA.get(phoneme)
    if attribs:
        return _is_nasal_a(attribs)

def _is_consonant_a(attribs):
    return "vowel" not in attribs

def is_consonant(phoneme):
    attribs = COMMON_IPA.get(phoneme)
    if attribs:
        return _is_consonant_a(attribs)

def _get_place_a(attribs):
    if _is_vowel_a(attribs):
        return attribs.replace(' rounded', '').replace(' vowel', '')
    else:
        return attribs[:attribs.rfind(' ')].replace('voiced ', '')
    
def get_place(phoneme):
    return _get_place_a(COMMON_IPA.get(phoneme))

def _get_manner_a(attribs):
    if not _is_vowel_a(attribs):
        return attribs[attribs.rfind(' ') + 1:]
    
def get_manner(phoneme):
    return _get_manner_a(COMMON_IPA.get(phoneme))

def can_add_std(growing_syllable, next):
    """
    Tell whether next sound can be added to growing_syllable. Different languages
    have different combining rules. This function simply imposes a common set
    of choices that are likely to be true across many languages, eliminating
    the most common nonsensical combinations of sounds.
    """
    prev = growing_syllable[-1]
    a_attrib = COMMON_IPA[prev]
    b_attrib = COMMON_IPA[next]
    # Long or doubled versions of sounds are not possible
    if a_attrib == b_attrib:
        return False
    vowel_a = _is_vowel_a(a_attrib)
    vowel_b = _is_vowel_a(b_attrib)
    if vowel_a != vowel_b:
        # vowel + consonant and consonant + vowel are generally
        # valid, unless the consonant is second and it is a
        # transition (meaning it must move into a vowel rather
        # than the other way around)
        return 'transition' not in b_attrib
    place_a = _get_place_a(a_attrib)
    place_b = _get_place_a(b_attrib)
    if vowel_a: # We're evaluating possible diphthongs.
        # Diphthongs are high-effort sounds, but a schwa is the ultimate
        # relaxed sound. Doesn't make sense to combine it with something
        # that destroys that relaxation.
        if prev == 'ə' or next == 'ə':
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
    # Voiced followed by unvoiced is not allowed
    if _is_voiced_a(a_attrib):
        if not _is_voiced_a(b_attrib):
            return False
    # Glottal consonants can't be second.
    if place_b == 'glottal':
        return False
    # Glottal stop can only be followed by a vowel.
    if prev == 'ʔ':
        return False
    manner_a = _get_manner_a(a_attrib)
    # Transitions and flaps can't be followed by a consonant.
    if manner_a in ['transition', 'flap']:
        return False
    manner_b = _get_manner_a(b_attrib)
    # Two consonants with the same manner of articulation are not allowed (pt, gd, ssh, chj)
    # except alveolar + labiodental (vz, fs)
    if manner_a == manner_b:
        x = ' '.join(sorted([place_a, place_b]))
        if x != "alveolar labiodental":
            return False
    # An affricate can't be followed by a fricative (ch+f, etc)
    elif manner_a == 'affricate' and manner_b == 'fricative':
        return False

    # require something that's MINIMUM_VOCALIC_SONORITY
    # don't allow two nucleuses
    # don't allow voiced unvoiced voiced
    # glides can only exist next to a vowel

    new_syllable = growing_syllable + next
    if len(new_syllable) > 2:
        # Don't allow two interruptions on same side of vowel.
        # Don't allow two nasals either on same side of vowel, either.
        # And don't allow the same sound to be repeated on same side of vowel.
        found_interruption = False
        found_nasal = False
        found_fric = False
        seen = []

        for phoneme in new_syllable:
            if is_vowel(phoneme):
                found_interruption = False
                found_nasal = False
                seen = []
                found_fric = False
            else:
                if phoneme in seen:
                    return False
                seen.append(phoneme)
                if is_interrupted(phoneme):
                    if found_interruption:
                        return False
                elif get_manner(phoneme) == 'fricative':
                    if found_fric:
                        return False
                    else:
                        found_fric = True
                if is_nasal(phoneme):
                    if found_nasal:
                        return False

    return True
            
def _valid_next(pat_item, vowels, consonants, growing_syllable=None):
    if pat_item == 'C':
        collection = consonants
    elif pat_item == 'V':
        collection = vowels
    else:
        collection = [pat_item]
    if not growing_syllable:
        for item in collection:
            yield item
    else:
        for phoneme in collection:
            if can_add_std(growing_syllable, phoneme):
                yield phoneme

def _get_all_valid_remainders(pat, vowels, consonants, growing_syllable):
    # Identify what will be left in the syllable pattern after we process
    # what we're looking at here.
    remainder = pat[1:]
    # For each character that could be fill the current spot in the pattern...
    for prefix in _valid_next(pat[0], vowels, consonants, growing_syllable):
        # If there's more pattern to complete...
        if remainder:
            new_syllable = growing_syllable + prefix if growing_syllable else prefix
            # Recurse to find what could come after
            for suffix in _get_all_valid_remainders(remainder, vowels, consonants, new_syllable):
                # Generate what fits in this spot plus all variations that could come after
                yield prefix + suffix
        else:
            yield prefix

def conceivable_syllables(vowels, consonants, *patterns):
    """
    Returns a set of all syllables that might make sense. Eliminates those
    that are not pronouncable by the human vocal tract or that are vanishingly
    rare.
    """
    for pat in patterns:
        for syllable in _get_all_valid_remainders(pat, vowels, consonants, None):
            yield syllable



