class Syllable:
    def __init__(self, phonemes):
        self.phonemes = phonemes
        
    
    @property
    def coda(self):
        return self._coda
    
    @property
    def nucleus(self):
        return self._nucleus
    
    @property
    def rime(self):
        return self._nucleus + self._coda
    
    @property
    def onset(self):
        return self._onset
    
    def __str__(self):
        return self.phonemes
    