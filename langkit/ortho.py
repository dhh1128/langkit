class Orthography:
    def __init__(self, mappings):
        self._ipa_to_chrs = mappings
        self._chrs_to_ipa = {}
        self._double_ipas = []
        self._double_chrs = []
        for key, value in mappings.items():
            if len(key) > 1:
                if key[0] not in self._double_ipas:
                    self._double_ipas.append(key[0])
            if len(value) > 1:
                if value[0] not in self._double_chrs:
                    self._double_chrs.append(value[0])
            self._chrs_to_ipa[value] = key

    def _transcribe(self, txt, mapping, doubles):
        out = ''
        skip = False
        for i in range(len(txt)):
            if skip:
                skip = False
                continue
            x = txt[i]
            if x in doubles:
                double = txt[i:i+2]
                if double in mapping:
                    x = double
                    skip = True
            out += mapping.get(x, x)
        return out

    def from_ipa(self, ipa):
        return self._transcribe(ipa, self._ipa_to_chrs, self._double_ipas)
    
    def to_ipa(self, txt):
        return self._transcribe(txt, self._chrs_to_ipa, self._double_chrs)
