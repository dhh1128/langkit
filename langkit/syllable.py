from .phoneme import *

class Pattern:
    def __init__(self, pat):
        self._pat = pat
        self._n = len(pat)

    def matches(self, syllable, inventory=None):
        if not inventory:
            inventory = ByIPA
        s = str(syllable)
        if len(s) != self._n:
            return False
        for i in range(0, self._n):
            pat_glyph = self._pat[i]
            syl_glyph = s[i]
            if pat_glyph in 'CV':
                syl_phone = inventory.get(syl_glyph)
                if syl_phone is None:
                    return False
                if pat_glyph == 'C':
                    if not syl_phone.is_consonant:
                        return False
                else:
                    if not syl_phone.is_vowel:
                        return False
            else:
                if pat_glyph != syl_glyph:
                    return False
        return True
    
    def __str__(self):
        return self._pat

class Syllable:
    def __init__(self, phonemes):
        self._phonemes = phonemes if isinstance(phonemes, str) \
            else ''.join([str(ph) for ph in phonemes])
        self._nucleus = -1
        self._coda = -1
        self._analyze()

    def _analyze(self):
        sonority = 0
        max_sonority = 0
        peak = -1
        for i in range(len(self._phonemes)):
            ph = self._phonemes[i]
            phoneme = ByIPA.get(ph)
            if not phoneme:
                raise ValueError(f"Unrecognized phone /{ph}/.")
            new_sonority = phoneme.sonority
            # Did we find a nucleus (a vowel)?
            if new_sonority >= 1.0:
                # First vowel?
                if self._nucleus == -1:
                    self._nucleus = i
                # Have we already seen something that wasn't a vowel?
                elif self._coda != -1:
                    raise ValueError("Can't have more than one nucleus.")
            # Are we still in the onset?
            elif self._nucleus == -1:
                pass
            # Else we found beginning of coda
            elif self._coda == -1:
                self._coda = i
            if new_sonority > max_sonority:
                peak = i
                max_sonority = new_sonority
            sonority = new_sonority
        if max_sonority < MINIMUM_VOCALIC_SONORITY:
            raise ValueError(f"No recognizable nucleus in /{self._phonemes}/.")
        elif max_sonority >= GLIDE_SONORITY - 0.01 and max_sonority <= GLIDE_SONORITY + 0.01:
            raise ValueError(f"Glide /{self.nucleus}/ can't be vocalic.")
        elif max_sonority < VOWEL_SONORITY:    
            self._nucleus = peak
            if peak + 1 <= i:
                self._coda = peak + 1
        
    @property
    def coda(self):
        return self._phonemes[self._coda:] if self._coda > -1 else ''
    
    @property
    def nucleus(self):
        return self._phonemes[self._nucleus:] if self._coda == -1 else self._phonemes[self._nucleus:self._coda]
    
    @property
    def rime(self):
        return self._phonemes[self._nucleus:]
    
    @property
    def onset(self):
        return self._phonemes[:self._nucleus]
    
    def __str__(self):
        return self.onset + self.rime
    
    @staticmethod
    def why_not_next(syl_phones, next, allowed_doubles=None):
        """
        Analyzes why next sound can't be added to syl_phones (a list of phonemes already
        in the syllable). Returns either an error string or None, meaning the append is valid.
        
        Different languages have different combining rules. This function simply imposes
        a common set of choices that are likely to be true across many languages,
        eliminating the most common nonsensical combinations of sounds.
        """
        # Always allow append if growing syllable is empty.
        if not syl_phones:
            return None
        
        # Disallow nonsensical repetition.
        prev = syl_phones[-1]
        same = (next == prev)
        if same:
            if (not allowed_doubles) or (next not in allowed_doubles): return f"Can't double /{next}/."
            if len(syl_phones) > 1 and next == syl_phones[-2]: return f"Can't triple /{next}/."

        next_vowel = next.is_vowel
        prev_vowel = prev.is_vowel
        if next_vowel:
            # Disallow double nucleus.
            consonant = False
            for i in range(len(syl_phones) - 1, -1, -1):
                if syl_phones[i].is_consonant:
                    consonant = True
                elif consonant:
                    return f"Already had nucleus /{syl_phones[i]}/; can't use /{next}/ as another nucleus."
            if prev_vowel:
                if vowel_distance(next, prev) < 1.5:
                    return f"/{prev}{next}/ aren't distinct enough to form a dipthong."
        
        # Are we analyzing consecutive consonants?
        elif not prev_vowel:

            if next.place == GLOTTAL:
                return f"Glottals can't follow other consonants."
            
            if prev.ipa == 'ʔ':
                return f"Glottal stop can't be followed by a consonant."
            
            if prev.manner == FLAP:
                return f"Flap can't be followed by a consonant."
            
            if (next.manner == prev.manner) and not same:
                if next.place | prev.place != ALVEOLAR | LABIODENTAL:
                    return "Consecutive consonants with the same manner are unpronounceable except alveolar + labiodental."

            if prev.manner == AFFRICATE and next.manner == FRICATIVE:
                return "An affricate can't be followed by a fricative."

            if prev.is_glide:
                return "Glides must be next to vowels."

            if (next.is_nasal and prev.is_nasal) and not same:
                return "Consecutive nasals are not distinct enough."
            
            # Rule 1: can't have the same phone twice on the same side of a
            # vowel, even if not repeated.
            check_dup = False
            # Rule 2: can't have two consonants that both interrupt, on the same
            # side of a vowel.
            check_interrupted = next.is_interrupted
            # Rule 3: can't change voiced twice on the same side of vowel.
            voiced_transition_count = 0
            voiced = next.is_voiced
            for i in range(len(syl_phones) - 1, -1, -1):
                pre = syl_phones[i]
                if pre.is_vowel:
                    break
                else:
                    # Rule 1
                    if not check_dup:
                        check_dup = True
                    else:
                        if pre == next:
                            return "/{next}/ can't appear twice on the same side of a vowel."
                    # Rule 2`
                    if check_interrupted and pre.is_interrupted:
                        return f"Already interrupted with /{pre}/; can't do it again with /{next}/."
                    # Rule 3
                    if pre.is_voiced != voiced:
                        voiced_transition_count += 1
                        if voiced_transition_count > 1:
                            return f"Can't change voicing of consonants more than once on the same side of a vowel."
                        voiced = pre.is_voiced
